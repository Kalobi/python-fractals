import itertools
import cmath
import math
import random
import time
import sys
import argparse
import contextlib

from PIL import Image
from colour import Color
import matplotlib.pyplot as plt
import numpy as np


class InvalidOptionsException(Exception):
    pass


def normalize_pixel(pixel, size, xrange, yrange):
    return complex(pixel[0] * (xrange[1] - xrange[0]) / size[0] + xrange[0],
                   -(pixel[1] * (yrange[1] - yrange[0]) / size[1] + yrange[0]))


def complex_to_pixel(c, size, xrange, yrange):
    return (int((c.real - xrange[0]) * size[0] / (xrange[1] - xrange[0])),
            int((-c.imag - yrange[0]) * size[1] / (yrange[1] - yrange[0])))


def height_to_size(height, xrange, yrange):
    return int(height * (xrange[1] - xrange[0]) / (yrange[1] - yrange[0])), height


def color_map(start, end, depth):
    return Color(start).range_to(Color(end), depth)


def iterate_bounded(fun, c, depth, bound, initial=0 + 0j):
    z = initial
    for i in range(depth):
        z = fun(z, c)
        if abs(z) > bound:
            return i + 1
    return 0


def mandelbrot_map(z, c):
    return z ** 2 + c


def get_multibrot_map(d):
    def multibrot_map(z, c):
        return z ** d + c

    return multibrot_map


def burning_ship_map(z, c):
    return (abs(z.real) + 1j * abs(z.imag)) ** 2 + c


def generate_buddhabrot_counters(f, height, xrange, yrange, depth, samples, initial=0 + 0j):
    size = height_to_size(height, xrange, yrange)
    counters = [[0 for y in range(size[1])] for x in range(size[0])]
    for x in range(samples):
        sample = cmath.rect(random.uniform(0, 2), random.uniform(-math.pi, math.pi))
        z = initial
        orbit = []
        for i in range(depth):
            z = f(z, sample)
            orbit.append(z)
            if abs(z) > 2:
                for z in orbit:
                    pixel = complex_to_pixel(z, size, xrange, yrange)
                    if 0 <= pixel[0] < len(counters) and 0 <= pixel[1] < len(counters[0]):
                        counters[pixel[0]][pixel[1]] += 1
                break
    return counters


def grayscale_from_counters(counters, range_adjust=lambda x: x):
    max_count = max(max(column) for column in counters)
    im = Image.new("L", (len(counters), len(counters[0])))
    for pixel in itertools.product(range(len(counters)), range(len(counters[0]))):
        im.putpixel(pixel, int(range_adjust(counters[pixel[0]][pixel[1]] / max_count) * 255))
    return im


def generate_fractal_image(fun, height, xrange, yrange, depth):
    image = Image.new("RGB", height_to_size(height, xrange, yrange), "white")
    for pixel in itertools.product(range(image.width), range(image.height)):
        iterations = iterate_bounded(fun, normalize_pixel(pixel, image.size, xrange, yrange),
                                     depth, 2)
        if not iterations:
            image.putpixel(pixel, (0, 0, 0))
    return image


def decode_function(args):
    fun_specifier = args.fractal
    if fun_specifier == "mandelbrot":
        return mandelbrot_map
    elif fun_specifier == "multibrot":
        return get_multibrot_map(args.fo[0] if args.fo else 4)
    elif fun_specifier == "burning_ship":
        return burning_ship_map
    else:
        raise InvalidOptionsException("Invalid fractal generator")


def parsed_gen_fractal(args):
    fun = decode_function(args)
    image = generate_fractal_image(fun, args.height, args.real_range, args.imag_range,
                                   args.depth)
    with args.output as f:
        image.save(f)


def parsed_buddha(args):
    fun = decode_function(args)
    counters = generate_buddhabrot_counters(fun, args.height, args.real_range,
                                            args.imag_range, args.depth, args.samples)
    with (args.output if not args.autogen_output
          else open(f"buddha_{args.fractal}{args.height}p_{args.depth}i"
                    + f"_{args.samples}s_{int(time.time())}.txt", "w")) as f:
        f.write(repr(counters))


def parsed_counter_images(args):
    if args.grayscale:
        with args.grayscale as f:
            image = grayscale_from_counters(eval(f.read()))
    else:
        with contextlib.ExitStack() as stack:
            files = [stack.enter_context(f) for f in args.rgb]
            image = Image.merge("RGB", [grayscale_from_counters(eval(i.read())) for i in files])
    with args.output as f:
        image.save(f)


def main():
    # top-level parser
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # subparser for "generate"
    parser_gen_fractal = subparsers.add_parser("generate", aliases=["gen"],
                                               help="generate an image of a Mandelbrot-like set")
    # subparser for "buddhacounters"
    parser_buddhacounters = subparsers.add_parser("buddhacounters", aliases=["counters"],
                                                  help="generate a text file of counters for a "
                                                       + "Buddhabrot-like image")
    generators = [parser_gen_fractal, parser_buddhacounters]
    for g in generators:
        g.add_argument("--height",
                       help="height of the resulting image in pixels",
                       type=int, default=1080)
        g.add_argument("--real-range", "--xrange", "-x",
                       help="ends of the real axis",
                       nargs=2, type=float, default=[-2, 1],
                       metavar=("MIN", "MAX"))
        g.add_argument("--imag-range", "--yrange", "-y", "-i",
                       help="ends of the imaginary axis",
                       nargs=2, type=float, default=[-1, 1],
                       metavar=("MIN", "MAX"))
        g.add_argument("-f", "--fractal", "--function",
                       help="which fractal should be generated",
                       choices=["mandelbrot", "multibrot", "burning_ship"],
                       default="mandelbrot")
        g.add_argument("--fo", "--fractal-options",
                       help="additional options for the fractal generating function",
                       nargs="*", type=int, metavar="OPTION")
        g.add_argument("-d", "--depth",
                       help="iteration depth", type=int,
                       default=50)
    parser_gen_fractal.add_argument("output",
                                    help="location where the output file should be saved",
                                    type=argparse.FileType("wb"))
    parser_buddhacounters.add_argument("samples", help="number of random samples", type=int)
    buddha_out = parser_buddhacounters.add_mutually_exclusive_group(required=True)
    buddha_out.add_argument("--output", "-o",
                            help="location where the output file should be saved",
                            type=argparse.FileType("w"))
    buddha_out.add_argument("--autogen-output", "-a", help="automatically name output file",
                            action="store_true")
    parser_gen_fractal.set_defaults(fun=parsed_gen_fractal)
    parser_buddhacounters.set_defaults(fun=parsed_buddha)

    # parser for counter images
    parser_counter_images = subparsers.add_parser("imagefromcounters", aliases=["image"],
                                                  help="generate an image from a grid of values")
    counters_in = parser_counter_images.add_mutually_exclusive_group(required=True)
    counters_in.add_argument("--grayscale", "-g", help="generate a grayscale image from one grid",
                             type=argparse.FileType("r"))
    counters_in.add_argument("--rgb", help="generate a colored image by "
                                           + "using three grids as rgb channels",
                             type=argparse.FileType("r"), nargs=3)
    parser_counter_images.add_argument("output",
                                       help="location where the output file should be saved",
                                       type=argparse.FileType("wb"))
    parser_counter_images.set_defaults(fun=parsed_counter_images)

    # parse and dispatch
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()
    try:
        args.fun(args)
    except InvalidOptionsException as e:
        parser.error(str(e))


if __name__ == "__main__":
    main()
    # with open("buddha_1080p_20i_10000000s_1548340008.txt") as f:
    #    counters = eval(f.read())
    # values = list(itertools.chain.from_iterable(counters))
    # print(max(values))
    # print(np.percentile(values, 99.9))
    # n, bins, patches = plt.hist(values, 256)
    # print(n)
    # plt.show()
    # files = ["buddha_1080p_20i_10000000s_1548340008.txt",
    #          "buddha_1080p_50i_10000000s_1571132560.txt",
    #          "buddha_1080p_500i_10000000s_1571133152.txt"]
    # counters = []
    # for name in files:
    #    with open(name) as f:
    #        counters.append(eval(f.read()))
    # for i, perm in enumerate(itertools.permutations(counters)):
    #    image = Image.merge("RGB", [grayscale_from_counters(counter) for counter in perm])
    #    image.save(f"nebulabrot{i}.png")
    # for i, counter in enumerate(counters):
    #    grayscale_from_counters(counter,
    #                            lambda x: math.log1p(x) / math.log(2)).save(f"buddha_log_{i}.png")

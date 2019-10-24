import itertools
import cmath
import math
import random
import time
import argparse

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
    return z**2 + c


def get_multibrot_map(d):
    def multibrot_map(z, c):
        return z**d + c
    return multibrot_map


def burning_ship_map(z, c):
    return (abs(z.real) + 1j*abs(z.imag))**2 + c


def generate_buddhabrot_counters(f, height, xrange, yrange, depth, samples, initial=0+0j, log=False):
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
    if log:
        with open(f"buddha_{height}p_{depth}i_{samples}s_{int(time.time())}.txt", "w") as f:
            f.write(repr(counters))
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
        iterations = iterate_bounded(fun, normalize_pixel(pixel, image.size, xrange, yrange), depth, 2)
        if not iterations:
            image.putpixel(pixel, (0, 0, 0))
    return image


def parsed_gen_fractal(args):
    fun_specifier = args.fractal
    if fun_specifier == "mandelbrot":
        fun = mandelbrot_map
    elif fun_specifier == "multibrot":
        fun = get_multibrot_map(args.fo[0])
    elif fun_specifier == "burning_ship":
        fun = burning_ship_map
    else:
        raise Exception("Invalid fractal generator")
    image = generate_fractal_image(fun, args.height, args.real_range, args.imag_range,
                                   args.depth)
    with args.output as f:
        image.save(f)


def main():
    # top-level parser
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # subparser for "generate"
    parser_gen_fractal = subparsers.add_parser("generate", aliases=["gen"])
    parser_gen_fractal.add_argument("--height",
                                    help="height of the resulting image in pixels",
                                    type=int, default=1080)
    parser_gen_fractal.add_argument("--real-range", "--xrange", "-x",
                                    help="ends of the real axis",
                                    nargs=2, type=float, default=[-2, 1])
    parser_gen_fractal.add_argument("--imag-range", "--yrange", "-y", "-i",
                                    help="ends of the imaginary axis",
                                    nargs=2, type=float, default=[-1, 1])
    parser_gen_fractal.add_argument("-f", "--fractal", "--function",
                                    help="which fractal should be generated",
                                    choices=["mandelbrot", "multibrot", "burning_ship"],
                                    default="mandelbrot")
    parser_gen_fractal.add_argument("--fo", "--fractal-options",
                                    help="additional options for the fractal generating function",
                                    nargs="*", type=int)
    parser_gen_fractal.add_argument("-d", "--depth",
                                    help="iteration depth", type=int,
                                    default=50)
    parser_gen_fractal.add_argument("output",
                                    help="location where the image should be saved",
                                    type=argparse.FileType("wb"))
    parser_gen_fractal.set_defaults(fun=parsed_gen_fractal)

    # parse and dispatch
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
    # files = ["buddha_1080p_20i_10000000s_1548340008.txt", "buddha_1080p_50i_10000000s_1571132560.txt", "buddha_1080p_500i_10000000s_1571133152.txt"]
    # counters = []
    # for name in files:
    #    with open(name) as f:
    #        counters.append(eval(f.read()))
    # for i, perm in enumerate(itertools.permutations(counters)):
    #    image = Image.merge("RGB", [grayscale_from_counters(counter) for counter in perm])
    #    image.save(f"nebulabrot{i}.png")
    # for i, counter in enumerate(counters):
    #    grayscale_from_counters(counter, lambda x: math.log1p(x) / math.log(2)).save(f"buddha_log_{i}.png")

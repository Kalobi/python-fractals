import itertools
import cmath
import math
import random
import time

from PIL import Image
from colour import Color


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


def iterate_bounded(f, c, depth, bound, initial=0 + 0j):
    z = initial
    for i in range(depth):
        z = f(z, c)
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


def generate_fractal_image(f, height, xrange, yrange, depth):
    image = Image.new("RGB", height_to_size(height, xrange, yrange), "white")
    for pixel in itertools.product(range(image.width), range(image.height)):
        iterations = iterate_bounded(f, normalize_pixel(pixel, image.size, xrange, yrange), depth, 2)
        if not iterations:
            image.putpixel(pixel, (0, 0, 0))
    return image


if __name__ == "__main__":
    files = ["buddha_1080p_20i_10000000s_1548340008.txt", "buddha_1080p_50i_10000000s_1571132560.txt", "buddha_1080p_500i_10000000s_1571133152.txt"]
    counters = []
    for name in files:
        with open(name) as f:
            counters.append(eval(f.read()))
    # for i, perm in enumerate(itertools.permutations(counters)):
    #    image = Image.merge("RGB", [grayscale_from_counters(counter) for counter in perm])
    #    image.save(f"nebulabrot{i}.png")
    for i, counter in enumerate(counters):
        grayscale_from_counters(counter, lambda x: math.log1p(x) / math.log(2)).save(f"buddha_log_{i}.png")

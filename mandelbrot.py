import itertools
import cmath
import math
import random

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


def iterate_bounded(f, c, iterations, bound, initial=0+0j):
    z = initial
    for i in range(iterations):
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


def generate_buddhabrot_counters(f, height, xrange, yrange, depth, samples):
    size = height_to_size(height, xrange, yrange)
    counters = [[0 for x in range(size[0])] for y in range(size[1])]
    for x in range(samples):
        sample = cmath.rect(random.uniform(0, 2), random.uniform(-math.pi, math.pi))



def generate_fractal_image(f, height, xrange, yrange, depth):
    image = Image.new("RGB", height_to_size(height, xrange, yrange), "white")
    for pixel in itertools.product(range(image.width), range(image.height)):
        iterations = iterate_bounded(f, normalize_pixel(pixel, image.size, xrange, yrange), depth, 2)
        if not iterations:
            image.putpixel(pixel, (0, 0, 0))
    return image


if __name__ == "__main__":
    p = (300, 42)
    c = normalize_pixel(p, (800, 600), (-2, 1), (-1, 1))
    print(c)
    p = complex_to_pixel(c, (800, 600), (-2, 1), (-1, 1))
    print(p)

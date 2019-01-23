from PIL import Image
from colour import Color


def normalize_pixel(pixel, size, xrange, yrange):
    return complex(pixel[0] * (xrange[1] - xrange[0]) / size[0] + xrange[0],
                   pixel[1] * (yrange[1] - yrange[0]) / size[1] + yrange[0])


def color_map(start, end, depth):
    return Color(start).range_to(Color(end), depth)


def mandelbrot(c, iterations, maximum):
    z = 0 + 0j
    for i in range(iterations):
        z = z**2 + c
        if abs(z) > maximum:
            return i + 1
    return 0


im = Image.new("RGB", (3000, 2000))
depth = 500
mapping = color_map("blue", "green", depth)
mapping = [tuple(int(v*256) for v in color.rgb) for color in mapping]
mapping.insert(0, (0, 0, 0))
for x in range(im.width):
    for y in range(im.height):
        iterations = mandelbrot(normalize_pixel((x, y), im.size, (-2, 1), (-1, 1)), depth, 2)
        im.putpixel((x, y), mapping[iterations])

im.save("result_color.png")

from PIL import Image


def normalize_pixel(pixel, size, xrange, yrange):
    return complex(pixel[0] * (xrange[1] - xrange[0]) / size[0] + xrange[0],
                   pixel[1] * (yrange[1] - yrange[0]) / size[1] + yrange[0])


def mandelbrot(c, iterations, maximum):
    z = 0 + 0j
    for i in range(iterations):
        z = z**2 + c
        if abs(z) > maximum:
            return i + 1
    return 0


im = Image.new("RGB", (900, 600), "white")
for x in range(im.width):
    for y in range(im.height):
        if not mandelbrot(normalize_pixel((x, y), im.size, (-2, 1), (-1, 1)), 1000, 2):
            im.putpixel((x, y), (0, 0, 0))

im.save("result3.png")

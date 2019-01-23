from PIL import Image


def pixel_to_complex(pixel):
    return complex(pixel[0]/250 - 2, pixel[1]/250 - 1)


def normalize_pixel(pixel, size, xrange, yrange):
    return complex()


def mandelbrot(c, iterations, max):
    z = 0 + 0j
    for i in range(iterations):
        z = z**2 + c
        if abs(z) > max:
            return i + 1
    return 0


im = Image.new("RGB", (1000, 500), "white")
for x in range(im.width):
    for y in range(im.height):
        if not mandelbrot(pixel_to_complex((x, y)), 1000, 2):
            im.putpixel((x, y), (0, 0, 0))

im.save("result2.png")

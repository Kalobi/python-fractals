from PIL import Image
import itertools


def generate_sierpinski_carpet(iters):
    if iters == 0:
        return Image.new("1", (1, 1), 1)
    im = Image.new("1", (3**iters, 3**iters), 0)
    sub = generate_sierpinski_carpet(iters - 1)
    for coord in itertools.product(range(3), repeat=2):
        if not coord[0] == coord[1] == 1:
            im.paste(sub, (coord[0]*3**(iters - 1), coord[1]*3**(iters - 1)))
    return im


if __name__ == '__main__':
    generate_sierpinski_carpet(9).save("sierpinski_carpet.png")

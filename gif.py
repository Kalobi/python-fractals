import itertools
import operator

from PIL import Image

import mandelbrot


def overlap(rgb_old, weights, cap=float("inf")):
    weights = [[weight / sum(t) for weight in t] for t in weights]
    return tuple(min(cap, int(sum(map(lambda t: t[0]*t[1], zip(rgb_old, w))))) for w in weights)


def overlap_grids_and_flatten(grids, weights=((1, 0, 0), (0, 1, 0), (0, 0, 1))):
    return list(map(lambda rgb: overlap(rgb, weights, 255), zip(*list(map(itertools.chain.from_iterable, grids)))))


def flattened_counters_to_image(counters, size):
    im = Image.new("RGB", (size[1], size[0]))
    im.putdata(counters)
    im = im.transpose(Image.TRANSPOSE)
    return im


def get_triangle_fun(start_value, start_point, mid_value, mid_point, end_point):
    def triangle(x):
        if x <= start_point:
            return start_value
        elif x <= mid_point:
            return (mid_value - start_value) / (mid_point - start_point) * (x - start_point) + start_value
        elif x <= end_point:
            return (start_value - mid_value) / (end_point - mid_point) * (x - mid_point) + mid_value
        else:
            return start_value
    return triangle


def composite(joins, *funs):
    def joint(x):
        return funs[len(list(itertools.takewhile(lambda j: j < x, joins)))](x)
    return joint


def shift_weights(num):
    splits = [i * (num - 1) / 6 + 1 for i in range(7)]
    first = composite((splits[2], splits[4]),
                      get_triangle_fun(0, splits[0] - 1, 1, splits[0], splits[2]),
                      lambda x: 0,
                      get_triangle_fun(0, splits[4], 1, splits[6], splits[6] + 1))
    second = get_triangle_fun(0, splits[0], 1, splits[2], splits[4])
    third = get_triangle_fun(0, splits[2], 1, splits[4], splits[6])
    r_weights = [(first(x), second(x), third(x)) for x in range(1, num + 1)]
    return list(map(lambda t: (t, (t[2], t[0], t[1]), (t[1], t[2], t[0])), r_weights))


if __name__ == "__main__":
    files = ["buddha_mandelbrot600p_20i_1000000s_1589320541.txt",
             "buddha_mandelbrot600p_50i_1000000s_1589320973.txt",
             "buddha_mandelbrot600p_500i_1000000s_1589321054.txt"]
    counters = []
    for name in files:
        with open(name) as f:
            counters.append(eval(f.read()))
    size = (len(counters[0]), len(counters[0][0]))

    counters = [mandelbrot.counters_to_brightnesses(grid) for grid in counters]
    flattened_counters = overlap_grids_and_flatten(counters)
    frame1 = flattened_counters_to_image(flattened_counters, size)
    weights = shift_weights(20)
    frames = [flattened_counters_to_image(list(map(lambda pixel: overlap(pixel, w, 255),
                                                   flattened_counters)), size)
              for w in weights[1:]]
    frame1.save("nebulas_600p_20frames.gif", save_all=True, append_images=frames, duration=50, loop=0)


    # grid1 = [[1, 10, 100], [2, 20, 200]]
    # grid2 = [[5, 25, 50], [3, 30, 150]]
    # grid3 = [[7, 17, 77], [20, 30, 40]]
    # grids = [grid1, grid2, grid3]
    # print(list(overlap_grids_and_flatten(grids, ((1, 1, 1), (0, 1, 0), (0, 0, 1)))))

    with open("flattened_nebula.txt", "r") as f:
        raw_counters = eval(f.read())
    weights = shift_weights(10)
    mixed = map(lambda pixel: overlap(pixel, weights[1], 255), raw_counters)
    im = flattened_counters_to_image(mixed, (1620, 1080))
    im.save("merged_nebula_test.png")

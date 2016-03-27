from colour import *
from cartesian import *
from timeit import *


def test_colour():
    b = colour_create(0, 0, 0, 0)
    for i in range(1, 100000):
        c = colour_create(.5, .5, .5, 0)
        b = colour_add(b, c)


def test_cartesian():
    b = cartesian_create(0, 0, 0)
    for i in range(1, 50000):
        c = cartesian_create(.5, .5, .5)
        b = cartesian_normalise(cartesian_add(b, c))
        d = cartesian_dot(c, b)
        e = cartesian_cross(c, b)
# if __name__ == '__main__':
#     print(repeat("test_colour()",
#                  setup="from __main__ import test_colour", number=50))

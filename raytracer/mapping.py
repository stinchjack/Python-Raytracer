import math
from gmpy2 import *
from raytracer.cartesian import *
from PIL import Image

"""
Basic classes and functions for texture mapping
"""


class Texture:

    def colour(self, uv_tuple):
        return None


class CircularRampTexture(Texture):

    __colour_array__ = []

    def __init__(self, colour_array):
        self.__colour_array__ = colour_array

    def colour(self, uv_tuple):
        u = uv_tuple[0]
        v = uv_tuple[1]
        colour_dist = 1.0 / mpfr(len(self.__colour_array__) - 1)
        dist = sqrt((u - 0.5) * (u - 0.5) + (v - 0.5) * (v - 0.5))

        i = int(dist / colour_dist)
        if i > (len(self.__colour_array__) - 1):
            i = i - 1

        clr1 = self.__colour_array__[i]
        clr2 = self.__colour_array__[i + 1]

        p1 = (dist / colour_dist) - i

        return colour_add(colour_scale(clr1, p1), colour_scale(clr2, 1 - p1))

"""
Class for holding a PIL image as a texture
"""


class PILImageTexture(Texture):

    __image__ = None
    __pixels__ = None

    def __init__(self, filename):
        self.__image__ = Image.open(filename)
        self.__pixels__ = self.__image__.load()

    def colour(self, uv_tuple):

        u = uv_tuple[0]
        v = uv_tuple[1]

        if u > 1:
            u = 1
        if v > 1:
            v = 1
        if u < 0:
            u = 0
        if v < 0:
            v = 0

        x = int(u * self.__image__.width) - 1
        y = int(v * self.__image__.height) - 1

        if x < 0:
            x = 0
        if y < 0:
            y = 0

        clr = self.__pixels__[x, y]

        return ('colour', clr[0] / 255.0, clr[1] / 255.0, clr[2] / 255.0)

"""
Maps an intersection result for a cylinder to a UV pair.

        :return: tuple (u, v)
        :param intersect_result: the intersection result dictionary
"""


def cylinder_map_to_rect(intersect_result):
    p = intersect_result['raw_point']

    x = p[1]

    if x < -1:
        x = -1
    if x > 1:
        x = 1

    a1 = math.degrees(asin(x))
    a1 = a1 + 90
    if (p[3] >= 0):
        a1 = 180 + (180 - a1)

    u = a1 / mpfr(360.0)
    v = (p[2]) + 0.5

    return (u, v)


def sphere_map_to_rect(intersect_result):
    p = intersect_result['raw_point']

    radius = sqrt((p[1] * p[1]) + (p[3] * p[3]))

    if (radius == 0):
        return (0, 0)

    x = p[1] / radius

    if x < -1:
        x = -1
    if x > 1:
        x = 1

    a1 = math.degrees(asin(x))
    a1 = a1 + 90

    if (p[3] >= 0):
        a1 = 180 + (180 - a1)

    u = a1 / mpfr(360.0)
    a2 = math.degrees(asin(p[2]))
    a2 = a2 + 90

    v = a2 / mpfr(180.0)

    return (u, v)


def get_colour_from_mapping(colour_mapping, intersect_result):
    if 'colour' in colour_mapping:
        return colour_mapping

    if 'colour_mapping' not in colour_mapping:
        return None

    xy = colour_mapping[1](intersect_result)
    return colour_mapping[2].colour(xy)

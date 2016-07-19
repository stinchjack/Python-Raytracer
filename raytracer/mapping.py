import math
from gmpy2 import *
from raytracer.cartesian import *
from raytracer.colour import *
from PIL import Image

"""
Basic classes and functions for texture mapping.

Todo:
    * Implement Uv mapping for cones, triangles, squares, discs.
    * Add feature to texture class so it can be rotated, flipped, and tiled
    * Add further patterns e.g. ColorRamp, ColourBands
    * Add more documentation
"""


class Texture:
    """ Base class for all textures s"""

    def colour(self, uv_tuple):
        return None


class CircularRampTexture(Texture):

    __colour_array__ = []
    __colour_dist__ = None

    def __init__(self, colour_array):
        self.__colour_array__ = colour_array
        self.__colour_dist__ = 1.0 / mpfr(len(self.__colour_array__) - 1)
        self.___point707__ = sqrt(.5)

    def colour(self, uv_tuple):

        dist = sqrt((uv_tuple[0] - 0.5) *
                    (uv_tuple[0] - 0.5) +
                    (uv_tuple[1] - 0.5) *
                    (uv_tuple[1] - 0.5)) / self.___point707__

        i = int(math.trunc(dist / self.__colour_dist__))

        if i >= (len(self.__colour_array__) - 1):
            i = i - 1

        if (i == 3):
            import pdb
            pdb.set_trace()
        clr1 = self.__colour_array__[i]
        clr2 = self.__colour_array__[i + 1]

        p1 = (dist / self.__colour_dist__) - i

        return colour_add(colour_scale(clr1, 1 - p1), colour_scale(clr2, p1))


class PILImageTexture(Texture):
    """
    Class for holding a PIL image as a texture
    """
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


def cylinder_map_to_rect(intersect_result):
    """
    Maps an intersection result for a cylinder to a UV pair.

            :return: tuple (u, v)
            :param intersect_result: the intersection result dictionary
    """
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
    """
    Maps an intersection result for a sphere to a UV pair.

            :return: tuple (u, v)
            :param intersect_result: the intersection result dictionary
    """
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

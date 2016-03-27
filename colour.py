"""Functions for dealing with colours.

A colour is stored as a tuple, with the first element being
the string 'colour' as an identifier, and the last three being
red green and blue values. """
import gmpy2
from gmpy2 import *

COLOUR_R = 1
COLOUR_G = 2
COLOUR_B = 3


def colour_create(r, g, b):
    """Creates a colour tuple

    :param  r: The red component of the colour
    :param  g: The green component of the colour
    :param  b: The blue component of the colour

    :return: A tuple: ('colour',r,g,b)
    """
    return ('colour', r, g, b)


def colour_add(c1, c2):
    """Adds two colours together

    :param  c1: A colour tuple
    :param  c2: A colour tuple

    :return: A couple tuple, the result of adding c1 and c2

    """
    return ('colour', c1[1] + c2[1], c1[2] + c2[2], c1[3] + c2[3])


def colour_scale(c1, scale):
    """Multiplies a colour by the given scale

    :param c1: A colour
    :param scale: A scalar value

    :return: c1 scaled by the scale parameter

    """
    return ('colour', c1[1] * scale, c1[2] * scale, c1[3] * scale)


def colour_mul(c1, c2):
    """Multiplies two colour together. One of the colour tuples should have
    scalar values. Useful for calculating relflected colours.

    :param c1: A colour tuple
    :param c2: A colour tuple

    :return: c1 multiplied by c2
    """
    return ('colour', c1[1] * c2[1], c1[2] * c2[2], c1[3] * c2[3])

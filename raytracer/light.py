try:
    from gmpy2 import *
except ImportError:
    from math import *
    from mpfr_dummy import *
from raytracer.cartesian import *
from raytracer.colour import *
from raytracer.transformation import *

"""Functions for dealing with lights

A point light is stored as a tuple, with the first two elements being the
stringd 'light', 'point' as an identifiers, and the last two being a cartesian
point and the colour.

A directional light is defined as an area within a hollow shape that lit.
For a cone, the cone is defined as having a base at x=0, y=0, z=0, having
a height of 1, and a radius of 1 at that height. For a tube (cylinder), it is
defined as having a radius of 1, where Y is between 0 and 1. Therefore a
transformation is necessary for these types of lights to be located elsewhere
and in other proportions in the scene.

A directional light is also stored as a tuple. The tuple elements are two
identifying strings as per point lights, a function to test if a point is
inside the shape, a colour, and a transformation of the shape"""

LIGHT_TYPE = 1
LIGHT_POINT_POINT = 2
LIGHT_POINT_COLOUR = 3

LIGHT_DIRECTION_ISINSIDE_FUNC = 2
LIGHT_CONE_ISINSIDE_FUNC = 2
LIGHT_CONE_COLOUR = 3
LIGHT_CONE_TRANSFORM = 4
LIGHT_TUBE_ISINSIDE_FUNC = 2
LIGHT_TUBE_COLOUR = 3
LIGHT_TUBE_TRANSFORM = 4


def light_point_light_create(point, colour):
    """Creates a point light.

    :param point: A cartesian point (see cartesian module documentation)
    :param colour: A colour (see cartesian module documentation)

    :return: A tuple of light parameters"""
    return ('light', 'point', point, colour)


def light_directional_is_inside(light, point):
    """Tests if a point is inside the area of a directional light. This
    calls the function stored in the directional light tuple for testing
    inside/outside.

    :param light: The directional light
    :param point: A cartesian as a point to test

    :return: Boolean"""

    return light[2](light, point)


def light_cone_is_inside(light, point):
    """Tests if a point is inside a cone. The cone is defined as
    having a base at x=0, y=0, z=0, having a height of 1, and a radius
    of 1 at that height.

     light: The cone light
     point: A cartesian as a point to test

    :return: Boolean"""

    p = light[LIGHT_CONE_TRANSFORM].transform_point(point)
    if p[3] <= 0:
        return False
    r = p[3] * aspect

    point_r2 = (p[1] * p[1]) + (p[2] * p[2])

    return pointr2 < 1.0


def light_conelight_create(colour, transform):
    """Creates a tuple for a cone-shaped light"""

    return ('light', 'cone', light_cone_is_inside, colour, transform)


def light_tubelight_create(colour, transform):
    """Creates a tube/cylinder shaped light

    :param light: The cone light
    :param point: A cartesian as a point to test

    :return: a tuple respresenting a directional light"""

    return ('light', 'tube', light_tube_is_inside, colour, transform)


def light_tube_is_inside(point):
    """Tests if a point is inside a cone. The cylinder is defined as
    having a radius of 1, where Y is between 0 and 1.

    :param point: A cartesian as a point to test

    :return: Boolean"""

    p = light[LIGHT_CONE_TRANSFORM].transform_point(point)
    if p[3] <= 0:
        return False
    point_r2 = (p[VECTOR_X] * p[VECTOR_X]) + (p[VECTOR_Y] * p[VECTOR_Y])

    return pointr2 < 1.0

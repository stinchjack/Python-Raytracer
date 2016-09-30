try:
    from gmpy2 import *
except ImportError:
    from math import *
    from raytracer.mpfr_dummy import *
from raytracer.cartesian import *
from raytracer.colour import *
from raytracer.transformation import *
from raytracer.quadraticshapes import *
import random
import copy
from warnings import *

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
LIGHT_COLOUR = 2
LIGHT_TRANSFORM = 3
LIGHT_CALCINFO_FUNC = 4
LIGHT_DATA = 5

def light_point_create(point, colour):
    return light_point_light_create(point, colour)

def light_point_light_create(point, colour):
    """Creates a point light.

    :param point: A cartesian point (see cartesian module documentation)
    :param colour: A colour (see cartesian module documentation)

    :return: A tuple of light parameters"""
    return (
            'light',
            'point',
            colour,
            None,
            light_point_calcinfo,
            {'point': point}

        )

def light_point_calcinfo (light, intersection_result):
    return {
        'shadow_vectors': \
            [cartesian_sub (
                light[LIGHT_DATA]['point'],
                intersection_result['shifted_point']
                )
            ],
        'is_inside': True,
        'light_direction': cartesian_sub (
                light[LIGHT_DATA]['point'],
                intersection_result['point']
                )
    }


def light_spotlight_create(transform, colour, samples = 10):

    
    return (

            'light',
            'spotlight',
            colour,
            transform,
            light_spotlight_calcinfo,
            {   
                'samples': samples,
                'cylinder': shape_cylinder_create(
                                None,
                                None,
                                transform)
            }
        )


def light_spotlight_calcinfo (light, intersection_result):
    
    shadow_vectors = []

    if light[LIGHT_TRANSFORM] is not None:
        
        lightspace_point = light[LIGHT_TRANSFORM].transform_cartesian(
                intersection_result['point']
            )
    else:
        lightspace_point = intersection_result['point']
    
    is_inside = False
    
    if lightspace_point[2] < 0:
        return {'is_inside': False}
    
    if ((lightspace_point[1] ** 2 + lightspace_point[3] ** 2) <= 1.0):
        is_inside = True
        
    if not is_inside:
        
        # import pdb; pdb. set_trace();
        
        #calculate world spacce point to to test ray
        p_world_space = ('cartesian', 
            intersection_result['point'][1],
            intersection_result['point'][2] - mpfr(0.5),
            intersection_result['point'][3]
            )

        p_cylinder_space = \
            light[LIGHT_DATA]['cylinder'][SHAPE_TRANSFORM].transform_cartesian(
                    p_world_space,
                    False
                )
        
        #work out point on light source to test
        
        p_light_test = \
            cartesian_normalise (
                ('cartesian', 
                0 - p_cylinder_space[1],
                mpfr(-0.5),
                0 - p_cylinder_space[3]
                )
            )

        
        direction_test = \
            cartesian_normalise(
                cartesian_sub (
                    p_light_test,
                    p_cylinder_space
                )
            )

        ray = ('ray',  p_cylinder_space, direction_test)

        cylinder_intersect_result = \
            shape_cylinder_intersect(light[LIGHT_DATA]['cylinder'], ray)
            
        if cylinder_intersect_result is False:
            # import pdb;pdb.set_trace();
            is_inside = False
    
    if not is_inside:
        
        return {'is_inside': False}
    
    shadow_vectors = []
    
    light_direction = ('cartesian', 0, 0, 0)
    
    for sample in range(0, light[LIGHT_DATA]['samples']):
        r = random.uniform(0, 1)
        angle = random.uniform(0, 1) * pi * 2 
        x = sin(angle) * r
        y = cos(angle) * r
        z = 0
        
        if light[LIGHT_TRANSFORM] is not None:
            worldspace_test_point = \
                light[LIGHT_TRANSFORM].inverse_transform(
                    ('cartesian', x, y, z), 
                    True
                )
        else: 
            worldspace_test_point = ('cartesian', x, y, z)
            
        shadow_vector = \
            cartesian_sub (
                worldspace_test_point,
                intersection_result['shifted_point']
            )
            
        light_direction = \
            cartesian_add (
                light_direction,
                shadow_vector
            )
        
        shadow_vectors.append (
            cartesian_sub (
                worldspace_test_point,
                intersection_result['shifted_point']
                )        
            )
        
    
    light_direction = \
        cartesian_scale(
            light_direction,
            1.0 / light[LIGHT_DATA]['samples']
        )
        
        
    return {
        'shadow_vectors': shadow_vectors,
        'is_inside': True,
        'light_direction': light_direction
    }


def light_conical_create(transform, colour, length = None, samples = 10):
    return ('light', 'spotlight', colour,
        transform, light_conical_calcinfo,
        {'samples': samples,
        'length': length}
        )

def light_conical_calcinfo (light, intersection_result):
    
    shadow_vectors = []

    if light[LIGHT_TRANSFORM] is not None:
        
        lightspace_point = light[LIGHT_TRANSFORM].transform_cartesian(
                intersection_result['point']
            )
    else:
        lightspace_point = intersection_result['point']
    
    if lightspace_point[2] <= 0:
        return {'is_inside': False}
    
    
    
    if (light[LIGHT_DATA]['length'] is not None and 
        light[LIGHT_DATA]['length'] > 0 and
        lightspace_point[2] > light[LIGHT_DATA]['length']):
        return {'is_inside': False}
    
        
    r = sqrt (lightspace_point[1]**2 + lightspace_point[3]**2) / \
        lightspace_point[2]
    
    
    if (r > 1.0):
        return {'is_inside': False}
        
    
    x = 0
    y = 0
    z = 0

    if light[LIGHT_TRANSFORM] is not None:
        worldspace_test_point = \
            light[LIGHT_TRANSFORM].inverse_transform(
                ('cartesian', x, y, z), 
                True
            )
    else: 
        worldspace_test_point = ('cartesian', x, y, z)

    shadow_vector = \
        cartesian_sub (
            worldspace_test_point,
            intersection_result['shifted_point']
        )

    light_direction =  shadow_vector
        


        
        
    return {
        'shadow_vectors': [shadow_vector],
        'is_inside': True,
        'light_direction': light_direction
    }




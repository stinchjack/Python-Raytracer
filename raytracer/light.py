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
                'samples': samples
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
    
    # check that point is 'above' cylinder
    if lightspace_point[2] < 0:
        return {'is_inside': False}
    
    # check if point is inside radius of cylinder
    if ((lightspace_point[1] ** 2 + lightspace_point[3] ** 2) <= 1.0):
        is_inside = True
        intensity = mpfr(1.0)
        
    if not is_inside:
        
        #  test if point interesects with the cylinder - if does then the light
        # is in complete shadow. if the light is outside the radius of cylider
        # but is in the outer cone of the light, then the light intensity needs
        # to be calculated

        light_test = cartesian_normalise(lightspace_point)[2]

        # if the test point is at more than 26.57 degrees to y-axis, then the point
        # is not lit

        light_cutoff = mpfr (0.4472135954999579)

        
        # is_inside = (abs(direction_test[2])>=  light_cutoff)
        is_inside = light_test >=  light_cutoff
        if is_inside: 
            intensity =   pow (((light_test - light_cutoff) /
                            (1.0 - light_cutoff)), 3)
        
    
    if not is_inside:
        
        return {'is_inside': False}
    
    shadow_vectors = []
    
    light_direction = ('cartesian', 0, 0, 0)

    if intensity == 1.0:
    
        # generate shadow test vectors
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
    
    else: #if intensity < 1.0

        # import pdb; pdb.set_trace();

        # v. messy to calculate shadow sample rays!
        
        # calclate the point on the 'cylider' rim to use as in calculating
        # direction for 'intersection' with 'disc'
        
        #import pdb; pdb.set_trace();

        
        p_cylinder_test = \
            list(
                cartesian_normalise (
                    ('cartesian', 
                    lightspace_point[1],
                    00,
                    lightspace_point[3])
                ) 
            )
        p_cylinder_test[2]  = 2.0;

        ray = \
            (
                'ray',
                lightspace_point,
                cartesian_sub (lightspace_point, p_cylinder_test)
            )

        disc_t = (0 - ray[RAY_START][2]) / (ray[RAY_VECTOR][2])
        disc_point = ray_calc_pt(ray, disc_t)
        
        if (disc_point[1] == 0 and
            disc_point[2] == 0 and
            disc_point[3] == 0):
            # in this case the only test point available is dead-centre
            if light[LIGHT_TRANSFORM] is not None:
                worldspace_test_point = \
                    light[LIGHT_TRANSFORM].inverse_transform(
                        disc_point, True
                    )
            else: 
                worldspace_test_point = disc_point            


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
        else:
            disc_radius_point = cartesian_normalise(disc_point)
            disc_mid_point = \
                cartesian_scale(
                    cartesian_add (
                    disc_point,
                    disc_radius_point 
                    ),
                    0.5
                )

            sin_b = cartesian_len(disc_mid_point)
            len_b = asin(min(1.0, abs(sin_b)))

            mid_line_half_len = sin ((1.5 * pi) - len_b)
            mid_line_direction = \
                ('cartesian',  0 - disc_mid_point[3] , 0, disc_mid_point[1])

            mid_line_ray = ('ray', disc_mid_point, mid_line_direction)


            for sample in range(0, light[LIGHT_DATA]['samples']):

                mid_line_sample_t = random.uniform (-1, 1)
                use_alt = random.uniform (-1, 1) > 0




                mid_line_point = ray_calc_pt (mid_line_ray, mid_line_sample_t)
                mid_line_point_t = cartesian_len(mid_line_point)
                line_from_ctr_pos = random.uniform (mid_line_point_t, 1.0)

                if use_alt:
                    disc_sample_point = \
                        cartesian_scale (
                            mid_line_point,
                            line_from_ctr_pos
                        )

                else:
                    disc_sample_point = \
                        cartesian_scale (
                            mid_line_point,
                            (line_from_ctr_pos  / mid_line_point_t) 
                        )

                if light[LIGHT_TRANSFORM] is not None:
                    worldspace_test_point = \
                        light[LIGHT_TRANSFORM].inverse_transform(
                            disc_sample_point, True
                        )
                else: 
                    worldspace_test_point = disc_sample_point            


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
        'intensity': intensity, 
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




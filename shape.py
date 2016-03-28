from cartesian import *
from colour import *
from matrix import *
from transformation import *

SHAPE_SHAPE = 1
SHAPE_DIFFUSECOLOUR = 2
SHAPE_SPECULARCOLOUR = 3
SHAPE_INTERSECT_FUNC = 4
SHAPE_INSIDE_FUNC = 5
SHAPE_DIFFUSECOLOUR_FUNC = 6
SHAPE_SPECULARCOLOUR_FUNC = 7
SHAPE_TRANSFORM = 8
SHAPE_DATA = 9

"""Functions for dealing with shapes. A shape is a list with the following
elements:

* the string 'shape'
* a string identifying the type of shape, e.g., 'disc'
* a colour tuple to use for the diffuse colour of the shape, where no function
  is used to calculate diffuse colour otherwise
* a colour tuple to use for the specular colour of the shape, where no function
  is used to calculate diffuse colour otherwise
* a function to test the intersection of a ray with the shape
* a function to test if a point is inside the shape
* a function for getting the diffuse colour at a particluar intersection
  point on the object
* a function for getting the specular colour at a particluar intersection
  point on the object
* a Transformation for the shape
* a dictionary of other shape data, as needed by particular shapes"""


def shape_set_transform(shape, transform):
    """Sets the transformation for a shape.
    :param shape: a shape
    :param transform: a Transformation object"""
    if isinstance(transform, Transform):
        shape[SHAPE_TRANSFORM] = transform
    elif type(transform) is dict:
        shape[SHAPE_TRANSFORM] = Transform(transform)
    else:
        shape[SHAPE_TRANSFORM] = None


def shape_diffuse_colour(shape, intersect_result):
    if(type(shape[SHAPE_DIFFUSECOLOUR]) is tuple and
            'colour' in shape[SHAPE_DIFFUSECOLOUR]):
        return shape[SHAPE_DIFFUSECOLOUR]
    else:
        return None


def shape_specular_colour(shape, intersect_result):
    if(type(shape[SHAPE_SPECULARCOLOUR]) is tuple and
            'colour' in shape[SHAPE_SPECULARCOLOUR]):
        return shape[SHAPE_SPECULARCOLOUR]
    else:
        return None


def shape_empty_shape():
    """"Returns a list with some starting elements necessary for a shape.
    
    :return: ['shape', None, None, None, None, None, shape_diffuse_colour,
             shape_specular_colour, None, {}]
    """
    return ['shape', None, None, None, None, None, shape_diffuse_colour,
            shape_specular_colour, None, {}]


def shape_point_inside(shape, cartesian):
    if shape[SHAPE_INSIDE_FUNC] is not None:
        return shape[SHAPE_INSIDE_FUNC](cartesian)


def shape_test_intersect(shape, ray):
    """Tests a ray for intersection against a shape.
 
    :param shape: the shape to test against 
    :param ray: the ray to test
    :return :"""
    if shape[SHAPE_TRANSFORM] is not None:
        result = shape[SHAPE_INTERSECT_FUNC](
            shape, shape[SHAPE_TRANSFORM].transform(ray))
    else:
        result = shape[SHAPE_INTERSECT_FUNC](shape, ray)

    return result


def shape_reverse_transform(result):
    shape = result['shape']
    if shape[SHAPE_TRANSFORM] is not None:
        if 'raw_point' in result:
            result['raw_intersect_point'] = result['raw_point']
            # result['point'] = shape[SHAPE_TRANSFORM].inverseTransform
            # (result['raw_point'], True)

        if 'raw_normal' in result:
            if not result['ray'][RAY_ISSHADOW]:
                result['normal'] = cartesian_normalise(
                    shape[SHAPE_TRANSFORM].inverse_transform(
                        result['raw_normal']))

    else:
        if 'raw_normal' in result:
            result['normal'] = result['raw_normal']
        if 'raw_point' in result:
            result['point'] = result['raw_point']

    return result

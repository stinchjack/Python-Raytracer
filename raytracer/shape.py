from raytracer.cartesian import *
from raytracer.colour import *
from raytracer.matrix import *
from raytracer.transformation import *
from raytracer.oct_tree import *

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
* a dictionary of other shape data, as needed by particular shapes
"""

SHAPE_SHAPE = 1
SHAPE_DIFFUSECOLOUR = 2
SHAPE_SPECULARCOLOUR = 3
SHAPE_INTERSECT_FUNC = 4
SHAPE_INSIDE_FUNC = 5
SHAPE_DIFFUSECOLOUR_FUNC = 6
SHAPE_SPECULARCOLOUR_FUNC = 7
SHAPE_TRANSFORM = 8
SHAPE_DATA = 9
SHAPE_BOUNDING_BOX_SHAPESPACE = 10
SHAPE_BOUNDING_BOX_WORLDSPACE = 11
SHAPE_TRANSPARENTCOLOUR = 12
SHAPE_TRANSPARENTCOLOUR_FUNC = 13

def shape_diffuse_colour(intersect_result):
    """Returns the diffuse colour for a shape that is stored in the shape
    tuple.
    :param shape: a shape
    :param intersect_result: a dictionary of intersection results. This
    parameter is not used. """    
    return shape_get_colour(intersect_result, SHAPE_DIFFUSECOLOUR) 

def shape_specular_colour(intersect_result):
    """Returns the specular colour for a shape that is stored in the shape
    tuple.
    :param intersect_result: a dictionary of intersection results"""
    return shape_get_colour(intersect_result, SHAPE_SPECULARCOLOUR)    
    
def shape_transparency_colour(intersect_result):
    """Returns the tranparency effect colour for an intersection result
    :param intersect_result: a dictionary of intersection results. """
    return shape_get_colour(intersect_result, SHAPE_TRANSPARENTCOLOUR)

def shape_get_colour(intersect_result, colour_type):
    
    if type(colour_type) is not int:
        colour_type = colour_type.lower().strip()
        if colour_type == 'diffuse':
            colour_type = SHAPE_DIFFUSECOLOUR
        elif colour_type == 'specular' or \
            'reflect' in colour_type: 
            colour_type = SHAPE_SPECULARCCOLOUR
        elif 'transp' in colour_type:
            colour_type= SHAPE_TRANSPARENTCOLOUR
        else:
            return None

            
    if colour_type == SHAPE_DIFFUSECOLOUR:
        function_index = SHAPE_DIFFUSECOLOUR_FUNC
    elif colour_type == SHAPE_SPECULARCOLOUR:
        function_index = SHAPE_SPECULARCOLOUR_FUNC    
    elif colour_type == SHAPE_TRANSPARENTCOLOUR:
        function_index = SHAPE_TRANSPARENTCOLOUR_FUNC
    else: 
        return None
        
    shape = intersect_result['shape']
    if shape[function_index] is not None:
        tuple = shape[function_index](shape, intersect_result)
    else:
        tuple = shape[colour_type]
    
    if tuple is None:
        return ('colour', 0, 0, 0)
    
    if 'colour' in tuple:
        return tuple
    elif 'colour_mapping' in tuple:
        uv_pair = tuple[1](intersect_result)
        return tuple[2].colour(uv_pair)

    return None

def shape_bounding_box(shape):
    if shape[SHAPE_BOUNDING_BOX_SHAPESPACE] is None:
      return None
  
    if shape[SHAPE_TRANSFORM] is None:
      return shape[SHAPE_BOUNDING_BOX_SHAPESPACE]
  
    if shape[SHAPE_BOUNDING_BOX_WORLDSPACE] is not None:
      return shape[SHAPE_BOUNDING_BOX_WORLDSPACE]
    
    
    # print ("shape[SHAPE_TRANSFORM].__options__")
    # print (shape[SHAPE_TRANSFORM].__options__)
        
    
    transformed_points = []
    for point in shape[SHAPE_BOUNDING_BOX_SHAPESPACE].coordinates:
      ws_point = shape[SHAPE_TRANSFORM].inverse_transform (point, True)
      transformed_points.append(ws_point)
    
      # print ("point %s"%point.__str__());
      # print ("ws-point %s"%ws_point.__str__());
      # print ();
 
    
    min_x = None
    max_x = None
    min_y = None
    max_y = None 
    min_z = None
    max_z = None
    
    for point in transformed_points:
      if min_x is None or point[1] < min_x : min_x = point[1]
      if max_x is None or point[1] > max_x : max_x = point[1]
      if min_y is None or point[2] < min_y : min_y = point[2]
      if max_y is None or point[2] > max_y : max_y = point[2]
      if min_z is None or point[3] < min_z : min_z = point[3]
      if max_z is None or point[3] > max_z : max_z = point[3]
    
    # import pdb; pdb.set_trace();    
    
    shape[SHAPE_BOUNDING_BOX_WORLDSPACE] = BoundingBox (
        min_x, max_x, min_y, max_y, min_z, max_z)
    
    return shape[SHAPE_BOUNDING_BOX_WORLDSPACE]
     
def shape_set_transform(shape, transform):
    """Sets the transformation for a shape.
    :param shape: a shape
    :param transform: a Transformation object
    """

    if isinstance(transform, Transform):
        shape[SHAPE_TRANSFORM] = transform
    elif type(transform) is dict:
        shape[SHAPE_TRANSFORM] = Transform(transform)
    else:
        shape[SHAPE_TRANSFORM] = None

def shape_empty_shape():
    """"Returns a list with some starting elements necessary for a shape.

    :return: ['shape', None, None, None, None, None, shape_diffuse_colour,
             shape_specular_colour, None, {}, None, None]"""

    return ['shape', None, None, None, None, None, None,
            None, None, {}, None, None, None, None]


def shape_point_inside(shape, cartesian):
    if shape[SHAPE_INSIDE_FUNC] is not None:
        return shape[SHAPE_INSIDE_FUNC](cartesian)
    else:
        return False


def shape_test_intersect(shape, ray):
    """Tests a ray for intersection against a shape. This function transforms
    the ray into shape-space before calling the shape's intersection test
    function.

    :param shape: the shape to test against
    :param ray: the ray to test
    :return: a dictionary of intersection results if the ray intersects, else
             False if the ray does not intersect."""

    if shape[SHAPE_TRANSFORM] is not None:
        result = shape[SHAPE_INTERSECT_FUNC](
            shape, shape[SHAPE_TRANSFORM].transform(ray))
    else:
        result = shape[SHAPE_INTERSECT_FUNC](shape, ray)
    
    if type(result) is list:     
        result['ray'] = ray
    return result


def shape_reverse_transform(intersect_result):
    """Transforms the normal from an intersection with a shape into
    scene-space, if there is a Transformation set for the shape

    :param intersect_result: a dictionary of intersection results.
    :return: the dictionary of intersection results, with member
             'normal' added."""

    shape = intersect_result['shape']
    if shape[SHAPE_TRANSFORM] is not None:
        if 'raw_point' in intersect_result:
            intersect_result['raw_intersect_point'] = \
                intersect_result['raw_point']
            # intersect_result['point'] =
            #       shape[SHAPE_TRANSFORM].inverseTransform
            # (intersect_result['raw_point'], True)

        if 'raw_normal' in intersect_result:
            if not intersect_result['ray'][RAY_ISSHADOW]:
                intersect_result['normal'] = cartesian_normalise(
                    shape[SHAPE_TRANSFORM].inverse_transform(
                        intersect_result['raw_normal']))

    else:
        if 'raw_normal' in intersect_result:
            intersect_result['normal'] = intersect_result['raw_normal']
        if 'raw_point' in intersect_result:
            intersect_result['point'] = intersect_result['raw_point']

    return intersect_result

def shape_set_transparency(shape, colour):
    shape[SHAPE_TRANSPARENTCOLOUR] = colour
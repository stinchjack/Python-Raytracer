
from raytracer.cartesian import *
from raytracer.colour import *
from raytracer.matrix import *
from raytracer.transformation import *
from raytracer.shape import *
from raytracer.oct_tree import *

"""Functions for quadratic shapes: spheres, cylinders, cones, capped cylinders,
capped cone
"""


def shape_sphere_intersect(shape, ray):
    """Intersection test function for a sphere. An untranslated sphere is
    located at X=0, Y=0, Z=0, with a radius of 1.

    :param shape: the shape tuple for the sphere
    :param ray: the ray to perform the intersection test with

    :return: False if no intersection, or a dictionary of results when
             there is an intersection.
    """

    a = cartesian_dot(ray[2], ray[2])
    b = mpfr(2) * cartesian_dot(ray[2], ray[1])
    c = cartesian_dot(ray[1], ray[1]) - mpfr(1)

    discriminant = ((b * b) - (mpfr(4) * a * c))
    if(discriminant < 0):
        return False
    sqroot = sqrt(discriminant)

    two_a = mpfr(2) * a


    ts = [((0 - b) + sqroot) / (two_a),
        ((0 - b) - sqroot) / (two_a)]
    
    results = {}
    
    for t in ts:
        if t <= mpfr(0):
            continue
        
        raw_point = ray_calc_pt(ray, t)

        
        results[t] = \
            {'t': t,
            'raw_point': raw_point,
            'raw_normal':
                cartesian_create(
                    raw_point[1], 0, raw_point[3])            
            }

    if len(results) == 0:
        return False

    final_t = sorted(results.keys()).pop(0)
    

    result = results[final_t]
    del(results[final_t])
    result['all_results'] = results
    
    return result


def shape_sphere_create(colour, specular, transform=None):
    """Creates a tuple with the data necessary to render a sphere.

    :param colour: the colour of the sphere.
    :param specular: the reflective colour of the sphere.
    :param transform: the transformation to apply to the sphere.

    :return: a tuple containg data to render a sphere
    """

    shape = shape_empty_shape()
    shape[SHAPE_SHAPE] = 'sphere'
    shape[SHAPE_DIFFUSECOLOUR] = colour
    shape[SHAPE_SPECULARCOLOUR] = specular
    shape[SHAPE_INTERSECT_FUNC] = shape_sphere_intersect
    shape_set_transform(shape, transform)
    
    shape[SHAPE_INSIDE_FUNC] = shape_sphere_is_inside
    shape[SHAPE_BOUNDING_BOX_SHAPESPACE] = BoundingBox (
        -1.0, 1.0, -1.0, 1.0,-1.0, 1.0)
    
    return shape

def shape_sphere_is_inside(shape, shape_space_point):
    p = shape_space_point
    return ((p[1]**2) + (p[2]**2) + (p[3]**2)) <= mpfr(1.0)


def shape_cylinder_intersect(shape, ray):
    """Intersection test function for a cylinder.

    shape: the shape tuple for the cylinder
    ray: the ray to perform the intersection test with

    :return: False if no intersection, or a dictionary of results when
             there is an intersection.
    """

    four = mpfr(4)
    two = mpfr(2)
    zero = mpfr(0)

    # if the ray is parallel to the cylinder, no intersection

    if ray[RAY_VECTOR][3] == zero and ray[RAY_VECTOR][1] == zero:
        return False

    o = cartesian_create(ray[RAY_START][1], 0, ray[RAY_START][3])
    l = cartesian_create(ray[RAY_VECTOR][1], 0, ray[RAY_VECTOR][3])

    o_c = o

    a = cartesian_dot(l, l)
    b = two * cartesian_dot(l, o_c)
    c = cartesian_dot(o_c, o_c) - mpfr(1)

    discriminant = ((b * b) - (four * a * c))

    if(discriminant < zero):
        return False
    sqroot = sqrt(discriminant)

    two_a = two * a
    ts = [((zero - b) + sqroot) / (two_a),
        ((zero - b) - sqroot) / (two_a)]
    
    results = {}
    
    for t in ts:
        if t <= zero:
            continue
        
        raw_point = ray_calc_pt(ray, t)

        if (raw_point[2] > mpfr(0.5) or
            raw_point[2] < mpfr(-0.5)):    
            continue
        
        results[t] = \
            {'t': t,
            'raw_point': raw_point,
            'raw_normal':
                cartesian_create(
                    raw_point[1], 0, raw_point[3])            
            }
        

            
    if len(results) == 0:
        return False

    final_t = sorted(results.keys()).pop(0)
    

    result = results[final_t]
    del(results[final_t])
    result['all_results'] = results
    
    return result

def shape_cylinder_is_inside(shape, shape_space_point):
    p = shape_space_point
    return ((p[1]**2) + (p[3]**2)) <= mpfr(1.0)


def shape_cylinder_create(colour, specular, transform=None):
    """Creates a cylinder tuple.

    :param colour: the colour of the cylinder.
    :param specular: the reflective colour of the cylinder.
    :param transform: the transformation to apply to the cylinder
    """

    shape = shape_empty_shape()
    shape[SHAPE_SHAPE] = 'cylinder'
    shape[SHAPE_DIFFUSECOLOUR] = colour
    shape[SHAPE_SPECULARCOLOUR] = specular
    shape[SHAPE_INTERSECT_FUNC] = shape_cylinder_intersect
    shape_set_transform(shape, transform)
    shape[SHAPE_BOUNDING_BOX_SHAPESPACE] = BoundingBox (
        -1.0, 1.0, -1.0, 1.0,-1.0, 1.0)
    shape[SHAPE_INSIDE_FUNC] = shape_cylinder_is_inside
    
    return shape




def shape_capped_cylinder_diffuse_colour(shape, intersect_result):
    """Returns the diffuse colour at the intersection point with a capped
    cylinder.

    :param shape: the capped cylinder
    :param intersect_result: the intersection results

    :return: a colour tuple
    """

    # print("intersectResult %s"%intersectResult)
    default = False
    if 'shape_part' not in intersect_result:
        return shape[SHAPE_DIFFUSECOLOUR]
    if(intersect_result['shape_part'] == 'topcap_result' and
       shape[SHAPE_DATA]['topcap'] is not None and
       'diffuse_colour' in shape[SHAPE_DATA]['topcap']):
        return shape[SHAPE_DATA]['topcap']['diffuse_colour']
    elif(intersect_result['shape_part'] == 'bottomcap_result' and
         shape[SHAPE_DATA]['bottomcap'] is not None and
         'diffuse_colour' in shape[SHAPE_DATA]['bottomcap']):
        return shape[SHAPE_DATA]['bottomcap']['diffuse_colour']
    else:
        return shape[SHAPE_DIFFUSECOLOUR]


def shape_capped_cylinder_specular_colour(shape, intersect_result):
    """Returns the specular colour at the intersection point with a capped
    cylinder.

    :param shape: the capped cylinder
    :param intersect_result: the intersection results

    :return: a colour tuple
    """

    if 'shape_part' not in intersect_result:
        return shape[SHAPE_SPECULARCOLOUR]
    if(intersect_result['shape_part'] == 'topcap_result' and
       shape[SHAPE_DATA]['topcap'] is not None and
       'specular_colour' in shape[SHAPE_DATA]['topcap']):
        return shape[SHAPE_DATA]['topcap']['specular_colour']
    elif(intersect_result['shape_part'] == 'bottomcap_result' and
         shape[SHAPE_DATA]['bottomcap'] is not None and
         'specular_colour' in shape[SHAPE_DATA]['bottomcap']):
        return shape[SHAPE_DATA]['bottomcap']['specular_colour']
    else:
        return shape[SHAPE_SPECULARCOLOUR]


def shape_capped_cylinder_intersect(shape, ray):
    """Intersection test function for a capped cylinder.

    :param shape: the shape tuple for the capped cylinder
    :param ray: the ray to perform the intersection test with

    :return: False if no intersection, or a dictionary of results when
             there is an intersection.s

    To do: implement optionality for caps
    """

    if ray[RAY_VECTOR][2] == 0:
        topcap_result = False
        bottomcap_result = False
    else:

        # Test for an intersection with the 'top' cap of the cylinder
        d = ray[RAY_VECTOR]
        topcap_t = (mpfr(-0.5) + (0 - ray[RAY_START][2])) / d[2]
        if topcap_t > 0:
            topcap_result = {'raw_normal': cartesian_create(
                0, -1, 0), 'shape': shape, 't': topcap_t}

            topcap_result['point'] = ray_calc_pt(ray, topcap_t)
            d = ((topcap_result['point'][1] * topcap_result['point'][1]) +
                 (topcap_result['point'][3] * topcap_result['point'][3]))
            if d > mpfr(1):
                topcap_result = False
        else:
            topcap_result = False

        # Test for an intersection with the 'bottom' cap of the cylinder
        d = ray[RAY_VECTOR]
        bottomcap_t = (mpfr(0.5) + (0 - ray[RAY_START][2])) / d[2]
        if bottomcap_t > 0:
            bottomcap_result = {'raw_normal': cartesian_create(0, 1, 0),
                                'shape': shape, 't': bottomcap_t}

            bottomcap_result['point'] = ray_calc_pt(ray, bottomcap_t)
            d = ((bottomcap_result['point'][1] *
                  bottomcap_result['point'][1]) +
                 (bottomcap_result['point'][3] *
                  bottomcap_result['point'][3]))
            if d > mpfr(1):
                bottomcap_result = False
        else:
            bottomcap_result = False

    # Get results for the cylinder and both caps into a dictionary
    results = {'cyl_result': shape_cylinder_intersect(shape, ray),
               'topcap_result': topcap_result,
               'bottomcap_result': bottomcap_result,
               }

    # Determine the result, being lowest value for t, or False if there
    # are no intersections
    final_result = False
    for key in results:
        result = results[key]
        if result is not False:
            if final_result is not False:
                if result['t'] < final_result['t']:
                    final_result = result
                    final_result['shape_part'] = key
            else:
                final_result = result
                final_result['shape_part'] = key

    return final_result


def shape_capped_cylinder_create(colour, specular, topcap={}, bottomcap={},
                                 transform=None):
    """Creates a capped cylinder tuple.

    :param colour: the colour of the cylinder
    :param specular: the reflective colour of the cylinder
    :param topcap: a dictionary with the following two optional members
                   'diffuse_colour': the diffuse colour for the 'top' cap
                   of the cylinder
                   'specular_colour': the specular colour for the 'top' cap
                   of the cylinder
    :param bottomcap: a dictionary with the following two optional members
                      'diffuse_colour': the diffuse colour for the 'bottom'
                      cap of the cylinder
                      'specular_colour': the specular colour for the 'bottom'
                      cap of the cylinder
    :param transform: the transformation to apply to the cylinder
    :return: a tuple with data for rendering a capped cylinder
    """

    shape = shape_empty_shape()
    shape[SHAPE_SHAPE] = 'capped_cylinder'
    shape[SHAPE_DIFFUSECOLOUR] = colour
    shape[SHAPE_SPECULARCOLOUR] = specular
    shape[SHAPE_INTERSECT_FUNC] = shape_capped_cylinder_intersect
    shape[SHAPE_DATA] = {'topcap': topcap, 'bottomcap': bottomcap}
    shape[SHAPE_DIFFUSECOLOUR_FUNC] = shape_capped_cylinder_diffuse_colour
    shape[SHAPE_SPECULARCOLOUR_FUNC] = shape_capped_cylinder_specular_colour
    shape_set_transform(shape, transform)
    shape[SHAPE_BOUNDING_BOX_SHAPESPACE] = BoundingBox (
        -1.0, 1.0, -1.0, 1.0,-1.0, 1.0)
    return shape


def shape_cone_test_point(shape, point):
    """Tests if a point transformed into cone-space is inside the Y-dimensions
    of the cone.

    :param shape: the cone to test against
    :param point: the point to test

    :return: Boolean
    """




def shape_cone_intersect(shape, ray):
    """Intersection test function for a cone.

    :param shape: the shape tuple for the capped cylinder
    :param ray: the ray to perform the intersection test with

    :return: False if no intersection, or a dictionary of results when
             there is an intersection.

    .. todo: Needs thourough checking for all cases.
    """

    zero = mpfr(0)

    # if the ray is parallel to the cone and y_top is more than 0, no
    # intersection
    if (shape[SHAPE_DATA]['y_top'] > zero and
            ray[RAY_VECTOR][3] == zero and ray[RAY_VECTOR][1] == zero):
        return False

    # print(ray)
    one = mpfr(1)
    four = mpfr(4)
    two = mpfr(2)

    o = ray[RAY_START]
    d = ray[RAY_VECTOR]

    # if shape[SHAPE_DATA]['y_top'] > zero:
    # d = cartesian_add(d, cartesian_create(\
    # 0,shape[SHAPE_DATA]['y_top'] ,0))
    # a =(d.x*d.x)+(d.z*d.z)-(d.y*d.y)
    # b =(2.0*(d.x*o.x)) +(2.0*(o.z*d.z)) -(2.0*(d.y*o.y))
    # c =(o.x*o.x)+(o.z*o.z)-(o.y*o.y)

    a = (d[1] * d[1]) + (d[3] * d[3]) - (d[2] * d[2])
    b = ((2.0 * (d[1] * o[1])) +
         (2.0 * (o[3] * d[3])) - (2.0 * (d[2] * o[2])))
    c = (o[1] * o[1]) + (o[3] * o[3]) - (o[2] * o[2])

    discriminant = ((b * b) - (four * a * c))

    if(discriminant < zero):
        return False
    sqroot = sqrt(discriminant)

    if a == 0:
        return False
    two_a = two * a
    t_vals = {'t1': ((zero - b) + sqroot) / (two_a),
              't2': ((zero - b) - sqroot) / (two_a)}

    results = {}
    
    for t_key in t_vals:
        t = t_vals[t_key] 
        if t > 0:
            raw_point = ray_calc_pt(ray, t)
            if raw_point[2] <= (shape[SHAPE_DATA]['y_bottom']) and \
                raw_point[2] >= (shape[SHAPE_DATA]['y_top']):

                results[t] = \
                    {'t': t - .0001,
                    'raw_point': raw_point,
                    'raw_normal':
                        cartesian_create(
                            raw_point[1], 0, raw_point[3])            
                    }

    if len(results)==0:
        return False
    final_t = sorted(results.keys()).pop(0)
    result = results[final_t]
    del(results[final_t])
    result['all_results'] = results 

    return result

def shape_cone_is_inside(shape, shape_space_point):
    p = shape_space_point
 
    if p[2] >= shape[SHAPE_DATA]['y_bottom'] or \
        p[2] <= shape[SHAPE_DATA]['y_top']:        
        return False
    
    p = ('cartesian', p[1], 0, p[3])
    p = cartesian_normalise(p)    
        
    
    return ((p[1]**2) + (p[3]**2)) <= mpfr(1.0)

def shape_cone_create(colour, specular, y_top=0, y_bottom=1,
                      transform=None):
    """Creates a tuple with the necessary data for rendering a cone.  An
    untransformed cone is in parallel to the Y axis, having a radius
    equal to the Y position. The apex of the untransformed cone is at X=0,
    Y=0, Z=0. Optionally, the minumum and maximum values of Y for the rendered
    cone can be specified.

    :param colour: the colour of the cylinder.
    :param specular: the reflective colour of the cylinder.

    :param y_top: The minimum Y value in an untransformed cone. If this
                  parameter is None, the default of 0 will be used.
    :param y_bottom: The maximum Y value in an untransformed cone. If
                     this parameter is None, the default of 1 will be used.
    :param transform: the transformation to apply to the cylinder.

    :return: a tuple with the data needed to render a cone.
    """

    shape = shape_empty_shape()
    shape[SHAPE_SHAPE] = 'cone'
    shape[SHAPE_DIFFUSECOLOUR] = colour
    shape[SHAPE_SPECULARCOLOUR] = specular
    shape[SHAPE_DATA] = {}
    

    shape[SHAPE_DATA]['y_top'] = y_top
    shape[SHAPE_DATA]['y_bottom'] = y_bottom

    
    if shape[SHAPE_DATA]['y_top'] > shape[SHAPE_DATA]['y_bottom']:
        j = shape[SHAPE_DATA]['y_bottom']
        shape[SHAPE_DATA]['y_bottom'] = shape[SHAPE_DATA]['y_top']
        shape[SHAPE_DATA]['y_top'] = j
    
    shape[SHAPE_DATA]['y_height'] = y_bottom - y_top
        
    shape[SHAPE_INTERSECT_FUNC] = shape_cone_intersect
    shape[SHAPE_INSIDE_FUNC] = shape_cone_is_inside
    shape_set_transform(shape, transform)
    
    shape[SHAPE_BOUNDING_BOX_SHAPESPACE] = BoundingBox (
        -1.0, y_top, -1.0, 1.0, y_bottom, 1.0)
    return shape


def shape_cone_ytop(shape):
    """Returns the minimum Y value in an untransformed cone.

    :param shape: the cone to query
    :return: the minimum Y value in an untransformed coneempty_shape
    """
    return shape[SHAPE_DATA]['y_top']


def shape_cone_ybottom(shape):
    """Returns the maximum Y value in an untransformed cone.

    :param shape: the cone to query
    :return: the maximum Y value in an untransformed cone
    """
    return shape[SHAPE_DATA]['y_bottom']


def shape_capped_cone_diffuse_colour(shape, intersect_result):
    """Returns the diffuse colour for an intersection point with a capped
    cone. This function is needed because different colours can be specified
    for cylinder body and both caps.

    :param shape: the cone to query
    :param intersect_result: a dictionary of intersection results

    :return: the diffuse colour for the specified intersection
    """
    if 'shape_part' not in intersect_result:
        return shape[SHAPE_DIFFUSECOLOUR]
    if intersect_result['shape_part'] == 'topcap_result':
        if shape[SHAPE_DATA]['topcap'] is not None:
            if 'diffuse_colour' in shape[SHAPE_DATA]['topcap']:
                return shape[SHAPE_DATA]['topcap']['diffuse_colour']
    elif intersect_result['shape_part'] == 'bottomcap_result':
        if shape[SHAPE_DATA]['bottomcap'] is not None:
            if 'diffuse_colour' in shape[SHAPE_DATA]['bottomcap']:
                return shape[SHAPE_DATA]['bottomcap']['diffuse_colour']
    else:
        return shape[SHAPE_DIFFUSECOLOUR]


def shape_capped_cone_specular_colour(shape, intersect_result):
    """Returns the specular colour for an intersection point with a capped
    cone. This function is needed because specular colours can be specified
    for cylinder body and both caps.

    :param shape: the cone to query
    :param intersect_result: a dictionary of intersection results

    :return: a colour
    """

    if 'shape_part' not in intersect_result:
        return shape[SHAPE_SPECULARCOLOUR]
    if intersect_result['shape_part'] == 'topcap_result':
        if shape[SHAPE_DATA]['topcap'] is not None:
            if 'specular_colour' in shape[SHAPE_DATA]['topcap']:
                return shape[SHAPE_DATA]['topcap']['specular_colour']
    elif intersect_result['shape_part'] == 'bottomcap_result':
        if shape[SHAPE_DATA]['bottomcap'] is not None:
            if 'specular_colour' in shape[SHAPE_DATA]['bottomcap']:
                return shape[SHAPE_DATA]['bottomcap']['specular_colour']
    else:
        return shape[SHAPE_SPECULARCOLOUR]


def shape_capped_cone_intersect(shape, ray):
    """Intersection test function for a capped cone.

    :param shape: the shape tuple for the capped cylinder
    :param ray: the ray to perform the intersection test with

    :return: False if no intersection, or a dictionary of results when
             there is an intersection.

    To do: Implement optionality for cap intersection test. Thourough checking
           for all instances needed.
    """

    zero = mpfr(0)
    ytop = shape[SHAPE_DATA]['y_top']
    do_top_cap = (ytop > zero)
    if ray[RAY_VECTOR][2] == zero:
        topcap_result = False
        bottomcap_result = False
    else:
        d = ray[RAY_VECTOR]

        ytop_r2 = (ytop * ytop)
        ybottom = shape[SHAPE_DATA]['y_ybottom']
        ybottom_r2 = (ybottom * ybottom)

        if do_top_cap:
            topcap_t = (ytop + (zero - ray[RAY_START][2])) / d[2]
        bottomcap_t = (ybottom + (zero - ray[RAY_START][2])) / d[2]
        if do_top_cap and topcap_t > zero:
            topcap_result = {'raw_normal': cartesian_create(
                0, -1, 0), 'shape': shape,  't': topcap_t}

            topcap_result['point'] = ray_calc_pt(ray, topcap_t)
            d = (topcap_result['raw_point'][1] * topcap_result['point'][1]) + \
                (topcap_result['point'][3] * topcap_result['point'][3])
            if d > ytop_r2:
                topcap_result = False
        else:
            topcap_result = False

        d = ray[RAY_VECTOR]
        if bottomcap_t > zero:
            bottomcap_result = {'raw_normal': cartesian_create(
                0, 1, 0), 'shape': shape, 't': bottomcap_t}

            bottomcap_result['point'] = ray_calc_pt(ray, bottomcap_t)
            d = ((bottomcap_result['raw_point'][1] *
                  bottomcap_result['raw_point'][1]) + (
                bottomcap_result['raw_point'][3] *
                bottomcap_result['raw_point'][3]))
            if d > ybottom_r2:
                bottomcap_result = False
        else:
            bottomcap_result = False

    results = {'cyl_result': shape_cone_intersect(shape, ray),
               'bottomcap_result': bottomcap_result}
    if do_top_cap:
        results['topcap_result'] = topcap_result

    final_result = False
    for key in results:
        result = results[key]
        if result is not False:
            if final_result is not False:
                if result['t'] < final_result['t']:
                    final_result = result
                    final_result['shape_part'] = key
            else:
                final_result = result
                final_result['shape_part'] = key

    return final_result


def shape_capped_cone_create(colour, specular, topcap={},
                             bottomcap={}, y_top=None,
                             y_bottom=None, transform=None):
    """Creates a tuple with the necessary data for rendering a capped cone. An
    untransformed cone is in parallel to the Y axis, having a radius
    equal to the Y position. The apex of the untransformed cone is at X=0,
    Y=0, Z=0. Optionally, the minumum and maximum values of Y for the rendered
    cone can be specified.

    :param colour: the colour of the cylinder.
    :param specular: the reflective colour of the cylinder.
    :param topcap: a dictionary with the following two optional members
        'diffuse_colour': the diffuse colour for the 'top' cap of the cylinder
        'specular_colour': the specular colour for the 'top' cap of the
        cylinder
    :param bottomcap: a dictionary with the following two optional members
        'diffuse_colour': the diffuse colour for the 'bottom' cap of the
        cylinder
        'specular_colour': the specular colour for the 'bottom' cap of the
        cylinder
    :param y_top: The minimum Y value in an untransformed cone. If this
        parameter is None, the default of 0 will be used.
    :param y_bottom: The maximum Y value in an untransformed cone. If this
        parameter is None, the default of 1 will be used.
    :param transform: the transformation to apply to the cylinder.

    :return: a tuple with the data needed to render a capped cone.
    """

    shape = hape_cone_create(colour, specular, y_top, y_bottom, transform)
    if type(topcap) is dict:
        shape[SHAPE_DATA]['topcap'] = topcap
    if type(bottomcap) is dict:
        shape[SHAPE_DATA]['bottomcap'] = bottomcap

    shape[SHAPE_INTERSECT_FUNC] = shape_capped_cone_intersect
    
    shape[SHAPE_BOUNDING_BOX_SHAPESPACE] = BoundingBox (
        -1.0, 1.0, -1.0, 1.0,-1.0, 1.0)
    return shape

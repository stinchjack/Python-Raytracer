from raytracer.cartesian import *
from raytracer.colour import *
from raytracer.matrix import *
from raytracer.transformation import *
from raytracer.shape import *
"""Functions for planar shapes: discs, rectangles, polygons, triangles,
and polygon meshes.

..to do: complete docstrings, restest all functions.
"""


def shape_disc_intersect(shape, ray):
    """Intersection test function for a disc. An untranslated disc is
        located at X=0, Y=0, Z=0, sits on the XY plane, and has a radius\
        of 1 in both X and Y.

        :param shape: the shape tuple for the disc
        :param ray: the ray to perform the intersection test with

        :return: False if no intersection, or a dictionary of results when
                there is an intersection.
        """
    if ray[RAY_VECTOR][3] == 0:
        return False
    t = (0 - ray[RAY_START][3]) / (ray[RAY_VECTOR])[3]
    if t < zero():
        return False
    point = ray_calc_pt(ray, t)
    if not(point[1] * point[1]) + (point[2] * point[2]) <= mpfr(1):
        return False

    return {'t': t,
            'raw_point': point,
            'raw_normal': ('cartesian', zero(), zero(), mpfr(-1))
            }


def shape_disc_create(colour, specular, transform=None):
    """Creates a tuple with the data necessary to render a disc.

        :param colour: the colour of the disc.
        :param specular: the reflective colour of the disc.
        :param transform: the transformation to apply to the disc.

        :return: a tuple containg data to render a disc

        """
    shape = shape_empty_shape()
    shape[SHAPE_SHAPE] = 'disc'
    shape[SHAPE_DIFFUSECOLOUR] = colour
    shape[SHAPE_SPECULARCOLOUR] = specular
    shape[SHAPE_INTERSECT_FUNC] = shape_disc_intersect
    shape_set_transform(shape, transform)
    return shape


def shape_rectangle_intersect(shape, ray):
    """Intersection test function for a rectangle.

        :param shape: the shape tuple for the rectangle
        :param ray: the ray to perform the intersection test with

        :return: False if no intersection, or a dictionary of results when
                there is an intersection."""
    if ray[RAY_VECTOR][3] == 0:
        return False
    t = (0 - ray[RAY_START][3]) / ray[RAY_VECTOR][3]
    point = ray_calc_pt(ray, t)
    if(not(point[1] >= shape[SHAPE_DATA]['left'] and
            point[1] <= shape[SHAPE_DATA]['right'] and
            point[2] >= shape[SHAPE_DATA]['top'] and
            point[2] <= shape[SHAPE_DATA]['bottom'])):
        return False
    return {'t': t,
            'raw_point': point,
            'raw_normal': ('cartesian', zero(), zero(), mpfr(-1))
            }


def shape_rectangle_create(colour, specular, bounds, transform=None):
    """Creates a tuple with the data necessary to render a rectangle.
        An untransformed rectangle sits on the XY plane, at Z=0, with the
        minimum and maximum bounds for X and Y set by the bounds parameter.

        :param colour: the colour of the rectangle.
        :param specular: the reflective colour of the rectangle
        :param bounds: a dictionary with the following values
                'top': the minimum Y value of the rectangle
                'bottom': the maximum Y value of the rectangle
                'left': the minimum X value of the rectangle
                'right': the maximum X value of the rectangle
        :param transform: the transformation to apply to the rectangle.

        :returns: a tuple containg data to render a rectangle
        """
    shape = shape_emptyShape()
    shape[SHAPE_DIFFUSECOLOUR] = colour
    shape[SHAPE_SPECULARCOLOUR] = specular
    shape[SHAPE_INTERSECT_FUNC] = shape_rectangle_intersect
    shape_set_transform(shape, transform)

    if('left' not in bounds or 'right' not in bounds or
            'top' not in bounds or 'bottom' not in bounds):
        return None

    if bounds['left'] > bounds['right']:
        x = bounds['right']
        bounds['right'] = bounds['left']
        bounds['left'] = x

    if bounds['top'] > bounds['bottom']:
        x = bounds['top']
        bounds['top'] = bounds['bottom']
        bounds['bottom'] = x

    for key in bounds:
        bounds[key] = mpfr(bounds[key])

    shape[SHAPE_DATA] = bounds
    return shape


def shape_polygon_convert2d(shape, point):
    """Takes a point in 3D space and flattens it without perspective into
        2D space. (The 2D points are used for inside/outside tests).

        :param shape: the polygon related to the point
        :param point: a cartesian point to flatten
        :return: a tuple with a 2D co-oridnate

        """
    for axis2d in shape[SHAPE_DATA]['kept_axes']:

        if shape[SHAPE_DATA]['kept_axes'][axis2d] == 'X':
            d = mpfr(point[1])
        elif shape[SHAPE_DATA]['kept_axes'][axis2d] == 'Y':
            d = mpfr(point[2])
        elif shape[SHAPE_DATA]['kept_axes'][axis2d] == 'Z':
            d = mpfr(point[3])

        if axis2d == 'u':
            u = d
        else:
            v = d
    return(u, v)


def shape_polygon_intersect(shape, ray):
    """Intersection test function for a polygon.

        :param shape: the shape tuple for the rectangle
        :param ray: the ray to perform the intersection test with

        :return: False if no intersection, or a dictionary of results when
                there is an intersection."""
    denom = cartesian_dot(ray[2], shape[SHAPE_DATA]['normal'])
    if denom == 0:
        return False
    elif(denom > 0):
        normal = cartesian_create(0 - shape[SHAPE_DATA]['normal'][1],
                                  0 - shape[SHAPE_DATA]['normal'][2],
                                  0 - shape[SHAPE_DATA]['normal'][3])

    t = cartesian_dot(cartesian_sub(shape[SHAPE_DATA]['centre'], ray[
                      1]), shape[SHAPE_DATA]['normal']) / denom
    if t < 0:
        return False
    result = {'t': t,
              'raw_point': ray_calc_pt(ray, t)
              }

    result['point2d'] = shape_polygon_convert2d(shape, result['raw_point'])

    count = 0
    testSeg = ('lineseg2d', result['point2d'],
               shape[SHAPE_DATA]['outside_point'])

    for outerLineSeg in shape[SHAPE_DATA]['polygon_line_segs']:
        if lineseg2d_intersect(testSeg, outerLineSeg):
            count = count + 1

    if count > 0 and(count % 2) == 1:
        result['raw_normal'] = shape[SHAPE_DATA]['normal']
        return result
    else:
        return False


def shape_polygon_create(data={}):
    """Creates a tuple with the data necessary to render a polygon.

        :param colour: the colour of the polygon.
        :param specular: the reflective colour of the polygon.
        :transform: the transformation to apply to the polygon.

        :return: a tuple containg data to render a polygon
        """
    shape = shape_empty_shape()
    shape[SHAPE_INTERSECT_FUNC] = shape_polygon_intersect

    colours = data['colour']
    points = data['points']
    if len(points) < 3:
        return None
    if 'reflections' in data:
        reflections = data['reflections']
    else:
        reflections = None

    shape[SHAPE_DIFFUSECOLOUR] = colours

    if 'transform' in data and isinstance(transform,  Transform):
        shape_setTransform(shape, data['transform'])

    shape[SHAPE_SPECULARCOLOUR] = reflections

    shape[SHAPE_DATA]['centre'] = cartesian_create(
        mpfr(points[0][1]), mpfr(points[0][3]), mpfr(points[0][3]))
    # Normal is calculated as per triangle

    shape[SHAPE_DATA]['normal'] = cartesian_normalise(cartesian_cross(
        cartesian_sub(points[1], points[0]), cartesian_sub(
            points[2], points[0])))
    # print("self.normal %s"%self.normal.normalise())
    ex = shape[SHAPE_DATA]['normal'][1]
    if ex < 0:
        ex = zero() - ex
    ey = shape[SHAPE_DATA]['normal'][2]
    if ey < 0:
        ey = zero() - ey
    ez = shape[SHAPE_DATA]['normal'][3]
    if ez < 0:
        ez = zero() - ez
    norml = cartesian_create(ex, ey, ez)
    # figure which axis to discard for in/out test
    if norml[1] > norml[2] and norml[1] > norml[3]:
        discard_axis = 'X'
        kept_axes = {'u': 'Y', 'v': 'Z'}
    elif norml[2] > norml[1] and norml[2] > norml[3]:
        discard_axis = 'Y'
        kept_axes = {'u': 'X', 'v': 'Z'}
    elif norml[3] > norml[1] and norml[3] > norml[2]:
        discard_axis = 'Z'
        kept_axes = {'u': 'X', 'v': 'Y'}
    else:
        discard_axis = 'X'
        kept_axes = {'u': 'Y', 'v': 'Z'}
    shape[SHAPE_DATA]['kept_axes'] = kept_axes
    # print("self.kept_axes %s"%self.kept_axes)
    # create a set of point with one axis discarded
    shape[SHAPE_DATA]['points2d'] = []
    # print("points2d:  ")

    for i in range(len(points)):
        p2d = shape_polygon_convert2d(shape, points[i])
        # print(p2d)
        shape[SHAPE_DATA]['points2d'].append(p2d)

    # print("polygon line segments")
    shape[SHAPE_DATA]['polygon_line_segs'] = []
    min_u = None
    min_v = None
    for i in range(len(shape[SHAPE_DATA]['points2d'])):
        p0 = shape[SHAPE_DATA]['points2d'][i]
        if i > 0:
            p1 = shape[SHAPE_DATA]['points2d'][i - 1]
        else:
            p1 = shape[SHAPE_DATA]['points2d'][
                len(shape[SHAPE_DATA]['points2d']) - 1]
        ls = lineseg2d_create(p0, p1)
        shape[SHAPE_DATA]['polygon_line_segs'].append(ls)
        # print(ls)
        if min_u is None or p0[0] < min_u:
            min_u = p0[0]

        if min_v is None or p0[1] < min_v:
            min_v = p0[1]

    shape[SHAPE_DATA]['outside_point'] = (min_u - 1.0, min_v - 1.0)

    return shape


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Code for a triangle
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def shape_triangle_diffuse_colour(shape, intersectResult):
    if not shape[SHAPE_DATA]['colorShade']:
        return shape[SHAPE_DIFFUSECOLOUR]

    di0 = cartesian_len(cartesian_substract(
        intersectResult['point'], shape[SHAPE_DATA]['p0']))
    di1 = cartesian_len(cartesian_substract(
        intersectResult['point'], shape[SHAPE_DATA]['p1']))
    di2 = cartesian_len(cartesian_substract(
        intersectResult['point'], shape[SHAPE_DATA]['p2']))

    cp0 = colour_scale(shape[SHAPE_DATA]['c0'], (mpfr(
        1.0) - (di0 / shape[SHAPE_DATA]['max_l'])))
    cp1 = colour_scale(shape[SHAPE_DATA]['c1'], (mpfr(
        1.0) - (di1 / shape[SHAPE_DATA]['max_l'])))
    cp2 = colour_scale(shape[SHAPE_DATA]['c2'], (mpfr(
        1.0) - (di2 / shape[SHAPE_DATA]['max_l'])))

    return colour_add(colour_add(cp0, cp1), cp2)


def shape_triangle_specular_colour(self, intersectResult):
    if not shape[SHAPE_DATA]['reflectShade']:
        return shape[SHAPE_SPECULARCOLOUR]

    di0 = cartesian_len(cartesian_substract(
        intersectResult['point'], shape[SHAPE_DATA]['p0']))
    di1 = cartesian_len(cartesian_substract(
        intersectResult['point'], shape[SHAPE_DATA]['p1']))
    di2 = cartesian_len(cartesian_substract(
        intersectResult['point'], shape[SHAPE_DATA]['p2']))

    cp0 = colour_scale(shape[SHAPE_DATA]['r0'], (mpfr(
        1.0) - (di0 / shape[SHAPE_DATA]['max_l'])))
    cp1 = colour_scale(shape[SHAPE_DATA]['r1'], (mpfr(
        1.0) - (di1 / shape[SHAPE_DATA]['max_l'])))
    cp2 = colour_scale(shape[SHAPE_DATA]['r2'], (mpfr(
        1.0) - (di2 / shape[SHAPE_DATA]['max_l'])))

    return colour_add(colour_add(cp0, cp1), cp2)


def shape_triangle_intersect(shape, ray):

    # p = ray[2].cross(self.e2)
    p = cartesian_cross(ray[2], shape[SHAPE_DATA]['e2'])

    # det = self.e1.dot(p)
    det = cartesian_dot(shape[SHAPE_DATA]['e1'], p)

    # ray and triangle are parallel if det is close to 0
    if det == zero():
        return False
    # if(det > mpfr("-0.000001") and det < mpfr("0.000001")):
    # return False

    inv_det = 1.0 / det

    # s = ray.point - self.p0
    s = cartesian_sub(ray[1], shape[SHAPE_DATA]['p0'])
    u = inv_det * cartesian_dot(s, p)
    if(u < 0 or u > 1.0):
        return False

    # q = s.cross(self.e1)
    q = cartesian_cross(s, shape[SHAPE_DATA]['e1'])
    # v = inv_det *(ray[2].dot(q))
    v = inv_det * cartesian_dot(ray[2], q)
    if(v < 0 or v > 1.0 or(u + v) > 1.0):
        return False

    # t = inv_det *(self.e2.dot(q))
    t = inv_det * cartesian_dot(shape[SHAPE_DATA]['e2'], q)
    if t < 0:
        return False

    return {
        't': t,
        'raw_normal': shape[SHAPE_DATA]['normal']
    }


def shape_triangle_create(points, colours, reflections=None):
    """Creates a tuple with the data necessary to render a triangle.

        colour: the colour of the triangle.
        specular: the reflective colour of the triangle.
        points: a list or tuple of three cartesians points,
        being the vertices ofthe triangle

        :param colours:
        :param reflections:

        :return: a tuple containg data to render a triangle
        """
    shape = shape_empty_shape()
    shape[SHAPE_SHAPE] = 'triangle'
    shape[SHAPE_INTERSECT_FUNC] = shape_triangle_intersect
    shape[SHAPE_DIFFUSECOLOUR_FUNC] = shape_triangle_diffuse_colour
    shape[SHAPE_SPECULARCOLOUR_FUNC] = shape_triangle_specular_colour

    shape[SHAPE_DATA]['colorShade'] = 'colour' not in colours
    shape[SHAPE_DATA]['reflectShade'] = (reflections is not None and
                                         'colour' not in reflections)

    shape[SHAPE_DIFFUSECOLOUR] = colours
    shape[SHAPE_SPECULARCOLOUR] = reflections

    shape[SHAPE_DATA]['p0'] = points[0]
    shape[SHAPE_DATA]['p1'] = points[1]
    shape[SHAPE_DATA]['p2'] = points[2]

    if shape[SHAPE_DATA]['colorShade']:
        shape[SHAPE_DATA]['c0'] = colours[0]
        shape[SHAPE_DATA]['c1'] = colours[1]
        shape[SHAPE_DATA]['c2'] = colours[2]

    if shape[SHAPE_DATA]['reflectShade']:
        shape[SHAPE_DATA]['r0'] = reflections[0]
        shape[SHAPE_DATA]['r1'] = reflections[1]
        shape[SHAPE_DATA]['r2'] = reflections[2]

    if shape[SHAPE_DATA]['reflectShade']:

        l0 = cartesian_len(cartesian_subs(points[1] - points[0]))
        l1 = cartesian_len(cartesian_subs(points[2] - points[1]))
        l2 = cartesian_len(cartesian_subs(points[0] - points[2]))

        shape[SHAPE_DATA]['max_l'] = l0
        if l1 > shape[SHAPE_DATA]['max_l']:
            shape[SHAPE_DATA]['max_l'] = l1
        if l2 > shape[SHAPE_DATA]['max_l']:
            shape[SHAPE_DATA]['max_l'] = l2

    shape[SHAPE_DATA]['normal'] = cartesian_normalise(cartesian_cross(
        cartesian_sub(points[1], points[0]), cartesian_sub(
            points[2], points[0])))

    shape[SHAPE_DATA]['e1'] = cartesian_sub(points[1], points[0])
    shape[SHAPE_DATA]['e2'] = cartesian_sub(points[2], points[0])
    return shape


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Code for a poly mesh
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def shape_polymesh_diffuseColour(shape, intersectResult):
    # if not 'hit_polygon' in intersectResult:
    # return self.basicColour

    return intersectResult['hit_polygon'][SHAPE_DIFFUSECOLOUR_FUNC](
        intersectResult['hit_polygon'], intersectResult)


def shape_polymesh_specularColour(shape, intersectResult):
    # if not 'hit_polygon' in intersectResult:
    # return self.refelectColour

    return intersectResult['hit_polygon'][SHAPE_SPECULARCOLOUR_FUNC](
        intersectResult['hit_polygon'], intersectResult)


def shape_polymesh_intersect(shape, ray):
    final_result = False

    for t in shape[SHAPE_DATA]['polygons']:
        result = t[SHAPE_INTERSECT_FUNC](t, ray)
        if result is not False:
            if final_result is False or result['t'] < final_result['t']:
                final_result = result
                final_result['hit_polygon'] = t
            # if ray[3]: return final_result

    return final_result


def shape_polymesh_create(data):
    shape = shape_empty_shape()
    shape[SHAPE_INTERSECT_FUNC] = shape_polymesh_intersect
    shape[SHAPE_DIFFUSECOLOUR_FUNC] = shape_polymesh_diffuseColour
    shape[SHAPE_SPECULARCOLOUR_FUNC] = shape_polymesh_specularColour
    if 'colour' in data:
        colour = data['colour']
    else:
        colour = None

    if 'reflection' in data:
        reflection = data['reflection']
    else:
        reflection = None

    if 'transform' in data:
        transform = data['transform']
    else:
        transform = None
    polygons = []
    points = data['points']
    polygon_point_indices = data['polygon_point_indices']

    if 'face_diffuse_colours' in data:
        face_diffuse_colours = data['face_diffuse_colours']
    else:
        face_diffuse_colours = []

    if 'face_specular_colours' in data:
        face_specular_colours = data['face_reflect_colours']
    else:
        face_reflect_colours = None

    do_refl = face_reflect_colours is not None
    if not do_refl:
        tri_refl = None
    face = -1
    for polygon_points in polygon_point_indices:
        face = face + 1

        tri_points = []
        for polygon_point in polygon_points:
            tri_points.append(points[polygon_point])

        tri_colours = None
        if('face_diffuse_colours' in data and
                face_diffuse_colours[face] is not None):
            tri_colours = face_diffuse_colours[face]
        elif colour is not None:
            tri_colours = colour

        if do_refl:
            tri_refl = None
            if('face_specular_colours' in data and
                    face_diffuse_colours[face] is not None):
                tri_colours = face_specular_colours[face]
            elif reflection is not None:
                tri_refl = reflection

        if len(tri_points) == 3:
            polygons.append(shape_triangle_create(tri_points, tri_colours))
        elif len(tri_points) > 3:
            polygons.append(shape_polygon_create(
                {'points': tri_points, 'colour': tri_colours}))
    shape[SHAPE_DATA]['polygons'] = polygons
    return shape


def shape_polymesh_shapes(data, transform=None):
    if 'colour' in data:
        colour = data['colour']
    else:
        colour = None

    if 'reflection' in data:
        reflection = data['reflection']
    else:
        reflection = None

    if 'transform' in data:
        transform = data['transform']
    else:
        transform = None
    polygons = []
    points = data['points']
    polygon_point_indices = data['polygon_point_indices']

    if 'face_diffuse_colours' in data:
        face_diffuse_colours = data['face_diffuse_colours']
    else:
        face_diffuse_colours = []

    if 'face_specular_colours' in data:
        face_specular_colours = data['face_reflect_colours']
    else:
        face_reflect_colours = None

    do_refl = face_reflect_colours is not None
    if not do_refl:
        tri_refl = None
    face = -1
    for polygon_points in polygon_point_indices:
        face = face + 1

        tri_points = []
        for polygon_point in polygon_points:
            tri_points.append(points[polygon_point])

        tri_colours = None
        if('face_diffuse_colours' in data and
                face_diffuse_colours[face] is not None):
            tri_colours = face_diffuse_colours[face]
        elif colour is not None:
            tri_colours = colour

        if do_refl:
            tri_refl = None
            if('face_specular_colours' in data and
                    face_diffuse_colours[face] is not None):
                tri_colours = face_specular_colours[face]
            elif reflection is not None:
                tri_refl = reflection

        if len(tri_points) == 3:
            polygons.append(shape_triangle_create(tri_points, tri_colours))
        elif len(tri_points) > 3:
            polygons.append(shape_polygon_create(
                {'points': tri_points, 'colour': tri_colours}))
    return polygons

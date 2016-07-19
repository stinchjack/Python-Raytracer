from gmpy2 import *
from raytracer.cartesian import *
from raytracer.colour import *
from raytracer.matrix import *
from raytracer.light import *
from raytracer.output import *
from raytracer.shape import *
from raytracer.scene import *
from raytracer.lighting_model import *
import random

"""Functions for dealing with views. A view is simply a perspective on a
scene. Crucially, view_render and view_render_pixel are core raytracer
functions, generating rays to be tested against objects in the scene. Views
should be created using the view_create function.

A view is stored as a list with the following elements:
    * Identifier string
    * An instance of a lighting model
    * The rectangle of the physical output to draw onto. This is a
        dictionary:
        'left': the left-hand edge of the physical output to draw onto
        'right': the right-hand edge of the physical output to draw onto
        'top': the top edge of the physical output to draw onto
        'bottom': the bottom edge of the physical output to draw onto

    * The rectangle of the logical view to draw at where z=0. This is a
        dictionary:
        'left': the left-hand edge
        'right': the right-hand edge
        'top': the top edge
        'bottom': the bottom edge

    * A dictionary of antialiasing setting for the view:
        'on': Boolean value dictating to using anti-alias while rendering
        or not
        'stochastic': Boolean value dictating use of stochastic/random
        anti-aliasing
        'x': How many times to divide the pixel on the horizontal axis
        'y': How many times to divide the pixel on the vertical axis

    * A transformation. If no transformation is required this element
        should be set to None. The transformation allows the view to come from
        anywhere in the scene, from any angle

    * The Z-position of the eye point. This should be a negative value. The X
        and Y co-ordinates of the eye are in the middle of the logical view

    * The Cartesian co-ordinate of the eye, calculated from the Z-position of
        the eye point and rectangle of the logical view

    * A dictionary of data intended for internal use with anitalising:

        'count': The total number of subsamples taken for each pixel, i.e.
            member 'x' times member 'y'
        'colour_scale': The multiplier for each colour subsample to be scaled
            by. This is the inverse of member 'count'
        'x_step': The scene distance to move horizontally for each horizontal
            pixel on the physical output
        'y_step': The scene distance to move vertically for each vertical
            pixel on the physical output
        'a_view_step_x': The horizontal step distance to use for sub sampling
        'a_view_step_y': The vertical step distance to use for sub sampling


    * The current X-position during rendering(intended for internal use)

    * The current Y-position during rendering(intended for internal use)"""

VIEW_LIGHTINGMODEL = 1
VIEW_OUTPUT = 2
VIEW_PHYSICALRECTANGLE = 3
VIEW_VIEWRECTANGLE = 4
VIEW_ANTIALIAS = 5
VIEW_TRANSFORM = 6
VIEW_EYEZ = 7
VIEW_EYE = 8
VIEW_ANTIALIAS_DATA = 9
VIEW_VIEW_X = 10
VIEW_VIEW_Y = 11


def view_create(eye_z,  physical_rectangle, view_rectangle, transform=None):
    """Creates a view.

     eye_z: The Z-position of the eye point. This should be a negative value.

     :param physical_rectangle: The rectangle of the physical output to draw
            onto. This is value is a dictionary:
            'left': the left-hand edge of the physical output to draw onto
            'right': the right-hand edge of the physical output to draw onto
            'top': the top edge of the physical output to draw onto
            'bottom': the bottom edge of the physical output to draw onto

     :param view_rectangle: The rectangle of the logical view to draw at
            where z=0. This is a dictionary:
            'left': the left-hand edge
            'right': the right-hand edge
            'top': the top edge
            'bottom': the bottom edge

    :param transformation: A transformation to apply to the view(optional)

    :return: A list of view parameters, or None on failure"""
    if not type(physical_rectangle) is dict:
        return None
    if not type(view_rectangle) is dict:
        return None
    view_rectangle['top'] = mpfr(view_rectangle['top'])
    view_rectangle['left'] = mpfr(view_rectangle['left'])
    view_rectangle['bottom'] = mpfr(view_rectangle['bottom'])
    view_rectangle['right'] = mpfr(view_rectangle['right'])
    view = ['view', lightingmodel_basic_create(), None,
            physical_rectangle, view_rectangle, {},
            transform, mpfr(eye_z),
            cartesian_create((view_rectangle['left'] +
                              view_rectangle['right']) / mpfr(2.0),
                             (view_rectangle['top'] +
                              view_rectangle['bottom']) /
                             mpfr(2.0), eye_z), {}, None, None]

    view_set_antialias(view)
    return view


def view_set_transform(view, transform):
    """Set or change the transformation for a view.

     :param view: The view to change
     :param transform: The Transformation to apply"""

    if isinstance(transform, Transform):
        view[VIEW_TRANSFORM] = transform
    elif type(transform) is dict:
        view[VIEW_TRANSFORM] = Transform(transform)


def view_set_antialias(
        view, on=False, x=1, y=1, stochastic=False,
        edge_detect=False, ed_threshold=.3):
    """Sets the antialias parameters for a view.

     :param view: The view to change
     :param on: Boolean value dictating to using antialias while rendering
        or not
     :param stochastic: Boolean value dictating use of stochastic/random
        antialiasing
     :param stochastic: Boolean value dictating use edge detection
     :param x: How many times to divide a pixel on the horizontal axis
     :param y: How many times to divide a pixel on the vertical axis"""

    view[VIEW_ANTIALIAS]['on'] = on
    view[VIEW_ANTIALIAS]['x'] = mpfr(x)
    view[VIEW_ANTIALIAS]['y'] = mpfr(y)
    view[VIEW_ANTIALIAS]['stochastic'] = stochastic
    view[VIEW_ANTIALIAS]['edge_detect'] = edge_detect
    view[VIEW_ANTIALIAS]['edge_detect_threshold'] = ed_threshold
    view[VIEW_ANTIALIAS]['count'] = mpfr(x * y)
    if on:
        count = mpfr(x * y)
        view[VIEW_ANTIALIAS_DATA]['count'] = mpfr(view[
            VIEW_ANTIALIAS]['x'] * view[VIEW_ANTIALIAS]['y'])
        view[VIEW_ANTIALIAS_DATA]['colour_scale'] = mpfr(1.0) / mpfr(count)
        view[VIEW_ANTIALIAS_DATA]['x_step'] = \
            (view[VIEW_VIEWRECTANGLE]['right'] -
             view[VIEW_VIEWRECTANGLE]['left']) /\
            (view[VIEW_PHYSICALRECTANGLE]['right'] -
             view[VIEW_PHYSICALRECTANGLE]['left'])
        view[VIEW_ANTIALIAS_DATA]['y_step'] =\
            (mpfr(view[VIEW_VIEWRECTANGLE]['bottom']) -
             view[VIEW_VIEWRECTANGLE]['top']) /\
            (mpfr(view[VIEW_PHYSICALRECTANGLE]['bottom']) -
             mpfr(view[VIEW_PHYSICALRECTANGLE]['top']))
        view[VIEW_ANTIALIAS_DATA]['a_view_step_x'] = \
            view[VIEW_ANTIALIAS_DATA]['x_step'] / \
            mpfr(view[VIEW_ANTIALIAS]['x'])
        view[VIEW_ANTIALIAS_DATA]['a_view_step_y'] = \
            view[VIEW_ANTIALIAS_DATA]['y_step'] / \
            mpfr(view[VIEW_ANTIALIAS]['y'])

        if edge_detect:
            view[VIEW_ANTIALIAS_DATA]['edge_detection_map'] = {}
            view[VIEW_ANTIALIAS_DATA]['antialias_function'] = \
                view_render_pixel_antialias_edge_detect
        elif stochastic:
            view[VIEW_ANTIALIAS_DATA]['antialias_function'] = \
                view_render_pixel_antialias_stochastic
        else:
            view[VIEW_ANTIALIAS_DATA]['antialias_function'] = \
                view_render_pixel_antialias_grid_pattern

    else:
        view[VIEW_ANTIALIAS_DATA]['antialias_function'] = \
            view_render_pixel_no_antialias


def view_set_lighting_model(view, model):
    """Sets the lighting model for a view

     :param view: The view to change
     :param model: Lighting model to use while rendering the scene"""
    view[VIEW_LIGHTINGMODEL] = model


def view_render_pixel(view, scene_obj, physical_x, physical_y, output_type,
                      lighting_model_flags=0):
    """Renders one pixel of a view

     :param view: The view to render
     :param scene_obj: The scene to render
     :param physical_x: The X co-ordinate of the pixel
     :param physical_y: The Y co-ordinate of the pixel
     :param lightingmodel_flags: Flags that affect behaviour of the lighting
                                 model
     """

    clr = view[VIEW_ANTIALIAS_DATA]['antialias_function'](
        view, scene_obj, lighting_model_flags)

    output_type.set_pixel(physical_x, physical_y, clr)
    return clr


def view_render_pixel_no_antialias(view, scene_obj, lighting_model_flags=0):
    """
    Performs the current pixel of a render without antialiasing.

    :param view: The view to render
    :param scene_obj: The scene to render
    :param lightingmodel_flags: Flags that affect behaviour of the lighting
                                model
    :return: a colour tuple
    """
    ray = ray_create(view[VIEW_EYE],
                     cartesian_create(
        view[VIEW_VIEW_X] - view[VIEW_EYE][1],
        view[VIEW_VIEW_Y] - view[VIEW_EYE][2],
        mpfr(0) - view[VIEW_EYE][3]))

    result = scene_obj.test_intersect(ray)

    if(result is not False):
        result['ray'] = ray
        clr = view[VIEW_LIGHTINGMODEL][LIGHTINGMODEL_BASIC_CALCFUNC](
            view[VIEW_LIGHTINGMODEL], scene_obj, result,
            lighting_model_flags)
        return clr

    return ('colour', 0, 0, 0)


def view_render_pixel_antialias_edge_detect_get_surrounding_eight(view):
    """Returns the eight surrounding view co-ordinates for the pixel
    currently being rendered

    :param view: the view
    :return: an array of tuples with view co-ordinates
    """
    # view[VIEW_VIEWRECTANGLE]
    # view[VIEW_VIEW_X]
    coordinates = []

    if (view[VIEW_VIEW_Y] > view[VIEW_VIEWRECTANGLE]['top']):
        coordinates.append(
            (view[VIEW_VIEW_X]),
            view[VIEW_VIEW_Y] - view[VIEW_ANTIALIAS]['y_step'])

    if (view[VIEW_VIEW_Y] < view[VIEW_VIEWRECTANGLE]['bottom']):
        coordinates.append(
            (view[VIEW_VIEW_X]),
            view[VIEW_VIEW_Y] + view[VIEW_ANTIALIAS]['y_step'])

    if (view[VIEW_VIEW_X] > view[VIEW_VIEWRECTANGLE]['left']):
        coordinates.append(
            (view[VIEW_VIEW_X] - view[VIEW_ANTIALIAS]['x_step']),
            view[VIEW_VIEW_Y])
        if (view[VIEW_VIEW_Y] > view[VIEW_VIEWRECTANGLE]['top']):
            coordinates.append(
                (view[VIEW_VIEW_X] - view[VIEW_ANTIALIAS]['x_step']),
                view[VIEW_VIEW_Y] - view[VIEW_ANTIALIAS]['y_step'])

        if (view[VIEW_VIEW_Y] < view[VIEW_VIEWRECTANGLE]['bottom']):
            coordinates.append(
                (view[VIEW_VIEW_X] - view[VIEW_ANTIALIAS]['x_step']),
                view[VIEW_VIEW_Y] + view[VIEW_ANTIALIAS]['y_step'])

    if (view[VIEW_VIEW_X] < view[VIEW_VIEWRECTANGLE]['right']):
        coordinates.append(
            (view[VIEW_VIEW_X] + view[VIEW_ANTIALIAS]['x_step']),
            view[VIEW_VIEW_Y])
        if (view[VIEW_VIEW_Y] > view[VIEW_VIEWRECTANGLE]['top']):
            coordinates.append(
                (view[VIEW_VIEW_X] + view[VIEW_ANTIALIAS]['x_step']),
                view[VIEW_VIEW_Y] - view[VIEW_ANTIALIAS]['y_step'])

        if (view[VIEW_VIEW_Y] < view[VIEW_VIEWRECTANGLE]['bottom']):
            coordinates.append(
                (view[VIEW_VIEW_X] + view[VIEW_ANTIALIAS]['x_step']),
                view[VIEW_VIEW_Y] + view[VIEW_ANTIALIAS]['y_step'])

    return coordinates


def view_render_pixel_antialias_edge_detect(
        view, scene_obj, lighting_model_flags=0):
    """
    Performs edge-detecting antialiasing for the current pixel of a render.

    :param view: The view to render
    :param scene_obj: The scene to render
    :param lightingmodel_flags: Flags that affect behaviour of the lighting
                                model
    :return: a colour tuple
    """

    clr = view_render_pixel_no_antialias(
        view, scene_obj, lighting_model_flags)

    surrounding_coordinates = \
        view_render_pixel_antialias_edge_detect_get_surrounding_eight(view)

    do_antialias = False

    for coordinate in surrounding_coordinates:
        if coordinate[0] in view[VIEW_ANTIALIAS_DATA]['edge_detection_map']:
            if (coordinate[1] in
                    view[VIEW_ANTIALIAS_DATA]
                    ['edge_detection_map'][coordinate[0]]):
                cell = (view[VIEW_ANTIALIAS_DATA]['edge_detection_map']
                        [coordinate[0]][coordinate[1]])

                cell_colour = cell[1]

                color_diff = (abs(clr[1] - cell_colour[1] +
                                  abs(clr[2] - cell_colour[2]) +
                                  abs(clr[3] - cell_colour[2])))

                if (color_diff >=
                        view[VIEW_ANTIALIAS]['edge_detect_threshold']):
                    do_antialias = True
                    break

    # view[VIEW_ANTIALIAS_DATA]['edge_detection_map']
    if do_antialias:
        if view[VIEW_ANTIALIAS]['stochastic']:
            clr_aa = view_render_pixel_antialias_stochastic(
                view, scene_obj, lighting_model_flags)
        else:
            clr_aa = view_render_pixel_antialias_grid_pattern(
                view, scene_obj, lighting_model_flags)

            clr = colour_add(
                color_scale(clr_aa, view[VIEW_ANTIALIAS]['count'] /
                            (view[VIEW_ANTIALIAS]['count'] + 1.0)),

                color_scale(clr, 1.0 /
                            (view[VIEW_ANTIALIAS]['count'] + 1.0)))

    return clr


def view_render_pixel_antialias_stochastic(
        view, scene_obj, lighting_model_flags=0):
    """
    Performs stochastic antialiasing for the current pixel of a render.

    :param view: The view to render
    :param scene_obj: The scene to render
    :param lightingmodel_flags: Flags that affect behaviour of the lighting
                                model
    :return: a colour tuple
    """
    clr = colour_create(0, 0, 0)
    zero = mpfr(0)
    for i in range(view[VIEW_ANTIALIAS_DATA]['count']):
        a_view_x = random.uniform(
            view[VIEW_VIEW_X], view[VIEW_VIEW_X] +
            view[VIEW_ANTIALIAS_DATA]['x_step'])
        a_view_y = random.uniform(
            view[VIEW_VIEW_Y], view[VIEW_VIEW_Y] +
            view[VIEW_ANTIALIAS_DATA]['y_step'])
        ray = ray_create(view[VIEW_EYE],
                         cartesian_create(
            a_view_x - view[VIEW_EYE][1],
            a_view_y - view[VIEW_EYE][2],
            zero - view[VIEW_EYE][3]))
        result = scene_obj.test_intersect(ray)
        if(result is not False):
            result['ray'] = ray
            colour = colour_scale(
                view[VIEW_LIGHTINGMODEL]
                [LIGHTINGMODEL_BASIC_CALCFUNC]
                (view[VIEW_LIGHTINGMODEL],
                 scene_obj, result),
                view[VIEW_ANTIALIAS_DATA]['colour_scale'])
            clr = colour_add(clr, colour)
    return clr


def view_render_pixel_antialias_grid_pattern(
        view, scene_obj, lighting_model_flags=0):
    """
    Performs non-stochastic antialiasing for the current pixel of a render.

    :param view: The view to render
    :param scene_obj: The scene to render
    :param lightingmodel_flags: Flags that affect behaviour of the lighting
                                model
    :return: a colour tuple
    """
    zero = mpfr(0)
    clr = colour_create(0, 0, 0)
    a_view_x = view[VIEW_VIEW_X] - view[VIEW_ANTIALIAS_DATA]['x_step']

    xc = 0
    yc = 0
    # while a_view_x < view[VIEW_VIEW_X]:
    for i in range(0, int(view[VIEW_ANTIALIAS]['y'])):
        a_view_y = view[VIEW_VIEW_Y] - view[VIEW_ANTIALIAS_DATA]['y_step']
        xc = xc + 1
        a_view_x = a_view_x + view[VIEW_ANTIALIAS_DATA]['a_view_step_x']
        # while a_view_y < view[VIEW_VIEW_Y]:
        for j in range(0, int(view[VIEW_ANTIALIAS]['y'])):
            yc = yc + 1
            a_view_y = a_view_y + \
                view[VIEW_ANTIALIAS_DATA]['a_view_step_y']

            ray = ray_create(view[VIEW_EYE],
                             cartesian_create(
                a_view_x - view[VIEW_EYE][1],
                a_view_y - view[VIEW_EYE][2],
                zero - view[VIEW_EYE][3]))
            result = scene_obj.test_intersect(ray)
            if(result is not False):
                result['ray'] = ray
                colour = colour_scale(view[VIEW_LIGHTINGMODEL]
                                      [LIGHTINGMODEL_BASIC_CALCFUNC](
                    view[VIEW_LIGHTINGMODEL], scene_obj,
                    result, lighting_model_flags),
                    view[VIEW_ANTIALIAS_DATA]['colour_scale'])
                clr = colour_add(clr, colour)

    return clr


def view_render(view, scene_obj, output_type, lighting_model_flags=0):
    """Renders a view of a scene.

     :param view: The view to render
     :param scene_obj: The scene to render
     :param output_type: An instance of class Output
     :param lightingmodel_flags: Flags that affect behaviour of the lighting
                                 model"""

    output_type.set_rectangle(view[VIEW_PHYSICALRECTANGLE])
    if not isinstance(scene_obj, Scene):
        return None
    view[VIEW_VIEW_Y] = view[VIEW_VIEWRECTANGLE]['top']
    view[VIEW_VIEW_X] = view[VIEW_VIEWRECTANGLE]['left']
    x_step = (view[VIEW_VIEWRECTANGLE]['right'] -
              view[VIEW_VIEWRECTANGLE]['left']) / \
        (view[VIEW_PHYSICALRECTANGLE]['right'] -
         view[VIEW_PHYSICALRECTANGLE]['left'])
    view[VIEW_ANTIALIAS]['x_step'] = x_step

    y_step = (mpfr(view[VIEW_VIEWRECTANGLE]['bottom']) -
              view[VIEW_VIEWRECTANGLE]['top']) / \
        (mpfr(view[VIEW_PHYSICALRECTANGLE]['bottom']) -
         mpfr(view[VIEW_PHYSICALRECTANGLE]['top']))

    view[VIEW_ANTIALIAS]['y_step'] = y_step

    if view[VIEW_ANTIALIAS]['on']:
        a_view_step_x = x_step / mpfr(view[VIEW_ANTIALIAS]['x'])
        a_view_step_y = y_step / mpfr(view[VIEW_ANTIALIAS]['y'])
        do_random = view[VIEW_ANTIALIAS]['stochastic']

    zero = mpfr(0)

    for physical_x in range(view[VIEW_PHYSICALRECTANGLE]['left'],
                            view[VIEW_PHYSICALRECTANGLE]['right']):

        view[VIEW_VIEW_Y] = mpfr(view[VIEW_VIEWRECTANGLE]['top'])
        for physical_y in range(view[VIEW_PHYSICALRECTANGLE]['top'],
                                view[VIEW_PHYSICALRECTANGLE]['bottom']):

            clr = view_render_pixel(view, scene_obj, physical_x, physical_y,
                                    output_type, lighting_model_flags)

            view[VIEW_VIEW_Y] = view[VIEW_VIEW_Y] + y_step

        view[VIEW_VIEW_X] = view[VIEW_VIEW_X] + x_step

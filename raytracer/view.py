try:
    from gmpy2 import *
    from math import degrees
except ImportError:
    from math import *
    from raytracer.mpfr_dummy import *

from raytracer.cartesian import *
from raytracer.colour import *
from raytracer.matrix import *
from raytracer.light import *
from raytracer.output import *
from raytracer.shape import *
from raytracer.scene import *
from raytracer.lighting_model import *
import multiprocessing as mp
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

    * A dictionary of data intended for internal use with anti-aliasing:

        'count': The total number of sub samples taken for each pixel, i.e.
            member 'x' times member 'y'
        'colour_scale': The multiplier for each colour subsample to be scaled
            by. This is the inverse of member 'count'
        'x_step': The scene distance to move horizontally for each horizontal
            pixel on the physical output
        'y_step': The scene distance to move vertically for each vertical
            pixel on the physical output
        'a_view_step_x': The horizontal step distance to use for sub sampling
        'a_view_step_y': The vertical step distance to use for sub sampling


    * The current X-position during rendering (intended for internal use)

    * The current Y-position during rendering (intended for internal use)"""

VIEW_LIGHTINGMODEL = 1
VIEW_OUTPUT = 2
VIEW_PHYSICALRECTANGLE = 3
VIEW_VIEWRECTANGLE = 4
VIEW_ANTIALIAS = 5
VIEW_TRANSFORM = 6
VIEW_EYEZ = 7
VIEW_EYE = 8
VIEW_ANTIALIAS_DATA = 9
VIEW_MULTIPROCESS_POOL = 10
VIEW_MULTIPROCESS_OPTIONS = 11
VIEW_SCENE = 12

def view_create(
        scene, eye_z,  physical_rectangle,
        view_rectangle, transform=None, output=None):
    """Creates a view.

     :param eye_z: The Z-position of the eye point. This should be a negative
                   value.

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

    :param transformation: A transformation to apply to the view (optional)

    :param output: A child class of Output
    
    :return: A list of view parameters, or None on failure"""   
    if not type(physical_rectangle) is dict:
        return None
    if not type(view_rectangle) is dict:
        return None
    view_rectangle['top'] = mpfr(view_rectangle['top'])
    view_rectangle['left'] = mpfr(view_rectangle['left'])
    view_rectangle['bottom'] = mpfr(view_rectangle['bottom'])
    view_rectangle['right'] = mpfr(view_rectangle['right'])
    view = ['view',
            lightingmodel_basic_create(),
            output,
            physical_rectangle,
            view_rectangle,
            {},
            transform,
            mpfr(eye_z),
            cartesian_create((view_rectangle['left'] +
                              view_rectangle['right']) / mpfr(2.0),
                             (view_rectangle['top'] +
                              view_rectangle['bottom']) /
                             mpfr(2.0), eye_z),
            {},
            None,
            {'DoMultiProcessing': True, 'MaxProcesses': 0},
            scene]

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


def view_set_output(view, output):
    """Set or change the transformation for a view.

     :param view: The view to change
     :param transform: The Transformation to apply"""

    view[VIEW_OUTPUT] = output

def view_set_multiprocessing(
        view, do_multiprocessing = True, max_processes = 0):
        view[VIEW_MULTIPROCESS_OPTIONS] = \
            {'DoMultiProcessing':  do_multiprocessing,
            'MaxProcesses': max_processes}

    
def view_set_antialias(
        view, on=False, x=1, y=1, stochastic=False,
        edge_detect=False, ed_threshold=.3):
    """Sets the antialias parameters for a view.

     :param view: The view to change
     :param on: Boolean value dictating to using antialias while rendering
        or not
     :param stochastic: Boolean value dictating use of stochastic/random
        antialiasing
     :param edge_detect: Boolean value dictating use edge detection
     :param ed_threshold: a value between one and 0 indicating the difference
                          between pixels necessary for edge-detecting
                          antialiasing
     :param x: How many times to divide a pixel on the horizontal axis
     :param y: How many times to divide a pixel on the vertical axis

     """

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
            view[VIEW_ANTIALIAS_DATA]['rerender_list'] = []
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


def view_set_lighting_model(view, lightingmodel, options={}):
    """Sets the lighting model for a view

     :param view: The view to change
     :param lightingmodel: Lighting model to use while rendering the scene
     :param options: optional lighting model  options dictionary
     """
    view[VIEW_LIGHTINGMODEL] = lightingmodel
    
    lightingmodel_set_options (lightingmodel, options)

def view_transform_ray (view, ray):
    if view[VIEW_TRANSFORM] is not None:

        ray_dir = view[VIEW_TRANSFORM].transform_cartesian (ray[RAY_DIR], True)
        ray_start =  view[VIEW_TRANSFORM].transform_point (ray[RAY_START])

        ray = ray_create(ray_start, ray_dir)
        
    return ray

def view_render_pixel(view, view_scan_x, view_scan_y):
    """Renders one pixel of a view

     :param view: The view to render
     :param physical_x: The X co-ordinate of the pixel
     :param physical_y: The Y co-ordinate of the pixel
     """

    clr = view[VIEW_ANTIALIAS_DATA]['antialias_function'](
        view, view_scan_x, view_scan_y)

    if 'rerender_list' in view[VIEW_ANTIALIAS_DATA]:
        while len(view[VIEW_ANTIALIAS_DATA]['rerender_list']) > 0:
            item = view[VIEW_ANTIALIAS_DATA]['rerender_list'].pop(0)

            view_render_pixel_antialias_edge_detect(view, 
                item[1][0], item[1][1], True) # ???

    return clr


def view_render_pixel_no_antialias(view, view_scan_x, view_scan_y):
    """clr
    Performs the current pixel of a render without antialiasing.

    :param view: The view to render
    :param lightingmodel_flags: Flags that affect behaviour of the lighting
                                model
    :return: a colour tuple
    """
    ray = ray_create(view[VIEW_EYE],
                     cartesian_create(
        view_scan_x - view[VIEW_EYE][1],
        view_scan_y - view[VIEW_EYE][2],
        mpfr(0) - view[VIEW_EYE][3]))

    ray = view_transform_ray (view, ray)
    
    result = view[VIEW_SCENE].test_intersect(ray)

    if(result is not False):
        result['ray'] = ray
        clr = view[VIEW_LIGHTINGMODEL][LIGHTINGMODEL_CALCFUNC](
            view[VIEW_LIGHTINGMODEL], view[VIEW_SCENE], result)
        return clr

    return ('colour', 0, 0, 0)


def view_render_pixel_antialias_edge_detect_get_surrounding_eight(
        view, view_scan_x, view_scan_y):
    """Returns the eight surrounding view co-ordinates for the pixel
    currently being rendered

    :param view: the view
    :return: an array of tuples with view co-ordinates
    """

    coordinates = []

    if (view_scan_y > view[VIEW_VIEWRECTANGLE]['top']):
        coordinates.append(
            (view_scan_x,
             view_scan_y - view[VIEW_ANTIALIAS]['y_step']))

    if (view_scan_y < view[VIEW_VIEWRECTANGLE]['bottom']):
        coordinates.append(
            (view_scan_x,
             view_scan_y + view[VIEW_ANTIALIAS]['y_step']))

    if (view_scan_x > view[VIEW_VIEWRECTANGLE]['left']):
        coordinates.append(
            (view_scan_x - view[VIEW_ANTIALIAS]['x_step'],
             view_scan_y))
        if (view_scan_y > view[VIEW_VIEWRECTANGLE]['top']):
            coordinates.append(
                (view_scan_x - view[VIEW_ANTIALIAS]['x_step'],
                 view_scan_y - view[VIEW_ANTIALIAS]['y_step']))

        if (view_scan_y < view[VIEW_VIEWRECTANGLE]['bottom']):
            coordinates.append(
                (view_scan_x - view[VIEW_ANTIALIAS]['x_step'],
                 view_scan_y + view[VIEW_ANTIALIAS]['y_step']))

    if (view_scan_x < view[VIEW_VIEWRECTANGLE]['right']):
        coordinates.append(
            (view_scan_x + view[VIEW_ANTIALIAS]['x_step'],
             view_scan_y))
        if (view_scan_y > view[VIEW_VIEWRECTANGLE]['top']):
            coordinates.append(
                (view_scan_x + view[VIEW_ANTIALIAS]['x_step'],
                 view_scan_y - view[VIEW_ANTIALIAS]['y_step']))

        if (view_scan_y < view[VIEW_VIEWRECTANGLE]['bottom']):
            coordinates.append(
                (view_scan_x + view[VIEW_ANTIALIAS]['x_step'],
                 view_scan_y + view[VIEW_ANTIALIAS]['y_step']))

    return coordinates


def view_render_pixel_antialias_edge_detect(view, view_scan_x, view_scan_y,
    force_antialias=False):
    """
    Performs edge-detecting antialiasing for the current pixel of a render.

    :param view: The view to render
    :param force_antialias: Boolean - disregard edge detection and antialias
                                      anyhow
    :return: a colour tuple
    """

    if not force_antialias:
        clr = view_render_pixel_no_antialias(view, view_scan_x, view_scan_y)

    surrounding_coordinates = \
        view_render_pixel_antialias_edge_detect_get_surrounding_eight(
            view, view_scan_x, view_scan_y)

    if force_antialias:
        do_antialias = True
    else:
        do_antialias = False
        for coordinate in surrounding_coordinates:

            if (coordinate[0] in
                    view[VIEW_ANTIALIAS_DATA]['edge_detection_map']):
                if (coordinate[1] in
                        view[VIEW_ANTIALIAS_DATA]
                        ['edge_detection_map'][coordinate[0]]):
                    cell = (view[VIEW_ANTIALIAS_DATA]['edge_detection_map']
                            [coordinate[0]][coordinate[1]])

                    cell_colour = cell[1]

                    color_diff = (abs(clr[1] - cell_colour[1]) +
                                  abs(clr[2] - cell_colour[2]) +
                                  abs(clr[3] - cell_colour[3]))

                    if (color_diff >=
                            view[VIEW_ANTIALIAS]['edge_detect_threshold']):
                        do_antialias = True

    if do_antialias:
        if view[VIEW_ANTIALIAS]['stochastic']:
            clr_aa = view_render_pixel_antialias_stochastic(
                view, view_scan_x, view_scan_y)
        else:
            clr_aa = view_render_pixel_antialias_grid_pattern(
                view, view_scan_x, view_scan_y)

        if force_antialias:
            clr = clr_aa
        else:
            clr = colour_add(
                colour_scale(clr_aa, view[VIEW_ANTIALIAS]['count'] /
                             (view[VIEW_ANTIALIAS]['count'] + 1.0)),

                colour_scale(clr, 1.0 /
                             (view[VIEW_ANTIALIAS]['count'] + 1.0)))

        for coordinate in surrounding_coordinates:

            if (coordinate[0] in
                    view[VIEW_ANTIALIAS_DATA]['edge_detection_map']):
                if (coordinate[1] in
                        view[VIEW_ANTIALIAS_DATA]
                        ['edge_detection_map'][coordinate[0]]):
                    cell = (view[VIEW_ANTIALIAS_DATA]['edge_detection_map']
                            [coordinate[0]][coordinate[1]])
                    cell_colour = cell[1]

                    color_diff = (abs(clr[1] - cell_colour[1] +
                                      abs(clr[2] - cell_colour[2]) +
                                      abs(clr[3] - cell_colour[2])))
                    if (not cell[0] and color_diff >=
                            view[VIEW_ANTIALIAS]['edge_detect_threshold']):

                        view[VIEW_ANTIALIAS_DATA]['rerender_list'].append(
                            (view_render_pixel_antialias_edge_detect,
                             coordinate))

    if view_scan_x not in \
            view[VIEW_ANTIALIAS_DATA]['edge_detection_map']:
        view[VIEW_ANTIALIAS_DATA]['edge_detection_map'][view_scan_x] = {}

    view[VIEW_ANTIALIAS_DATA]['edge_detection_map'][
        view_scan_x][view_scan_y] = (do_antialias, clr)
    return clr


def view_render_pixel_antialias_stochastic(view, view_scan_x, view_scan_y):
    """
    Performs stochastic antialiasing for the current pixel of a render.

    :param view: The view to render

    :return: a colour tuple
    """
    clr = colour_create(0, 0, 0)
    zero = mpfr(0)
    for i in range(int(view[VIEW_ANTIALIAS_DATA]['count'])):
        a_view_x = random.uniform(
            view_scan_x, view_scan_x +
            view[VIEW_ANTIALIAS_DATA]['x_step'])
        a_view_y = random.uniform(
            view_scan_y, view_scan_y +
            view[VIEW_ANTIALIAS_DATA]['y_step'])
        ray = ray_create(view[VIEW_EYE],
                         cartesian_create(
            a_view_x - view[VIEW_EYE][1],
            a_view_y - view[VIEW_EYE][2],
            zero - view[VIEW_EYE][3]))
            
        ray = view_transform_ray (view, ray)
        
        result = view[VIEW_SCENE].test_intersect(ray)
        if(result is not False):
            result['ray'] = ray
            colour = colour_scale(
                view[VIEW_LIGHTINGMODEL]
                [LIGHTINGMODEL_CALCFUNC]
                (view[VIEW_LIGHTINGMODEL],
                 view[VIEW_SCENE], result),
                view[VIEW_ANTIALIAS_DATA]['colour_scale'])
            clr = colour_add(clr, colour)
    return clr


def view_render_pixel_antialias_grid_pattern(view, view_scan_x, view_scan_y):
    """
    Performs non-stochastic antialiasing for the current pixel of a render.

    :param view: The view to render

    :return: a colour tuple
    """
    zero = mpfr(0)
    clr = colour_create(0, 0, 0)
    a_view_x = view_scan_x - view[VIEW_ANTIALIAS_DATA]['x_step']

    xc = 0
    yc = 0
    # while a_view_x < view_scan_x:
    for i in range(0, int(view[VIEW_ANTIALIAS]['y'])):
        a_view_y = view_scan_y - view[VIEW_ANTIALIAS_DATA]['y_step']
        xc = xc + 1
        a_view_x = a_view_x + view[VIEW_ANTIALIAS_DATA]['a_view_step_x']
        # while a_view_y < view_scan_y:
        for j in range(0, int(view[VIEW_ANTIALIAS]['y'])):
            yc = yc + 1
            a_view_y = a_view_y + \
                view[VIEW_ANTIALIAS_DATA]['a_view_step_y']

            ray = ray_create(view[VIEW_EYE],
                             cartesian_create(
                a_view_x - view[VIEW_EYE][1],
                a_view_y - view[VIEW_EYE][2],
                zero - view[VIEW_EYE][3]))
            ray = view_transform_ray (view, ray)
            result = view[VIEW_SCENE].test_intersect(ray)
            if(result is not False):
                result['ray'] = ray
                colour = colour_scale(view[VIEW_LIGHTINGMODEL]
                                      [LIGHTINGMODEL_BASIC_CALCFUNC](
                    view[VIEW_LIGHTINGMODEL], view[VIEW_SCENE],
                    result),
                    view[VIEW_ANTIALIAS_DATA]['colour_scale'])
                clr = colour_add(clr, colour)

    return clr


def view_render(view):
    """Renders a view of a scene.

     :param view: The view to render
    """

    view[VIEW_OUTPUT].set_rectangle(view[VIEW_PHYSICALRECTANGLE])
    if not isinstance(view[VIEW_SCENE], Scene):
        return None
    view_scan_y = view[VIEW_VIEWRECTANGLE]['top']
    view_scan_x = view[VIEW_VIEWRECTANGLE]['left']
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

    if ('DoMultiProcessing' in view[VIEW_MULTIPROCESS_OPTIONS] and
        view[VIEW_MULTIPROCESS_OPTIONS]['DoMultiProcessing']):
        queue_func = view_process_queue_multiprocess
        
        if 'MaxProcesses' in view[VIEW_MULTIPROCESS_OPTIONS]:
            max_processes = view[VIEW_MULTIPROCESS_OPTIONS]['MaxProcesses']
        else:
            max_processes = 0
        
        if max_processes <= 0:
            view[VIEW_MULTIPROCESS_POOL]= mp.Pool(mp.cpu_count())
        else:
            view[VIEW_MULTIPROCESS_POOL]= mp.Pool(max_processes)
    
    else:
        queue_func = view_process_queue
    
    queue = []
    
    for physical_x in range(view[VIEW_PHYSICALRECTANGLE]['left'],
                            view[VIEW_PHYSICALRECTANGLE]['right']):

        view_scan_y = mpfr(view[VIEW_VIEWRECTANGLE]['top'])
        for physical_y in range(view[VIEW_PHYSICALRECTANGLE]['top'],
                                view[VIEW_PHYSICALRECTANGLE]['bottom']):
            
            if type(queue) == list:
                # print ((view_scan_x, view_scan_y))
                queue.append([view, view_scan_x, view_scan_y,
                    physical_x, physical_y, False])
                
            else:
                clr = view_render_pixel(view, view_scan_x, view_scan_y) 
                view[VIEW_OUTPUT].set_pixel(physical_x, physical_y, clr)
                
            view_scan_y = view_scan_y + y_step

        view_scan_x = view_scan_x + x_step

    queue_func(view, queue)
        
def view_process_queue(view, queue):
    while len(queue)>0:
        item = queue.pop(0)
        #if (item[3] == 121 and  item[4] == 40):
        #    import pdb; pdb.set_trace();
        clr = view_render_pixel(item[0], item[1], item[2])
        #clr = view_pp_render_pixel (item)
        view[VIEW_OUTPUT].set_pixel(item[3], item[4], clr)

def view_process_queue_multiprocess(view, queue):

    # Seems to unable to pass
    output = view[VIEW_OUTPUT]
    pool = view[VIEW_MULTIPROCESS_POOL]
    view[VIEW_OUTPUT] = None
    view[VIEW_MULTIPROCESS_POOL] = None
    colours = pool.map(view_pp_render_pixel, queue)
   
    view[VIEW_OUTPUT] = output
    view[VIEW_MULTIPROCESS_POOL] = pool
    
    for clr, queue_item in zip (colours, queue):
        view[VIEW_OUTPUT].set_pixel(queue_item[3], queue_item[4], clr)
    
    del queue[:] #empty the list

def view_pp_render_pixel(queue_item):
    view, view_scan_x, view_scan_y, physical_x, physical_y, force_aa = \
        queue_item
    
    clr = view_render_pixel(view, view_scan_x, view_scan_y)

    return clr


def view_create_look_at (
        scene, physical_rectangle,
        view_width,
        eye_distance_to_screen,
        eye_point,
        look_at,
        scale = 1,
        z_rotation = 0,
        output = None):

    """
    :param view_width: the width od the view at the scree point, in scene-space
    :eye_distance_to_screen: the distance from the eye to the screen
    :eye_point: cartesian for the eye location
    :param physical_rectangle: The rectangle of the physical output to draw
        onto. This is value is a dictionary:
        'left': the left-hand edge of the physical output to draw onto
        'right': the right-hand edge of the physical output to draw onto
        'top': the top edge of the physical output to draw onto
        'bottom': the bottom edge of the physical output to draw onto
    :look_at: cartesian point to look at
    :scale: scale/zoom factor
    :z_rotation: the amount of rotation about the line of sight
    :output: an instance of class Output
    """        
    if (eye_point[1] == look_at[1] and 
        eye_point[2] == look_at[2] and 
        eye_point[3] == look_at[3]):        
        raise Exception('eye_point and look_at are the same')
    
    physical_width = physical_rectangle['right'] - physical_rectangle['left']
    physical_height = physical_rectangle['bottom'] - physical_rectangle['top']
    aspect_ratio = physical_width/physical_height
    
    view_height = mpfr(view_width/aspect_ratio)
    
    # cartesian_sub(look_at, eye_point)
    view_axis = cartesian_sub(look_at, eye_point)
    view_axis_normalised = cartesian_normalise(view_axis)        
    
    eye_translate = {'x': 0 - eye_point[1],
        'y': 0 - eye_point[2],
        'z': 0 - (eye_point[3] + eye_distance_to_screen )}

    transform = Transform ({'translate':eye_translate })

    if view_axis[1] == 0 and view_axis[2] == 0:

        rotation_axis= cartesian_cross(
            view_axis_normalised, ('cartesian', 1, 0, 0))

    else:
        rotation_axis= cartesian_normalise(cartesian_cross(
            view_axis_normalised, ('cartesian', 0, 0, 1)))

    
    rotation_angle = math.degrees(
                        acos(
                            cartesian_dot(
                                view_axis_normalised, ('cartesian', 0, 0, 1))))
       
    eye_z = 0 - eye_distance_to_screen

    
    rotation_z_matrix = RotationZMatrix (0 - z_rotation)
    # rotation_z_matrix = RotationMatrix(view_axis, z_rotation)
    look_at_matrix = RotationMatrix(rotation_axis,  0 - rotation_angle)
    scale_matrix = ScaleMatrix (1, 1, scale)
    matrix =    look_at_matrix  * scale_matrix * rotation_z_matrix
    transform.set_matrix(matrix)

    view_rectangle = {
        'left': 0 - (view_width / 2.0),
        'right': (view_width / 2.0) ,
        'top': 0 - (view_height / 2.0),
        'bottom':  (view_height / 2.0)       
    }
    view = view_create (
            scene,
            eye_z,
            physical_rectangle,
            view_rectangle,

            transform,
            output
            )

    return view
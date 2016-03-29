import sys
import os
import gmpy2
from gmpy2 import *
import random
from cartesian import *
from colour import *
from matrix import *
from light import *
from output import *
from shape import *
from view import *
from scene import *
from quadraticshapes import *
from planarshapes import *

from timeit import *


from lightingModel import *

if __name__ == '__main__':

    get_context().precision = 32

    scene = Scene()
    view = view_create(-15, {'left': 0,
                             'right': 300,
                             'top': 0,
                             'bottom': 300},
                       # {'left':.1, 'right':.1, 'top':.1, 'bottom':.1}),
                       {'left': -5, 'right': 5, 'top': -5, 'bottom': 5})

    scene.add_view(view, 'view')

    sphere2 = shape_cone_create(
        colour_create(1, .6, 1),
        colour_create(0, 0, 0))

    # shape_set_transform(sphere2,
    #    Transform({'scale': {'x': 2, 'y': 2.0, 'z': 2},
    #    'translate': {'x': 0, 'y': 0, 'z': 0},
    #    'rotate': {'vector': cartesian_create(1, 0, 0),
    #                                   'angle': 180}}))

    tetra_data = {
        'points': [cartesian_create(-1, -1, 1),
                   cartesian_create(1, -1, 1),
                   cartesian_create(1, 1, 1),
                   cartesian_create(-1, 1, 1),
                   cartesian_create(0, 0, 0)],

        'polygon_point_indices': [[0, 1, 2, 3],
                                  [4, 0, 1],
                                  [4, 1, 2],
                                  [4, 2, 3],
                                  [4, 3, 0]],

        'face_diffuse_colours': [colour_create(0, 1, 0),
                                 colour_create(1, 1, 1),
                                 colour_create(0, 0, 1),
                                 colour_create(0, 1, 1),
                                 colour_create(1, 0, 0)],
    }
    poly_mesh = shape_polymesh_create(tetra_data)

    shape_set_transform(poly_mesh, Transform({
        'scale': {'x': 1.0, 'y': 3.0, 'z': 2.0},
        'rotate': {'vector': cartesian_create(1, 0, 0), 'angle': 90},
        'translate': {'x': 3, 'y': 0, 'z': 0}
    }))

    poly_data = {
        'colour': colour_create(1, 0, 1),
        'points': [cartesian_create(-1, -1, 5),
                   cartesian_create(1, -1, 5),
                   cartesian_create(1, 1, 5),
                   cartesian_create(-1, 1, 5)]}

    polygon = shape_polygon_create(poly_data)
    shape_set_transform(polygon, Transform({
        'scale': {'x': 2.0, 'y': 1.0, 'z': 1.0},
        'rotate': {'vector': cartesian_create(1, 0, 0), 'angle': 30},
    }))

    # scene.addShape(poly_mesh, 'triMesh')
    scene.add_shape(sphere2, 'sph2')

    scene.add_light(light_point_light_create(cartesian_create(
        0, 0, -1.5), colour_create(1, 1, 1)), 'light1')

    image = scene.render('view')
    image.show()

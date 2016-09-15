# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.


import sys
import os
import random
from raytracer.cartesian import *
from raytracer.colour import *
from raytracer.matrix import *
from raytracer.light import *
from raytracer.output import *
from raytracer.shape import *
from raytracer.view import *
from raytracer.scene import *
from raytracer.quadraticshapes import *
from raytracer.planarshapes import *
from raytracer.lighting_model import *

if __name__ == '__main__': 
    
    get_context().precision = 32

    scene = Scene()
    view = view_create(scene, -15, {'left': 0,
                             'right': 300,
                             'top': 0,
                             'bottom': 300},
                       # {'left':.1, 'right':.1, 'top':.1, 'bottom':.1}),
                       {'left': -5, 'right': 5, 'top': -5, 'bottom': 5})
    view_set_output(view, PIL_Output())
    view_set_multiprocessing(view, True)
    scene.add_view(view, 'view')
    
    tgl = shape_triangle_create(
        [('cartesion', 0,0,0), ('cartsian', -3, -3, 1), ('cartsian', 3, -6, 3) ],
        ('colour_mapping', triangle_map_to_rect, PILImageTexture("examples/ocean-sunrise.jpg"))
        )
    
    scene.add_shape(tgl, 'triMesh')

    scene.add_light(light_point_light_create(cartesian_create(
        0, 0, -10), colour_create(1, 1, 1)), 'light1')

    image = scene.render('view')
    image.show()

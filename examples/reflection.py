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
from raytracer.mapping import *

if __name__ == '__main__':
    get_context().precision = 32

    scene = Scene(True)
    view = view_create(scene, -3, {'left': 0,
                             'right': 300,
                             'top': 0,
                             'bottom': 300},
                       # {'left':.1, 'right':.1, 'top':.1, 'bottom':.1}),
                       {'left': -5, 'right': 5, 'top': -5, 'bottom': 5})


    view_set_antialias (view, False, 5, 5, True) #, True, .4)
    view_set_output(view, PIL_Output())
    view_set_multiprocessing(view, True);
    view_set_lighting_model (view, view[VIEW_LIGHTINGMODEL],
         {'NoShadows': False, 'NoDiffuse': False, 'NoReflections': False})
    scene.add_view(view, 'view')
    scene.add_light(light_point_light_create(
            
            cartesian_create(
                0, 0, -2), colour_create(1, 1, 1)), 'light1')
    

    rectangle = shape_rectangle_create(
        colour_create(.5, .5, .5),
        colour_create(1,1,1),
        {'top': -10, 'bottom': 10,  'left': -10, 'right': 10},
        Transform({
        'translate': {'x': 0, 'y': 0, 'z': 3}}))

    scene.add_shape(rectangle, 'squre')

    sphere = shape_sphere_create(
        colour_create(1,0,1),
        colour_create(0,0,0))
    

    scale = 3
        
    shape_set_transform(sphere, Transform({
        'scale': {'x': scale, 'y': scale, 'z': scale},

        'translate': {'x': 0, 'y': 0, 'z': -7}
    }))              

    scene.add_shape(sphere, 'sphere')
    
    image = scene.render('view')

    image.show()

           
                
    

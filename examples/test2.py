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

    scene = Scene(False)
    view = view_create(scene, -150, {'left': 0,
                             'right': 300,
                             'top': 0,
                             'bottom': 300},
                       # {'left':.1, 'right':.1, 'top':.1, 'bottom':.1}),
                       {'left': -5, 'right': 5, 'top': -5, 'bottom': 5})

                       
    view_set_antialias (view, False, 5, 5, True) #, True, .4)
    view_set_output(view, PIL_Output())
    view_set_multiprocessing(view, False, 2)
    #view_set_lighting_model (view, view[VIEW_LIGHTINGMODEL], {'NoShadows': True, 'NoDiffuse': True})
    scene.add_view(view, 'view')


    #sphere = shape_cylinder_create(
    #    ('colour_mapping', cylinder_map_to_rect, PILImageTexture("C:\\Users\\jack-2\\Desktop\\tumblr\\http___65.media.tumblr.com_81e915b5bdc8937ed4dc24519d63ab87_tumblr_o7mtlcDEDS1shlzkjo1_1280.jpg")),
    #    colour_create(0,0,0))

    sphere = shape_cylinder_create(
        ('colour_mapping', cylinder_map_to_rect,
        BandedSprialTexture([colour_create(1,0,0), colour_create(1,1,0) , colour_create(1,0,1) , colour_create(1,1,1)])),
        colour_create(0,0,0))
        
        
    shape_set_transform(sphere, Transform({
        'scale': {'x': 1, 'y': 1, 'z': 1},
        'rotate': {'vector': cartesian_create(0,1,0), 'angle':270 },
        #'translate': {'x': 3, 'y': 0, 'z': 0}
    }))


    scene.add_shape(sphere, 'triMesh')

    scene.add_light(light_point_light_create(cartesian_create(
        0, 0, -5.5), colour_create(1, 1, 1)), 'light1')

    #scene.add_light(light_point_light_create(cartesian_create(
    #    -2, 0, -5.5), colour_create(1, 1, 1)), 'light1')
        

    #for i in range (0, 360, 20):
    shape_set_transform(sphere, Transform({
         'scale': {'x': 2.0, 'y': 4.0, 'z': 1.0},
        'rotate': {'vector': cartesian_create(0,1,0), 'angle': 270},
        #'translate': {'x': 3, 'y': 0, 'z': 0}
    }))    

    #map_test()    
    image = scene.render('view')
    image.show()


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

    scene = Scene(True, 2)
    view = view_create(scene, -150, {'left': 0,
                             'right': 300,
                             'top': 0,
                             'bottom': 300},
                       # {'left':.1, 'right':.1, 'top':.1, 'bottom':.1}),
                       {'left': -5, 'right': 5, 'top': -5, 'bottom': 5})


    view_set_antialias (view, False, 5, 5, False) # True, .4)
    view_set_output(view, PIL_Output())
    view_set_multiprocessing(view, False)
    view_set_lighting_model (view, view[VIEW_LIGHTINGMODEL], {'NoShadows': True, 'NoDiffuse': False, 'NoReflections': True})
    scene.add_view(view, 'view')
    scene.add_light(light_point_light_create(cartesian_create(
        0, 0, -5.5), colour_create(1, 1, 1)), 'light1')

    scale = 1.5

    bands = []
    count = int(5)
    for j in range (0, count +2):
        bands.append(('colour', random.uniform(0,.5), random.uniform(0,.5), random.uniform(0,.5)))

    sphere = shape_sphere_create(
        ('colour_mapping', sphere_map_to_rect, BandedSprialTexture(bands)),
        colour_create(1,1,1))
        
    shape_set_transform(sphere, Transform({
        'scale': {'x': scale, 'y': scale, 'z': scale},
        # 'rotate': {'vector': cartesian_create(
        #             random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)),
        #            'angle':random.uniform(0, 360) },
        'translate': {'x': -1, 'y': 1, 'z': 1}
    }))              

    scene.add_shape(sphere)

    sphere = shape_sphere_create(
        colour_create(1,1,1),
        ('colour_mapping', sphere_map_to_rect, BandedSprialTexture(bands)))

    shape_set_transform(sphere, Transform({
        'scale': {'x': scale, 'y': scale, 'z': scale},
        # 'rotate': {'vector': cartesian_create(
        #             random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)),
        #            'angle':random.uniform(0, 360) },
        'translate': {'x': 0, 'y': 1, 'z': 1.5}
    }))   

    scene.add_shape(sphere)


    sphere = shape_sphere_create(
        colour_create(1,1,1),
        ('colour_mapping', sphere_map_to_rect, BandedSprialTexture(bands)))

    shape_set_transform(sphere, Transform({
        'scale': {'x': scale*2, 'y': scale, 'z': scale},
        # 'rotate': {'vector': cartesian_create(
        #             random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)),
        #            'angle':random.uniform(0, 360) },
        'translate': {'x': 2, 'y': 1, 'z': 1.5}
    }))   

    scene.add_shape(sphere)

    image = scene.render('view')
    
    image.show()

           
                
    

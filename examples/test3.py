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
    view = view_create(scene, -1, {'left': 0,
                             'right': 300,
                             'top': 0,
                             'bottom': 300},
                       # {'left':.1, 'right':.1, 'top':.1, 'bottom':.1}),
                       {'left': -5, 'right': 5, 'top': -5, 'bottom': 5})

                       
    view_set_antialias (view, False, 5, 5, True) #, True, .4)
    view_set_output(view, PIL_Output())
    view_set_multiprocessing(view, False, 2)
    view_set_lighting_model (view, view[VIEW_LIGHTINGMODEL], {'NoShadows': True, 'NoDiffuse': False})
    scene.add_view(view, 'view')
    scene.add_light(light_point_light_create(cartesian_create(
    0, 0, -5.5), colour_create(1, 1, 1)), 'light1')

    
    for i in range(1, 500):
    
        bands = []
        count = int(round(random.random()*5,0))
        for j in range (0, count+2):
            bands.append(('colour', random.uniform(.5,1), random.uniform(.5,1), random.uniform(.5,1)))


        sphere = shape_sphere_create(
            ('colour_mapping', sphere_map_to_rect,
            BandedSprialTexture(bands)),
            colour_create(0,0,0))
        
        
        z =  random.uniform(2, 10)
        f = 2.5 #+s (z /1.4)
            
        shape_set_transform(sphere, Transform({
            'scale': {'x': random.uniform(.5, 3.5), 'y': random.uniform(.5, 3.5), 'z': random.uniform(.5, 3.5)},
            'rotate': {'vector': cartesian_create(
                        random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)),
                        'angle':random.uniform(0, 360) },
            'translate': {'x': random.uniform(-f, f), 'y': random.uniform(-f, f), 'z': z}
        }))


        scene.add_shape(sphere, 'sphere_%i'%i)

        
    image = scene.render('view')
    image.show()

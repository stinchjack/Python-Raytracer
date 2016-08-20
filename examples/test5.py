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
    view = view_create(scene, -150, {'left': 0,
                             'right': 300,
                             'top': 0,
                             'bottom': 300},
                       # {'left':.1, 'right':.1, 'top':.1, 'bottom':.1}),
                       {'left': -5, 'right': 5, 'top': -5, 'bottom': 5})


    view_set_antialias (view, False, 5, 5, True) #, True, .4)
    view_set_output(view, PIL_Output())
    view_set_multiprocessing(view, True)
    view_set_lighting_model (view, view[VIEW_LIGHTINGMODEL], {'NoShadows': False, 'NoDiffuse': False, 'NoReflections': False})
    scene.add_view(view, 'view')
    scene.add_light(light_point_light_create(cartesian_create(
        0, 0, -5.5), colour_create(1, 1, 1)), 'light1')
    
    i = 0
    first = True
    for x in range(-1, 2):
        for y in range(-1, 2):
            for z in range(1, 4):
                i = i + 1
                bands = []
                count = int(5)
                for j in range (0, count +2):
                    bands.append(('colour', random.uniform(0,.5), random.uniform(0,.5), random.uniform(0,.5)))
        
                if i % 2:
                    sphere = shape_sphere_create(
                        ('colour_mapping', sphere_map_to_rect, BandedSprialTexture(bands)),
                        # colour_create(1,0,0),
                        colour_create(1,1,1))
                else:
                    sphere = shape_sphere_create(
                        colour_create(.5,0,0),
                        colour_create(1,1,1))                    

                scale = 1               
                if first:
                    scale = 3

                    
                shape_set_transform(sphere, Transform({
                    'scale': {'x': scale, 'y': scale, 'z': scale},
                    # 'rotate': {'vector': cartesian_create(
                    #             random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)),
                    #            'angle':random.uniform(0, 360) },
                    'translate': {'x': x*2+((z-1)*.75), 'y': y*2+((z-1)*.75), 'z': z}
                }))              
        
                scene.add_shape(sphere, 'sphere_%i'%i)
                
                first = False
        
    for i in range (0, 1, 1):
        trans = Transform({

                'rotate': {'vector': cartesian_create(0,1,0),
                        'angle': i },
                'scale': {'x': 1.5, 'y': 1.5, 'z': 1.5}

                })
        view_set_transform(view, trans)
        image = scene.render('view')

        image.show()

           
                
    

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

    scene = Scene(False, 8)
    #import pdb; pdb.set_trace();
    view = view_create_look_at(scene,
                            
                            {'left': 0,
                                'right': 300,
                                'top': 0,
                                'bottom': 300},
                            10,
                            20,
                            ('cartesian', 0, 0, -20), ## eye point,
                            ('cartesian', 0, 0, 3), ## look at
                            1,
                            0)


                       
    view_set_antialias (view, False, 3, 3, False) # True, .4)
    view_set_output(view, PIL_Output())
    view_set_multiprocessing(view, True)
    view_set_lighting_model (view, view[VIEW_LIGHTINGMODEL],
        {'NoShadows': False, 'NoDiffuse': False, 'NoReflections': False})
    scene.add_view(view, 'view')
    """scene.add_light(light_point_light_create(cartesian_create(
        0, 0, -20), colour_create(1, 1, 1)), 'light1')
        
    scene.add_light(light_point_light_create(cartesian_create(
        0, 0, 30), colour_create(1, 1, 1)), 'light2')"""
    
    scene.add_light(light_point_light_create(cartesian_create(
        0, -20, 00), colour_create(1, 1, 1)), 'light3')
        
    
    scene.add_light(light_point_light_create(cartesian_create(
     20, 20, 20), colour_create(1, 1, 1)), 'light4')   
        
    """ scene.add_light(light_point_light_create(cartesian_create(
        20, 00, 00), colour_create(1, 1, 1)), 'light5')     
    scene.add_light(light_point_light_create(cartesian_create(
        -20, 00, 00), colour_create(1, 1, 1)), 'light6')           """
    
    i = 0
    first = True
    for x in range(-1, 2):
        for y in range(-1, 2):
            for z in range(2, 7):
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
                    'translate': {'x': (x*2+((z-1)*.75)), 'y': (y*2+((z-1)*.75)), 'z': z}
                }))              
        
                scene.add_shape(sphere, 'sphere_%i'%i)
                
                first = False
        
    image = scene.render('view')

    image.show()

           
                
    

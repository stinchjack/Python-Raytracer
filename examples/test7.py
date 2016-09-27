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

    scene = Scene(True, 8)
    
    view = view_create_look_at(scene,
                            
                            {'left': 0,
                                'right': 1024,
                                'top': 0,
                                'bottom': 720},
                            10,
                            20,
                            ('cartesian', 0, 0, -22.5), ## eye point,
                            ('cartesian', 0,0,-4 ), ## look at
                            .6,
                           0)


                       
    view_set_antialias (view, True, 3, 3,  False, False)
    view_set_output(view, PIL_Output())
    view_set_multiprocessing(view, True)
    view_set_lighting_model (view, view[VIEW_LIGHTINGMODEL],
        {'NoShadows': False, 'NoDiffuse': False, 'NoReflections': False})
    scene.add_view(view, 'view')
    scene.add_light(light_point_light_create(cartesian_create(
        -20, 0, -5), colour_create(.3, .3, 0 )), 'light1')
        
    """scene.add_light(light_point_light_create(cartesian_create(
        0, 0, 30), colour_create(1, 1, 1)), 'light2')
    
    scene.add_light(light_point_light_create(cartesian_create(
        0, -20, 00), colour_create(1, 1, 1)), 'light3')
        
    
    scene.add_light(light_point_light_create(cartesian_create(
     20, 0, 00), colour_create(1, 1, 1)), 'light4')   
        
    scene.add_light(light_point_light_create(cartesian_create(
        20, 00, 00), colour_create(1, 1, 1)), 'light5')"""    
    scene.add_light(light_point_light_create(cartesian_create(
        20, 00, 00), colour_create(1.2, 1.2, .8)), 'light6')  
   
    i = 0
    first = True
    for x in range(0, 2):
        for y in range(0, 2):
            for z in range(1, 7):
                i = i + 1
                bands = []
                count = int(5)
                for j in range (0, count + 2):
                    bands.append(('colour', random.uniform(0,.5), random.uniform(0,.5), random.uniform(0,.5)))
        
                if i % 2:
                    sphere = shape_sphere_create(
                        #('colour_mapping', sphere_map_to_rect, BandedSprialTexture(bands)),
                        colour_create(.5, 0, .5),
                        colour_create(0,0,0))
                else:
                    sphere = shape_sphere_create(
                        colour_create(0,0,0),
                        colour_create(1,1,1))                    

                scale = 1               
                if first:
                    scale = 3

                    
                shape_set_transform(sphere, Transform({
                    'scale': {'x': scale, 'y': scale, 'z': scale},
                    # 'rotate': {'vector': cartesian_create(
                    #             random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)),
                    #            'angle':random.uniform(0, 360) },
                    'translate': {'x': (x*2+((z-1)*.75)), 'y': (y*2+((z-1)*.75)), 'z': z-1}
                }))              
        
                scene.add_shape(sphere, 'sphere_%i'%i)
                
                first = False

    sphere = shape_sphere_create(
                        ('colour_mapping', sphere_map_to_rect, PILImageTexture("examples/ocean-sunrise.jpg")),
                        colour_create(0,0,0))   

    scale = 50
    i += 1
    shape_set_transform(sphere, Transform({
        'scale': {'x': scale, 'y': scale, 'z': scale},
        'translate': {'x': 5, 'y':10, 'z': 5}
    }))              

    scene.add_shape(sphere, 'sphere_%i'%i)        
    
    image = scene.render('view')
    image.show()

           
                
    

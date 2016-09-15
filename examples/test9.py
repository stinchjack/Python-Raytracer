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

    scene = Scene(False)
    
    view = view_create_look_at(scene,
                            
                            {'left': 0,
                                'right': 300,
                                'top': 0,
                                'bottom': 300},
                            10,
                            20,
                            ('cartesian', 0, 0, -22.5), ## eye point,
                            ('cartesian', 0,0,-4 ), ## look at
                            .333,
                           0)

    view = view_create_look_at(scene,
                            
                            {'left': 0,
                                'right': 300,
                                'top': 0,
                                'bottom': 300},
                            10,
                            20,
                            ('cartesian', 0, 3.95, 7), ## eye point,
                            ('cartesian', 0, -20, -20 ), ## look at
                            .2,
                           180)

                       
    view_set_antialias (view, False, 3, 3,  False, False)
    view_set_output(view, PIL_Output())
    view_set_multiprocessing(view, True)
    view_set_lighting_model (
        view, view[VIEW_LIGHTINGMODEL],
            {'NoShadows': False,
            'NoDiffuse': False,
            'NoReflections': False,
            }
        )
    scene.add_view(view, 'view')
    
    
    ##########################
    scene.add_light(light_point_light_create(cartesian_create(
        0, -20, -20), colour_create((192.0/255.0), (83.0/255.0), (210.0/255.0))), 'light1')

    scene.add_light(light_point_light_create(cartesian_create(
        0, -4, 45), colour_create((192.0/255.0), (83.0/255.0), (210.0/255.0))), 'light2')    
        
    ############################33
    textr = \
        MosiacTexture (
            {
            0: [(PILImageTexture("examples/rusty-iron-tileable.jpg"), .16, .6, .15, .15)],
            1: [(TiledTexture(
                    PILImageTexture("examples/stone-tileable.jpg"),
                    6.28318530, 5), 0, 0, 1, 1)]
            },
            ('colour', 1,1,1)
        )
 
    
    cyl = shape_cylinder_create(
        ('colour_mapping', cylinder_map_to_rect,
            textr),
        colour_create(0,0,0))
    

    shape_set_transform(cyl, Transform({
        'scale': {'x': 2, 'y': 5, 'z': 2},
        'translate': {'x': 0, 'y':0, 'z': 0}
    }))
           
    
    scene.add_shape(cyl, 'tower')     
    ###############################
    
    cone = shape_cone_create(
        colour_create(1,.2,0),
        colour_create(0,0,0),
        0, 1)
    
    
    shape_set_transform(cone, Transform({
        # 'scale': {'x': 2.5, 'y': 2, 'z': 2.5},
        'translate': {'x': 0, 'y':-5.5, 'z': 0}
        }))

    #scene.add_shape(cone, 'towerTop')
    ###############################

    disc = shape_disc_create(
        ('colour_mapping', disc_map_to_rect_cookie,
            TiledTexture(
                PILImageTexture("examples/water_rippled.jpg"),
                30, 60)),
        ('colour_mapping', disc_map_to_rect_cookie,
            TiledTexture(
                PILImageTexture("examples/water_rippled_reflection.jpg"),
                30, 60))         
    )

    shape_set_transform(disc, Transform({
        'scale': {'x':50, 'y': 50, 'z': 1},
        'translate': {'x': 0, 'y':4, 'z': 0},
        'rotate':{'vector': ('c', 1.0, 0 ,0),
                    'angle': 90}
        }))
    
    scene.add_shape(disc, 'water') 
    
    ###################################
    
    sky = shape_sphere_create(
                        ('colour_mapping', sphere_map_to_rect, PILImageTexture("examples/nightsky.jpeg")),
                        #colour_create(1,1,0),
                        colour_create(0,0,0))   

  
    shape_set_transform(sky, Transform({
        'scale': {'x': 50, 'y': 50, 'z': 50},
        'translate': {'x': 0, 'y':0, 'z': 0},
        'rotate':{'vector': ('c', 0, 1 ,0),
                    'angle': 90}        
    }))              

    scene.add_shape(sky, 'nightsky')      
    
    
    ###################################
    
    image = scene.render('view')
    image.show()

           
                
    

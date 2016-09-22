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
                            ('cartesian', 2, 0, -4), ## eye point,
                            ('cartesian', 0,-18,0), ## look at
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
                            .5,
                           180)

    view = view_create_look_at(scene,
                            
                            {'left': 0,
                                'right': 300,
                                'top': 0,
                                'bottom': 300},
                            10,
                            20,
                            ('cartesian', 0, -10, -20), ## eye point,
                            ('cartesian', 0, -10, 0 ), ## look at
                            .5,
                           0)

                       
    view_set_antialias (view, True, 3,3 ,  False, False)
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
        0, -30, -30), colour_create((192.0/255.0), (83.0/255.0), (210.0/255.0))), 'light1')

    scene.add_light(light_point_light_create(cartesian_create(
        0, -4, 45), colour_create((192.0/255.0), (83.0/255.0), (210.0/255.0))), 'light2')
        
    scene.add_light(
        light_point_light_create(
            cartesian_create(0, -13, 0),
            colour_create(0, 1,0)),
            'light3'
        )
             
    ############################33
    textr = \
        MosiacTexture (
            {
            0: [(PILImageTexture("examples/rusty-iron-tileable.jpg"), .16, .6, .15, .15)],
            1: [(TiledTexture(
                    PILImageTexture("examples/stone-tileable.jpg"),
                    6.28318530, 15), 0, 0, 1, 1)]
            },
            ('colour', 1,1,1)
        )


    refl = ('colour_mapping',
            cylinder_map_to_rect,
            MosiacTexture (
                {
                0: [(PlainTexture(('colour', .8, .8, .8)),.2, .2, .15, .07)],
                1: [(PlainTexture(('colour', 0,0,0)),1,1,1,1)]
                },
                ('colour', 0,0,0)
            )
        )

    cyl = shape_cylinder_create(
        ('colour_mapping', cylinder_map_to_rect,
            textr),
        refl)
    

    shape_set_transform(cyl, Transform({
        'scale': {'x': 2, 'y': 15, 'z': 2},
        'translate': {'x': 0, 'y':-8, 'z': 0}
    }))
           
    shape_set_transparency(
        cyl, 
        ('colour_mapping',
            cylinder_map_to_rect,
            MosiacTexture (
                {
                0: [(PlainTexture(('colour', 1, 1, 1)),.2, .2, .15, .07)],
                1: [(Rotate90Texture(
                        ColourRampTexture(
                            [
                                ('colour', 0, 0, 0),
                                ('colour', .3, .3, .3),
                                ('colour', 1, 1, 1)
                            ]),
                        True
                        ), 0, 0 ,1, 1)
                    ]
                },
                ('colour', 1, 1, 1)
            )
        )
    )
    

    
    scene.add_shape(cyl, 'tower')     
    ###############################
    
    cone = shape_cone_create(
        ('colour_mapping', cone_map_to_rect,
            TiledTexture(
                PILImageTexture("examples/red-brick-tileable.jpg"),
                math.pi*9, 9
            )
        ),
        colour_create(0,0,0),
        0, 1.33)
    
    
    shape_set_transform(cone, Transform({
        'scale': {'x': 2.5, 'y': 3.2, 'z': 2.5},
        'translate': {'x': 0, 'y':-18.25, 'z': 0}
        }))

    scene.add_shape(cone, 'towerTop')
    #########################################
    disc = shape_disc_create(
        ('colour', 0,0,0),    
        ('colour', 0,0,0)
        
    )

    shape_set_transform(disc, Transform({
        'scale': {'x':2, 'y': 2.0, 'z': 1},
        'translate': {'x': 0, 'y':-11.5, 'z': 0},
        'rotate':{'vector': ('c', 1.0, 0 ,0),
                    'angle': 90}
        }))
    
    scene.add_shape(disc, 'towerInternalDisk') 
    
    ###############################

    cone = shape_cone_create(
        colour_create((192.0/512.0), (83.0/512.0), (210.0/512.0)),
        colour_create(0,0,0),
        .75, 1)

    shape_set_transparency(
        cone,
            ('colour_mapping', cone_map_to_rect,
                Rotate90Texture(
                    ColourRampTexture(
                        [
                            ('colour', 1,1,1),
                            ('colour', 0,0,0),
                            ('colour', 1,1,1)
                        ]),
                    True)
            ),        
        )

    shape_set_transform(cone, Transform({
        'scale': {'x': 50, 'y': 25, 'z': 50},
        'translate': {'x': 0, 'y':(48-25), 'z': 0},
        'rotate':{ 
            'vector': ('c', 1.0, 0 ,0),
            'angle': 180}        
        }))


    scene.add_shape(cone, 'mist');
    
    ##############################
    disc = shape_disc_create(
        ('colour_mapping', disc_map_to_rect_cookie,
            TiledTexture(
                PILImageTexture("examples/water_rippled.jpg"),
                30, 60)),
        ('colour_mapping', disc_map_to_rect_cookie,
            TiledTexture(
                PILImageTexture("examples/water_rippled_reflection.jpg"),
                1, 2))         
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
                        ('colour_mapping', 
                            sphere_map_to_rect,
                            PILImageTexture("examples/nightsky.jpeg")),
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

           
                
    

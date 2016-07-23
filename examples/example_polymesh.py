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

# Set the maths precision
get_context().precision = 32

# Create a Scene object to contain lights, views, and shapes
scene = Scene()

# Create a view. The rendered view wil be 300 x 300 pixels.
# The eye point will be at 0,0,-15. At z=0, the scene will be scanned from
# -5 to 5 on both the X and Y axis.

view = view_create(-15, 
                   {'left': 0,
                    'right': 300,
                    'top': 0,
                    'bottom': 300},
                   {'left': -5,
                    'right': 5,
                    'top': -5,
                    'bottom': 5})

# Add the view to the scene
scene.add_view(view, 'view')

# Data to define a polymesh tetrahedron. First, is a list of points in the
# polymesh. Second is a list of polygons, where each polygon is defined as a 
# list of indices of points, so [0, 1, 2, 3] is the square forming the 'base'
# of the tetrahedron. Finally, diffuse colours for each polygon in the mesh
# defined.

tetra_data = {
    'points': [cartesian_create(1, -1, -1),
               cartesian_create(1, 1, -1),
               cartesian_create(1, 1, 1),
               cartesian_create(1, -1, 1),
               cartesian_create(0, 0, 0)],

    'polygon_point_indices': [[0, 1, 2, 3],
                              [4, 0, 1],
                              [4, 1, 2],
                              [4, 2, 3],
                              [4, 3, 0]],

    'face_diffuse_colours': [colour_create(0, 1, 0),
                             colour_create(1, 1, 0),
                             colour_create(1, 0, 1),
                             colour_create(0, 1, 1),
                             colour_create(1, 0, 0)],
}

#Create a polymesh.
poly_mesh = shape_polymesh_create(tetra_data)

# Set a transformation for the polymesh. The polymesh will be scaled by 3 on
# the y-axis, and 2 on the z-axis. It will also be translated from its
# original position by 3 on the x-axis. It is also rotated 

shape_set_transform(poly_mesh,
                    Transform({
                        'scale': {'x': 2.0, 'y': 2.0, 'z': 1.0},
                        'rotate': {'vector': cartesian_create(1, 1, 0),
                                   'angle': 130},
                        'translate': {'x': 0, 'y': 0, 'z': 0}
                            }))

# Add the polymesh to the scene.

scene.add_shape(poly_mesh, 'triMesh')

# Add a point light to the scene
scene.add_light(
    light_point_light_create(
        cartesian_create(0, 0, -1.5),
        colour_create(1, 1, 1)),
        'light1')

        
# Render the scene. The returned image is in PIL format.
image = scene.render('view')

# Display the image.
image.show()

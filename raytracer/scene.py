try:
    from gmpy2 import *
except ImportError:
    from math import *
    from raytracer.mpfr_dummy import *
from raytracer.cartesian import *
from raytracer.colour import *
from raytracer.matrix import *
from raytracer.light import *
from raytracer.output import *
from raytracer.shape import *
import raytracer.view
from raytracer.view import *
from raytracer.oct_tree import *

"""A scene class is a container for shapes, lights and views. It also
contains a key piece of raytracer code, the loop for testing a ray
against each shape in the scene
"""


class Scene(object):
    def __init__(self, use_octtree = True, oct_tree_threshold = 20):
        self.__lights__ = {}
        self.__shapes__ = {}
        self.__views__ = {}
        self.__shape_count__ = 0
        self.__light_count__ = 0
        self.__view_count__ = 0
        self.__max_relfections__ = 5
        
        self.__use_octtree__ = use_octtree
        self.__oct_tree_threshold__ = oct_tree_threshold
        
    def get_max_reflections(self):
        return self.__max_relfections__

    def add_shape(self, shape, name=None):
        """Add a shape to the scene
        :param shape: the shape to add
        :param name: a text handle for the shape"""

        self.__shape_count__ += 1

        while name in self.__shapes__ or name is None:
            name = "Shape%d" % (self.__shape_count__)


        self.__shapes__[name] = shape

    def add_light(self, light, name=None):
        """Add a light to the scene
        :param light: the light to add
        :param name: a text handle for the light
        """

        self.light_count = self.__light_count__ + 1

        while name in self.__lights__ or name is None:
            name = "Light%d" % (self.light_count)
            self.light_count = self.light_count + 1

        self.__lights__[name] = light

    def get_lights(self):
        """Returns the array of lights in the scene.
        :return: an array of lights
        """
        return self.__lights__

    def add_view(self, view_obj, name=None):
        """Adds a view to the scene.
        :return: an array of lights
        :param view_obj: the view to add
        :param name: a string handle for the view
        """

        
        self.__view_count__ = self.__view_count__ + 1
  

        # Assign a handle to the view if none give
        while name in self.__views__ or name is None:
            name = "View%d" % (self.__view_count__)
            self.__view_count__ = view_count + 1

        self.__views__[name] = view_obj


    def setup_octtree(self):
        
        if self.__use_octtree__ and \
            len (self.__shapes__) >= self.__oct_tree_threshold__:                  
            
            # get bounding boxes for all shapes
            min_x = None
            min_y = None
            min_z = None
            
            max_x = None
            max_y = None
            max_z = None
            
            for shape_name in sorted(self.__shapes__):
                shape = self.__shapes__[shape_name]
                box = shape_bounding_box(shape)
                
                if box is not None:
                    if min_x is None or box.min_x < min_x:
                        min_x = box.min_x
                    if min_y is None or box.min_y < min_y:
                        min_y = box.min_y
                    if min_z is None or box.min_z < min_z:
                        min_z = box.min_z
                    
                    if max_x is None or box.max_x > max_x:
                        max_x = box.max_x
                    if max_y is None or box.max_y > max_y:
                        max_y = box.max_y
                    if max_z is None or box.max_z > max_z:
                        max_z = box.max_z                
                    
            if min_x is not None and \
                min_y is not None and \
                min_z is not None and \
                max_x is not None and \
                max_y is not None and \
                max_z is not None:

                self.__octtree_top__ =  OctTreeLeaf(
                    self, self.__oct_tree_threshold__,
                    min_x, max_x, min_y, max_y, min_z, max_z)

  
                for shape_name in sorted(self.__shapes__):
                    shape = self.__shapes__[shape_name]
                    self.__octtree_top__.add_shape(shape)
                    
                  

            else: 
                self.__octtree_top__ = None



    def render(self, view_name):
        """
        Renders the scene using the specified view. The output type must be
        set prior to calling this method.
        :param view_name: the handle of the view to use
        :return: the rendered output
        """
        
        if self.__use_octtree__ and \
            len (self.__shapes__) >= self.__oct_tree_threshold__:  
            self.setup_octtree()

                    
        raytracer.view.view_render(
            self.__views__[view_name])
            
        return (self.__views__[view_name]
                [raytracer.view.VIEW_OUTPUT].get_output())

    def replace_node(self, old_node, new_node):
         self.__octtree_top__ = new_node
          
                
    def test_intersect(self, ray, exclude_shapes=[]):
        if self.__use_octtree__ and \
            len (self.__shapes__) >= self.__oct_tree_threshold__ and \
            self.__octtree_top__ is not None:
            shapes = self.__octtree_top__.get_shapes_by_ray(ray)
        else:
            shapes = self.__shapes__
            
        return self.test_intersect_list (ray, shapes, exclude_shapes)
        
        
    def test_intersect_list(self, ray, list, exclude_shapes=[]):
        """Tests intersection of a ray with all the shapes in the scene.
        :param ray: the ray to test against the shapes
        :param exclude_shapes: a list of shapes to exclude from the
        intersection test
        """
        curr_sh = None
        curr_t = None
        curr_intersect_result = None
        for shape in self.__shapes__:

            if shape not in exclude_shapes:
                sh = self.__shapes__[shape]
                intersect_result = shape_test_intersect(sh, ray)
                if (intersect_result is not False and
                        intersect_result is not None):
                    intersect_result['shape'] = sh

                    t = intersect_result['t']
                    if t > 0 and (curr_t is None or t < curr_t):

                        curr_sh = sh
                        curr_t = t
                        curr_intersect_result = intersect_result
                        curr_intersect_result['shape'] = sh

                        if ray[RAY_ISSHADOW]:
                            return curr_intersect_result

        if curr_intersect_result is None:
            return False
        return curr_intersect_result

from gmpy2 import *
from raytracer.cartesian import *
from raytracer.colour import *
from raytracer.matrix import *
from raytracer.light import *
from raytracer.output import *
from raytracer.shape import *
import raytracer.view
from raytracer.view import *

"""A scene class is a container for shapes, lights and views. It also
contains a key piece of raytracer code, the loop for testing a ray
against each shape in the scene
"""


class Scene:
    __lights__ = {}
    __shapes__ = {}
    __views__ = {}
    __shape_count__ = 0
    __light_count__ = 0
    __view_count__ = 0
    __output__ = PIL_Output()

    def add_shape(self, shape, name=None):
        """Add a shape to the scene
        :param shape: the shape to add
        :param name: a text handle for the shape"""

        self.shape_count = self.__shape_count__ + 1

        while name in self.__shapes__ or name is None:
            name = "Shape%d" % (self.shape_count)
            self.shape_count = self.__shape_count__ + 1

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

    def render(self, view_name):
        """
        Renders the scene using the specified view. The output type must be
        set prior to calling this method.
        :param view_name: the handle of the view to use
        :return: the output of the rendered scene, or None if no output type
                 is set
        """
        if(self.__output__ is None):
            return None
        raytracer.view.view_render(
            self.__views__[view_name])
        return self.__views__[view_name][raytracer.view.VIEW_OUTPUT].get_output()

    def test_intersect(self, ray, exclude_shapes=[]):
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
                    if t > 0 and(curr_t is None or t < curr_t):

                        curr_sh = sh
                        curr_t = t
                        curr_intersect_result = intersect_result
                        curr_intersect_result['shape'] = sh

                        if ray[RAY_ISSHADOW]:
                            return curr_intersect_result

        if curr_intersect_result is None:
            return False
        return curr_intersect_result

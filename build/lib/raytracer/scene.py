import gmpy2
from gmpy2 import *
from cartesian import *
from colour import *
from matrix import *
from light import *
from output import *
from shape import *
import view

"""A scene class is a container for shapes, lights and views. It also
contains a key piece of raytracer code, the loop for testing a ray
against each shape in the scene."""


class Scene:
    lights = {}
    shapes = {}
    views = {}
    shape_count = 0
    light_count = 0
    view_count = 0
    output = PIL_Output()

    def add_shape(self, shape, name=None):
        """Add a shape to the scene
        :param shape: the shape to add
        :param name: a text handle for the shape"""
        self.shape_count = self.shape_count + 1

        while name in self.shapes or name is None:
            name = "Shape%d" % (self.shape_count)
            self.shape_count = self.shape_count + 1

        self.shapes[name] = shape

    def add_light(self, light, name=None):
        """Add a light to the scene
        :param light: the light to add
        :param name: a text handle for the light"""
        self.light_count = self.light_count + 1

        while name in self.lights or name is None:
            name = "Light%d" % (self.light_count)
            self.light_count = self.light_count + 1

        self.lights[name] = light

    def get_lights(self):
        """Returns the array of lights in the scene.
        :return: an array of lights"""
        return self.lights

    def add_view(self, view_obj, name=None):
        """Adds a view to the scene.
        :return: an array of lights
        :param view_obj: the view to add
        :param name: a string handle for the view"""

        self.view_count = self.view_count + 1

        # Assign a handle to the view if none give
        while name in self.views or name is None:
            name = "View%d" % (self.view_count)
            self.view_count = view_count + 1

        self.views[name] = view_obj

    def render(self, view_name):
        """Renders the scene using the specified view. The output type must be
        set prior to calling this method.
        :param view_name: the handle of the view to use
        :return: the output of the rendered scene, or None if no output type
                 is set
        :rtype: an instance of a child class of Output, being the same object
                passed as a paramter into set_output_type"""
        if(self.output is None):
            return None
        view.view_render(self.views[view_name], self, self.output)
        return self.output.get_output()

    def test_intersect(self, ray, exclude_shapes=[]):
        """Tests intersection of a ray with all the shapes in the scene.
        :param ray: the ray to test against the shapes
        :param exclude_shapes: a list of shapes to exclude from the
                               intersection tests"""
        curr_sh = None
        curr_t = None
        curr_intersect_result = None
        for shape in self.shapes:

            if shape not in exclude_shapes:
                sh = self.shapes[shape]
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

    def set_output_type(self, output):
        """Sets the output type for rendering the scene.
        :param output: an instance of a child class of Output"""
        if not isinstance(output, Output):
            return None

        self.output = output

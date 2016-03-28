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
        return self.lights

    def add_view(self, view_obj, name=None):

        self.view_count = self.view_count + 1

        while name in self.views or name is None:
            name = "View%d" % (self.view_count)
            self.view_count = view_count + 1

        self.views[name] = view_obj

    def render(self, view_name):

        if(self.output is None):
            return None
        view.view_render(self.views[view_name], self, self.output)
        return self.output.get_output()

    def test_intersect(self, ray, excludeShape=None):

        curr_sh = None
        curr_t = None
        curr_intersect_result = None
        for shape in self.shapes:
            # print(shape)
            sh = self.shapes[shape]
            intersect_result = shape_test_intersect(sh, ray)
            if intersect_result is not False and intersect_result is not None:
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

        if not isinstance(output, Output):
            return None

        self.output = output

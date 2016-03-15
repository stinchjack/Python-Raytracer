import gmpy2
from gmpy2 import *
from cartesian import *
from colour import *
from matrix import *
from light import *
from output import *
from shape import *
import view


class Scene:
    lights = {}
    shapes = {}
    views = {}
    shape_count = 0
    light_count = 0
    view_count = 0
    output = PIL_Output()

    def addShape(self, shape, name=None):

        self.shape_count = self.shape_count + 1

        while name in self.shapes or name == None:
            name = "Shape%d" % (self.shape_count)
            self.shape_count = self.shape_count + 1

        self.shapes[name] = shape

    def addLight(self, light, name=None):

        self.light_count = self.light_count + 1

        while name in self.lights or name == None:
            name = "Light%d" % (self.light_count)
            self.light_count = self.light_count + 1

        self.lights[name] = light

    def getLights(self):
        return self.lights

    def addView(self, view_obj, name=None):

        self.view_count = self.view_count + 1

        while name in self.views or name == None:
            name = "View%d" % (self.view_count)
            self.view_count = view_count + 1

        self.views[name] = view_obj

    def render(self, viewName):

        if (self.output == None):
            return None
        view.view_render(self.views[viewName], self, self.output)
        return self.output.getOutput()

    def testIntersect(self, ray, excludeShape=None):

        curr_sh = None
        curr_t = None
        curr_intersect_result = None
        for shape in self.shapes:
            #print (shape)
            sh = self.shapes[shape]
            intersect_result = shape_test_intersect(sh, ray)
            if intersect_result != False and intersect_result != None:
                intersect_result['shape'] = sh

                t = intersect_result['t']
                if t > 0 and (curr_t == None or t < curr_t):

                    curr_sh = sh
                    curr_t = t
                    curr_intersect_result = intersect_result
                    curr_intersect_result['shape'] = sh

                    if ray[RAY_ISSHADOW]:
                        return curr_intersect_result

        if curr_intersect_result == None:
            return False
        return curr_intersect_result

    def setOutputType(self, output):

        if not isinstance(output, Output):
            return None

        self.output = output

"""Lighting module functions.

The rationale of this module is to allow for more than one lighting model, where simpler
lighting models can be used for quicker rendering.

To do: Implement reflections
 
"""

from cartesian import *
from colour import *
from matrix import *
from light import *
from output import *
import scene
from view import *
LIGHTINGMODEL_BASIC_CALCFUNC = 2
LIGHTINGMODEL_BASIC_AMBIENT = 3
LIGHTINGMODEL_BASIC_MAXREFLECT = 4


def lightingmodel_calculate(lightingmodel, scene_obj, result):
    return lightingModel[LIGHTINGMODEL_BASIC_CALCFUNC](lightingModel, scene_obj, result)


def lightingmodel_basic_calculate(lightingmodel, scene_obj, result):
    if not type(result) is dict:
        return None
    if not isinstance(scene_obj, scene.Scene):
        return None

    result = shape_reverseTransform(result)

    if not 'point' in result:
        ray = result['ray']
        #result['point'] = ray.start+(ray.vector.scale(result['t']))
        #result['point'] = cartesian_add (ray.start, cartesian_scale(ray.vector, result['t']))
        result['point'] = ray_calc_pt(ray, result['t'])

    diffuseColour = result['shape'][
        SHAPE_DIFFUSECOLOUR_FUNC](result['shape'], result)

    end_colour = colour_mul(lightingModel[3], diffuseColour)

    lights = scene_obj.getLights()

    for l in lights:
        light = lights[l]
        #shadow_ray = Ray (light[LIGHT_POINT_POINT], Vector(result['point']-light[LIGHT_POINT_POINT]), True)

        #print ("result['point']: %s"%result['point'])
        #print ("result['normal']: %s"%result['normal'])

        # if (result['normal'].dot(result['ray'].vector)<0):
        if (cartesian_dot(result['normal'], result['ray'][RAY_VECTOR]) < 0):
            norml = result['normal']
        else:
            norml = cartesian_create(0 - result['normal'][VECTOR_X], 0 - result[
                                     'normal'][VECTOR_Y], 0 - result['normal'][VECTOR_Z])

        #norml = Vector(result['normal'])
        #sh_ray_dir = Vector(light[LIGHT_POINT_POINT]-result['point'])

        rs = cartesian_add(
            result['point'], cartesian_scale(norml, mpfr(".0001")))

        #shadow_ray = Ray (rs, Vector(light[LIGHT_POINT_POINT]-result['point']), True)
        shadow_ray = ray_create(rs, cartesian_sub(
            light[LIGHT_POINT_POINT], result['point']), True)

        #print("result['normal']: %s"%snorml)
        #print("result['point']: %s"%result['point'])

        #print ("lightingMOdelShape %s"%result['shape'])
        r = scene_obj.testIntersect(shadow_ray, result['shape'])

        if r == False:  # if not in shadow

            #light_ray = Vector((light[LIGHT_POINT_POINT] - result['point'])).normalise()
            light_ray = cartesian_normalise(cartesian_sub(
                light[LIGHT_POINT_POINT], result['point']))

            #if d<0: d= 0-d
            diff = colour_scale(
                light[LIGHT_POINT_COLOUR], cartesian_dot(light_ray, norml))

            end_colour = colour_add(
                end_colour, colour_mul(diff, diffuseColour))
            #end_colour = colour_add (end_colour, colour_mul(colour_scale(light[LIGHT_POINT_COLOUR],cartesian_dot (cartesian_normalise(cartesian_sub(light[LIGHT_POINT_POINT],result['point'])), norml)),diffuseColour ))
        # else:
        #	print (shadow_ray)
        #	exit()
    return end_colour


def lightingmodel_basic_create(ambient_light=None, max_reflect=5):
	"""Creates a tuple with data for basic lighting model.
	
	
	"""
    if ambient_light == None:
        ambient_light = colour_create(0, 0, 0)
    return ('lightingModel', 'basic', lightingmodel_basic_calculate, ambient_light, max_reflect)

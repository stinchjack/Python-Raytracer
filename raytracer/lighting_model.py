from raytracer.cartesian import *
from raytracer.colour import *
from raytracer.matrix import *
from raytracer.light import *
from raytracer.output import *
import raytracer.scene as scene
from raytracer.view import *
from raytracer.mapping import *

"""Lighting module functions.

The rationale of this module is to allow for more than one lighting model,
where simpler lighting models can be used for quicker rendering. A lighting
model tuple has the following elements:

* The string 'lighting_model' as an identifier.
* A string identifying the lighting model type, e.g. 'basic'
* A reference to the calculation function for the lighting model.
* The ambient light colour
* The maximum number of reflections
* a dictionary of optional options:
    'NoShadows': if True shadows will not be rendered
    'NoDiffuse': if True diffuse shading will not be rendered


To do: Implement reflections for the basic lighting model."""

LIGHTINGMODEL_BASIC_CALCFUNC = 2
LIGHTINGMODEL_BASIC_AMBIENT = 3
LIGHTINGMODEL_BASIC_MAXREFLECT = 4
LIGHTINGMODEL_CALCFUNC = 2
LIGHTINGMODEL_AMBIENT = 3
LIGHTINGMODEL_MAXREFLECT = 4
LIGHTINGMODEL_OPTIONS = 5


def lightingmodel_set_options(lighting_model, options={}):
    lighting_model[LIGHTINGMODEL_OPTIONS] = options


def lightingmodel_basic_calculate(lighting_model, scene_obj, result):
    """Calculates the colour where a ray intersects with an object.

    lightingmodel: a lighting model tuple.
    :param scene_obj: the Scene object
    :param result: the intersection test results
    :return: a tuple of colour information

    To do: Implement reflections. """
    
    if not type(result) is dict:
        return None
    if not isinstance(scene_obj, scene.Scene):
        return None

    result = shape_reverse_transform(result)

    if 'point' not in result:
        ray = result['ray']

        result['point'] = ray_calc_pt(ray, result['t'])

    if result['shape'][SHAPE_DIFFUSECOLOUR_FUNC] is not None:
        diffuse = result['shape'][
            SHAPE_DIFFUSECOLOUR_FUNC](result['shape'], result)
    else:
        diffuse = shape_diffuse_colour(result['shape'], result)

    diffuse_colour = get_colour_from_mapping(diffuse, result)

    doReflections = ('NoReflections' not in
        lighting_model[LIGHTINGMODEL_OPTIONS] or
        ('NoReflections' in lighting_model[LIGHTINGMODEL_OPTIONS] and
        lighting_model[LIGHTINGMODEL_OPTIONS]['NoShadows'] is False))
        
           
    if (doReflections):
        if result['shape'][SHAPE_SPECULARCOLOUR_FUNC] is not None:
            specular = result['shape'][
                SHAPE_SPECULARCOLOUR_FUNC](result['shape'], result)
        else:
            specular = shape_specular_colour(result['shape'], result)
    
        specular_colour = get_colour_from_mapping(specular, result)
    
        if specular_colour[1] <= 0 and \
            specular_colour[2] <= 0 and \
            specular_colour[3] <= 0:
                doReflections = False
             
    if (doReflections):
        reflect_result =  scene_obj.test_intersect (ray, [])
        
        if reflect_result is False:
            doReflections = False

    if (doReflections):
        if 'reflect_count' not in result:
            reflect_result['reflect_count'] = scene_obj.get_max_reflections()
        else:
            reflect_result['reflect_count'] -= 1;
        
        if reflect_result['reflect_count'] <= 0:
           doReflections = False    
    
    if (doReflections):    
        reflect_colour = lightingmodel_basic_calculate(lighting_model, scene_obj, reflect_result)

    
    end_colour = lighting_model[LIGHTINGMODEL_AMBIENT]

    lights = scene_obj.get_lights()

    for l in lights:
        light = lights[l]

        if(cartesian_dot(result['normal'], result['ray'][RAY_VECTOR]) < 0):
            norml = result['normal']
        else:
            norml = cartesian_create(0 - result['normal'][VECTOR_X],
                                     0 - result['normal'][VECTOR_Y],
                                     0 - result['normal'][VECTOR_Z])

        rs = cartesian_add(
            result['point'], cartesian_scale(norml, mpfr(".0001")))

        shadow_ray = ray_create(rs, cartesian_sub(
            light[LIGHT_POINT_POINT], result['point']), True)

        if ('NoShadows' in lighting_model[LIGHTINGMODEL_OPTIONS] and
                lighting_model[LIGHTINGMODEL_OPTIONS]['NoShadows'] is True):
            r = False
        else:
            r = scene_obj.test_intersect(shadow_ray, result['shape'])

        if r is False:  # if not in shadow

            light_ray = cartesian_normalise(cartesian_sub(
                light[LIGHT_POINT_POINT], result['point']))

            diff = colour_scale(
                light[LIGHT_POINT_COLOUR], cartesian_dot(light_ray, norml))

            if ('NoDiffuse' in lighting_model[LIGHTINGMODEL_OPTIONS] and
                    lighting_model[LIGHTINGMODEL_OPTIONS]['NoDiffuse']):
                end_colour = colour_add(
                    end_colour, colour_scale(diffuse_colour, mpfr(0.5)))
            else:
              
                end_colour = colour_add(
                    end_colour, colour_mul(diffuse_colour, diff))
                    
    return end_colour


def lightingmodel_basic_create(
        ambient_light=None, max_reflect=5, lighting_model_options={}):
    """Creates a tuple with data for basic lighting model.

    :param ambient_light: The colour of the ambient light to apply
    :param max_reflect: the maximum number of recursive reflections
                        to allow

    Returns: a lighting model tuple"""

    if ambient_light is None:
        ambient_light = colour_create(0, 0, 0)
    return['lighting_model', 'basic', lightingmodel_basic_calculate,
           ambient_light, max_reflect, lighting_model_options]

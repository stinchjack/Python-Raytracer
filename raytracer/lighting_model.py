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

To do: Implement reflections for the basic lighting model."""

LIGHTINGMODEL_BASIC_CALCFUNC = 2
LIGHTINGMODEL_BASIC_AMBIENT = 3
LIGHTINGMODEL_BASIC_MAXREFLECT = 4

LIGHTINGMODEL_NOSHADOWS = 1
LIGHTINGMODEL_NODIFFUSE = 2


def lightingmodel_calculate(lighting_model, scene_obj, result):
    return lighting_model[LIGHTINGMODEL_BASIC_CALCFUNC](lighting_model,
                                                        scene_obj, result,
                                                        lightingmodel_flags=0)


def lightingmodel_basic_calculate(lighting_model, scene_obj, result,
                                  lightingmodel_flags=0):
    """Calculates the colour where a ray intersects with an object.

    lightingmodel: a lighting model tuple.
    :param scene_obj: the Scene object
    :param result: the intersection test results
    :param lightingmodel_flags: Flags that affect behaviour of the lighting
    model:
    * LIGHTINGMODEL_NOSHADOWS: do not render shadows
    * LIGHTINGMODEL_NODIFFUSE: do not calucalte diffuse lighting

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

    end_colour = lighting_model[LIGHTINGMODEL_BASIC_AMBIENT]

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

        if (LIGHTINGMODEL_NOSHADOWS & lightingmodel_flags > 0):
            r = False
        else:
            r = scene_obj.test_intersect(shadow_ray, result['shape'])

        if r is False:  # if not in shadow

            light_ray = cartesian_normalise(cartesian_sub(
                light[LIGHT_POINT_POINT], result['point']))

            diff = colour_scale(
                light[LIGHT_POINT_COLOUR], cartesian_dot(light_ray, norml))

            if (LIGHTINGMODEL_NODIFFUSE & lightingmodel_flags > 0):
                end_colour = colour_add
                (end_colour, colour_scale(diffuse_colour, mpfr(0.5)))
            else:
                end_colour = colour_add(
                    end_colour, colour_mul(diff, diffuse_colour))

    return end_colour


def lightingmodel_basic_create(ambient_light=None, max_reflect=5):
    """Creates a tuple with data for basic lighting model.

    :param ambient_light: The colour of the ambient light to apply
    :param max_reflect: the maximum number of recrusive reflections
                        to allow

    Returns: a lighting model tuple"""

    if ambient_light is None:
        ambient_light = colour_create(0, 0, 0)
    return('lighting_model', 'basic', lightingmodel_basic_calculate,
           ambient_light, max_reflect)

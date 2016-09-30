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
    if 'NormalOffset' not in options:
        options['NormalOffset'] = mpfr(".0001")
    
    lighting_model[LIGHTINGMODEL_OPTIONS] = options


def lightingmodel_basic_calculate(lighting_model, scene_obj, result):
    """Calculates the colour where a ray intersects with an object.

    lightingmodel: a lighting model tuple.
    :param scene_obj: the Scene object
    :param result: the intersection test results
    :return: a tuple of colour information
     """
    # import pdb; pdb.set_trace();
    
    if not type(result) is dict:
        return None
    if not isinstance(scene_obj, scene.Scene):
        return None

    # type checking
    end_colour = lighting_model[LIGHTINGMODEL_AMBIENT]

    #convert result into scene co-ordinates
    result = shape_reverse_transform(result)


    if cartesian_dot (result['ray'][RAY_DIR], result['normal']) < 0:
        shift = lighting_model[LIGHTINGMODEL_OPTIONS]['NormalOffset']
        # result['normal'] = cartesian_sub(('c',0,0,0), result['normal'])
    else:

        shift = mpfr(0) - lighting_model[LIGHTINGMODEL_OPTIONS]['NormalOffset']
    
    if not 'point' in result:
        result['point'] = ray_calc_pt(result['ray'], result['t'] )
    
    rs = cartesian_add(
        result['point'], cartesian_scale(result['normal'], shift))

    reflected_colour = \
        lightingmodel_basic_reflections(lighting_model, scene_obj, result, rs)

    if reflected_colour is not None:
        end_colour = colour_add(end_colour, reflected_colour)



    lights = scene_obj.get_lights()


    diffuse_colour = shape_get_colour(result, SHAPE_DIFFUSECOLOUR)
    diffuse_colour_total = ('colour', 0, 0, 0)

    result['shifted_point'] =rs
    for l in lights:
        light = lights[l]
        
        light_calc_info = light[LIGHT_CALCINFO_FUNC] (light, result)

        if not light_calc_info['is_inside']:
            continue
        
            
        #shadow calculation
        shadow_factor = ('colour', 0, 0, 0)
        has_shadow = False
        if ('NoShadows' in lighting_model[LIGHTINGMODEL_OPTIONS] and
                lighting_model[LIGHTINGMODEL_OPTIONS]['NoShadows'] is True):
            r = False
        else:
            #import pdb; pdb.set_trace();
            
            has_shadow = False
            in_complete_shadow = False
            
            
            shadow_count_scale = (mpfr(1.0) / 
                len (light_calc_info['shadow_vectors']))
            shadow_factor = ('colour', 0, 0, 0)
            
            import pdb; pdb.set_trace();
            
            for shadow_vector in light_calc_info['shadow_vectors']:

                shadow_ray = ray_create(rs, shadow_vector, True)            
                shadow_result = scene_obj.test_intersect(shadow_ray)
                
                shadow_transparency = \
                    colour_scale (
                        lightingmodel_basic_shadow_ray_transparency (                
                            lighting_model,
                            shadow_result),
                        shadow_count_scale 
                        )
                
                #shadow_transparency = ('colour',1,1,1)
                
                shadow_factor = \
                    colour_add (
                        shadow_factor,
                        shadow_transparency
                    )
        
        in_complete_shadow = (
            shadow_factor[1] <=0 and
            shadow_factor[2] <=0 and 
            shadow_factor[3] <=0)

        has_shadow =  (
            shadow_factor[1] <1.0 and
            shadow_factor[2] <1.0 and 
            shadow_factor[3] <1.0)

        if not has_shadow:
            in_complete_shadow = False


        #diffuse calucation
        if not in_complete_shadow:
            # shadow_factor = ('colour' ,0,0,0)
            diffuse_colour_total = colour_add(
                diffuse_colour_total,
                lightingmodel_basic_calc_diffuse (
                    lighting_model, scene_obj,
                    result, shift, shadow_factor, light,
                    light_calc_info,
                    diffuse_colour, has_shadow)
                )

    diffuse_transparency_results = \
             lightingmodel_basic_transparency_diffuse(
                lighting_model, scene_obj, result
            ) 
    if diffuse_transparency_results is not None:
        diffuse_transparency_effect = diffuse_transparency_results[0]
        transparency_colour_inv = diffuse_transparency_results[1] 
        end_colour = \
            colour_add(
                end_colour,
                diffuse_transparency_effect
            )

        # apply transparency effect to diffuse colour                    
        diffuse_colour_total = colour_mul (
                diffuse_colour_total,
                transparency_colour_inv
            )

    end_colour = colour_add(
            end_colour, diffuse_colour_total)
    
        
    # Sanity check    
    if end_colour[1] < 0 or end_colour[2] <0  or end_colour[3] < 0:

        ec = [None, None, None, None]        
        for i in range (1,4):
            if end_colour[i] < 0:
                ec[i] = 0
            else:
                ec[i] = end_colour[i]

        end_colour = ('colour', ec[1], ec[2], ec[3]); 
                        
                    
    return end_colour

def lightingmodel_basic_shadow_ray_transparency (lighting_model, shadow_result):
    
    if type(shadow_result) is False or (
            't' in shadow_result and
         shadow_result['t'] > 1.0):
        return ('colour', 1,1,1)


    all_shadow_results = {shadow_result['t']: shadow_result}

    if 'all_results' in shadow_result:
        all_shadow_results.update(shadow_result['all_results'])
        del (shadow_result['all_results'])

    this_shadow_rays_factor  = \
            ('colour', 1,1,1)
    for result_key in sorted(all_shadow_results.keys()):
        shadow_result_item = \
                all_shadow_results[result_key]

        this_transparency_shadow_factor  = \
            ('colour', 1.0, 1.0, 1.0)

        if shadow_result_item['t'] <= 1:


            shadow_result_item_transparency_colour = \
                    shape_get_colour(
                        shadow_result_item,
                        'transparency'
                    )

            this_transparency_shadow_factor = \
                    colour_mul(
                        this_transparency_shadow_factor,
                        shadow_result_item_transparency_colour
                    )

        this_shadow_rays_factor = \
            colour_mul (
                this_shadow_rays_factor,
                this_transparency_shadow_factor
            )

        if (this_shadow_rays_factor[1] <= 0 and 
                this_shadow_rays_factor[2] <= 0 and 
                this_shadow_rays_factor[3] <= 0):
            break
    
    return this_shadow_rays_factor

         
def lightingmodel_basic_transparency_diffuse(lighting_model, scene_obj, result):
    
    doTransparency = True
    
    if not 'all_results' in result or len(result['all_results']) == 0:
        doTransparency = False

    if doTransparency:
        
        transparency_colour = shape_get_colour(result, 'transparency')
        
        if transparency_colour is None or \
            (transparency_colour[1] <= 0 and \
            transparency_colour[2] <= 0 and \
            transparency_colour[3] <= 0):
            doTransparency = False
    
    else:
        return None

    if doTransparency:
 
        next_result_t = sorted(result['all_results'].keys()).pop(0)
        next_result = result['all_results'][next_result_t]
        del (result['all_results'][next_result_t])
        next_result['all_results'] = result['all_results']
        next_result_colour = lightingmodel_basic_calculate(
            lighting_model, scene_obj, next_result)
        transparency_colour_inv = ('colour',
            1.0 - transparency_colour[1],
            1.0 - transparency_colour[2],
            1.0 - transparency_colour[3])   
       
        return (
            colour_mul(next_result_colour, transparency_colour),
            ('colour',
                1.0 - transparency_colour[1],
                1.0 - transparency_colour[2],
                1.0 - transparency_colour[3]))
            
    else:
        return None            
                      

def lightingmodel_basic_calc_diffuse (
                    lighting_model, scene_obj,
                    result, shift, shadow_factor, light,
                    light_calc_info,
                    diffuse_colour, has_shadow):

    if ('NoDiffuse' in lighting_model[LIGHTINGMODEL_OPTIONS] and
            lighting_model[LIGHTINGMODEL_OPTIONS]['NoDiffuse']):
        return colour_scale(diffuse_colour, mpfr(0.5))
    else:
        

        
        light_ray = cartesian_normalise(light_calc_info['light_direction'])
 

        costh = cartesian_dot(light_ray, result['normal'])
        if shift < 0: 
            costh = 0 - costh
        if costh >= 0:
            diff = colour_scale(
                light[LIGHT_COLOUR],
                costh)
            this_light_diffuse_colour = colour_mul(diffuse_colour, diff)

            if has_shadow:
                this_light_diffuse_colour = \
                    colour_mul(
                        this_light_diffuse_colour,
                        shadow_factor
                    )
            return this_light_diffuse_colour
        else:
            return ('colour', 0, 0, 0)


def lightingmodel_basic_reflections(lighting_model, scene_obj, result, rs):
    # work out reflection, if any
    doReflections = ('NoReflections' not in 
            lighting_model[LIGHTINGMODEL_OPTIONS] or
        ('NoReflections' in lighting_model[LIGHTINGMODEL_OPTIONS] and
        lighting_model[LIGHTINGMODEL_OPTIONS]['NoReflections'] is False))
        
    if (doReflections):
        
        if 'reflect_count' not in result:
            result['reflect_count'] = scene_obj.get_max_reflections()
        else:
            result['reflect_count'] = result['reflect_count'] - 1;

        if result['reflect_count'] <= 0:
           doReflections = False  
           
    if (doReflections):
    
        specular_colour = shape_get_colour(result, SHAPE_SPECULARCOLOUR)
    
        if specular_colour[1] <= 0 and \
            specular_colour[2] <= 0 and \
            specular_colour[3] <= 0:
            doReflections = False   
             
    if (doReflections):
        reflected_dir = ray_reflect_vector(result['ray'], result['normal'])
        reflected_ray = ('ray', rs, reflected_dir, False)     
        reflect_result = scene_obj.test_intersect (reflected_ray, [])
           
        
        if reflect_result is False:
            doReflections = False

    if (doReflections):
        reflect_result['ray'] = reflected_ray
        reflect_result['reflect_count'] = result['reflect_count']
        reflect_colour = lightingmodel_basic_calculate(
           lighting_model, scene_obj, reflect_result)
        
        return colour_mul(reflect_colour, specular_colour)
    
    return None


def lightingmodel_basic_create(
        ambient_light=None, max_reflect=5, lighting_model_options={}):
    """Creates a tuple with data for basic lighting model.

    :param ambient_light: The colour of the ambient light to apply
    :param max_reflect: the maximum number of recursive reflections
                        to allow

    Returns: a lighting model tuple"""


    if ambient_light is None:
        ambient_light = colour_create(0, 0, 0)
        
        
    model = ['lighting_model', 'basic', lightingmodel_basic_calculate,
           ambient_light, max_reflect, None]
 
    lightingmodel_set_options(model, lighting_model_options)
    
    
    
    return model

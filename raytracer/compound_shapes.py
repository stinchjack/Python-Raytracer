from raytracer.cartesian import *
from raytracer.colour import *
from raytracer.matrix import *
from raytracer.transformation import *
from raytracer.shape import *


def shape_create_add (tuple1, tuple2, transform = None):
      
    
    shape = shape_empty_shape()
    shape[SHAPE_SHAPE] = 'sphere'
    
    shape[SHAPE_DIFFUSECOLOUR] = ('colour', 0, 0, 0)
    shape[SHAPE_SPECULARCOLOUR] = ('colour', 0, 0, 0)
    shape[SHAPE_INTERSECT_FUNC] = shape_add_intersect
    shape[SHAPE_INSIDE_FUNC] = shape_add_is_inside
    
    shape_set_transform(shape, transform)
    
    shape[SHAPE_DATA]['subshapes'] = [tuple1, tuple2]

    min_x = None
    max_x = None
    min_y = None
    max_y = None
    min_z = None
    max_z = None
    
    for subshape in shape[SHAPE_DATA]['subshapes']:
        subshape_bbox = shape_bounding_box (subshape)
        
        if min_x is None or subshape_bbox.min_x < min_x:
            min_x = subshape_bbox.min_x
        if min_y is None or subshape_bbox.min_y < min_y:
            min_y = subshape_bbox.min_y
        if min_z is None or subshape_bbox.min_z < min_z:
            min_z = subshape_bbox.min_z            

        if max_x is None or subshape_bbox.max_x > max_x:
            max_x = subshape_bbox.max_x
        if max_y is None or subshape_bbox.max_y > max_y:
            max_y = subshape_bbox.max_y
        if max_z is None or subshape_bbox.max_z > max_z:
            max_z = subshape_bbox.max_y 

    shape[SHAPE_BOUNDING_BOX_SHAPESPACE] = BoundingBox (
        min_x, max_x, min_y, max_y, min_z, max_z)
        
    
    return shape


def shape_add_intersect(shape, ray):
    
    results = {}
    
    for subshape, transform in shape[SHAPE_DATA]['subshapes']:
        
        ray_trans = transform.transform(ray)
        subshape_result = subshape[SHAPE_INTERSECT_FUNC](subshape, ray_trans)
        if subshape_result is not False:
           
           results[subshape_result['t']] = subshape_result
           if 'all_shapes' in subshape_result:
               results.update(subshape_result['all_shapes'])
               del (subshape_result['all_shapes'])
 
    if len(results) == 0:
        return False

    final_t = sorted(results.keys()).pop(0)
    

    result = results[final_t]
    del(results[final_t])
    result['all_results'] = results
    
    
    return result           

    
    
def shape_add_is_inside(shape, shape_space_point):

    
    for subshape, transform in shape[SHAPE_DATA]['subshapes']:
        sub_is_inside = shape_is_inside (subshape, shape_space_point)
        if sub_is_inside is True:
            return True
    
    return False

def shape_create_union (tuple1, tuple2, transform = None):
    
   
    
    shape = shape_empty_shape()
    shape[SHAPE_SHAPE] = 'sphere'
    
    shape[SHAPE_DIFFUSECOLOUR] = ('colour', 0, 0, 0)
    shape[SHAPE_SPECULARCOLOUR] = ('colour', 0, 0, 0)
    shape[SHAPE_INTERSECT_FUNC] = shape_union_intersect
    shape[SHAPE_INSIDE_FUNC] = shape_union_is_inside
    
    shape_set_transform(shape, transform)
    
    shape[SHAPE_DATA]['subshapes'] = [tuple1, tuple2]
    
    bbox1 = shape_bounding_box(tuple1[0])
    bbox2 = shape_bounding_box(tuple1[1])    

    max_x = min([bbox1.max_x, bbox2.max_x])
    max_y = min([bbox1.max_y, bbox2.max_y])
    max_z = min([bbox1.max_z, bbox2.max_z])

    min_x = max([bbox1.min_x, bbox2.min_x])
    min_y = max([bbox1.min_y, bbox2.min_y])
    min_z = max([bbox1.min_z, bbox2.min_z])  


    shape[SHAPE_BOUNDING_BOX_SHAPESPACE] = BoundingBox (
        min_x, max_x, min_y, max_y, min_z, max_z)
        
    return shape

def shape_union_is_inside(shape, shape_space_point):
    
    for subshape, transform in shape[SHAPE_DATA]['subshapes']:
        sub_is_inside = shape_is_inside (subshape, shape_space_point)
        if sub_is_inside is False or sub_is_inside is None:
            return False
    
    return True

def shape_union_intersect(shape, ray):

    
    sh1 = shape[SHAPE_DATA]['subshapes'][0][0]
    sh2 = shape[SHAPE_DATA]['subshapes'][1][0]   

    tr1 = shape[SHAPE_DATA]['subshapes'][0][1]
    tr2 = shape[SHAPE_DATA]['subshapes'][1][1]
   
    ray_tr1 = tr1.transform(ray)
    sh1_result = sh1[SHAPE_INTERSECT_FUNC](subshape, ray_tr1)
    
    if sh1_result is False:
        return False
    
    ray_tr2 = tr2.transform(ray)
    sh2_result = sh2[SHAPE_INTERSECT_FUNC](subshape, ray_tr2)
    if sh2_result is False:
        return False    
    
        
    results = {}
    
    if 'all_results' in sh1_result:
        sh1_all = sh1_result['all_results']
        del sh1_result['all_results']
        sh1_all[sh1_result['t']] = sh1_result
    
    if 'all_results' in sh2_result:
        sh2_all = sh2_result['all_results']
        del sh1_result['all_results']
        sh2_all[sh2_result['t']] = sh2_result
        
    for result in sh1_result:
        point = ray_calc_pt(ray, result[t])
        if shape_is_inside(sh2, point):
            results[result['t']] = result
    
    for result in sh2_result:
        point = ray_calc_pt(ray, result[t])
        if shape_is_inside(sh1, point):
            results[result['t']] = result

    if len(results) == 0:
        return False

    final_t = sorted(results.keys()).pop(0)
    
    result = results[final_t]
    del(results[final_t])
    result['all_results'] = results
    
    return result  
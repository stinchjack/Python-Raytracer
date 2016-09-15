import math
try:
    from gmpy2 import *
except ImportError:
    from raytracer.mpfr_dummy import *
from raytracer.cartesian import *
from raytracer.colour import *
from PIL import Image
from raytracer.planarshapes import shape_triangle_barycentric_coords


"""
Basic classes and functions for texture mapping.

Todo:
    * Implement Uv mapping for cones, triangles, squares, discs.
    * Add feature to texture class so it can be rotated, flipped, and tiled
    * Add further patterns e.g. ColorRamp, ColourBands
    * Add more documentation
"""

def get_colour_from_mapping(colour_mapping, intersect_result):
    """
        Returns a colour from a Texture object. If a colour_mapping is a
        colour tuple, then the colour tuple will be returned

            :param colour_mapping: a colour mapping tuple or colour tuple
            :param intersect_result: an intersection result dictionary
    """
    if colour_mapping is None:
        return ('colour', 0, 0, 0)

    if 'colour' in colour_mapping:
        return colour_mapping

    if 'colour_mapping' not in colour_mapping:
        return None

    uv_pair = colour_mapping[1](intersect_result)
    return colour_mapping[2].colour(uv_pair)

class Texture:
    """ Base class for all textures"""

    def colour(self, uv_tuple):
        """
        Calculates a colour from a UV tuple
                :param uv_tuple: a tuple with a UV pair to generate a
                                 texture from
        """
        return None


class CircularRampTexture(Texture):
    """ A texture of concentric blended colours
    """

    def __init__(self, colour_array):
        """
        Class constructor

                :param colour_array: an array of colour tuples
        """
        self.__colour_array__ = colour_array
        self.__colour_dist__ = 1.0 / mpfr(len(self.__colour_array__) - 1)
        self.___point707__ = sqrt(.5)

    def colour(self, uv_tuple):

        dist = sqrt((uv_tuple[0] - 0.5) *
                    (uv_tuple[0] - 0.5) +
                    (uv_tuple[1] - 0.5) *
                    (uv_tuple[1] - 0.5)) / self.___point707__

        i = int(math.trunc(dist / self.__colour_dist__))

        if i >= (len(self.__colour_array__) - 1):
            i = i - 1

        clr1 = self.__colour_array__[i]
        clr2 = self.__colour_array__[i + 1]

        p1 = (dist / self.__colour_dist__) - i

        return colour_add(colour_scale(clr1, 1 - p1), colour_scale(clr2, p1))

class ColourBandsTexture(Texture):

    def __init__(self, colour_array):
        self.colour_array = colour_array
        self.band_width = mpfr(1.0)/len(colour_array)
        
    def colour(self, uv_tuple):    
        return self.bands[int(u/self.band_width)]


class ColourRampTexture(Texture):

    def __init__(self, colour_array):
        self.colour_array = colour_array
        self.band_width = mpfr(1.0)/(len(colour_array)-1)
        
    def colour(self, uv_tuple):
        
        band1 = int(u/self.band_width)
        band2 = int(u/self.band_width) + 1
        
        proportion = (u - (band1 - self.band_width)) / self.band_width
        
        return colour_add (
            colour_scale(self.band[band1], proportion),
            colour_scale(self.band[band2], 1.0 - proportion))
        
        
class TiledTexture(Texture):
    def __init__(self, texture, u_repeat, v_repeat):
        self.texture = texture
        self.u_repeat = u_repeat
        self.v_repeat = v_repeat
        self.u_size =  1.0 / u_repeat
        self.v_size =  1.0 / v_repeat
        
    def colour(self, uv_tuple):
    
        u_pos = (uv_tuple[0] - (int(uv_tuple[0] / self.u_size) * self.u_size )) / self.u_size
        v_pos = (uv_tuple[1] - (int(uv_tuple[1] / self.v_size) * self.v_size )) / self.v_size
        
        return self.texture.colour((u_pos, v_pos))

class FlipTexture(Texture):
    def __init__(self, texture, flip_u, flip_v):
        self.texture = texture
        self.flip_u = flip_u
        self.flip_v = flip_v
    
    def colour(self, uv_tuple):
        
        if self.flip_u:
            u = mpfr(1.0 - uv_tuple[0])
        else:
            u = uv_tuple[0]

        if self.flip_u:
            v = mpfr(1.0 - uv_tuple[1])
        else:
            v = uv_tuple[1]
        
        return self.texture.colour((u, v))
    
class Rotate90Texture(Texture):
    def __init__(self, texture, left = False):
        self.texture = texture
        self.left = left
    
    def colour(self, uv_tuple):
        if self.left:
            v = 1.0 - uv_tuple[0]
            u = uv_tuple[1]
            
        else:
            v =  uv_tuple[0]
            u = 1.0 - uv_tuple[1]

        return self.texture.colour((v, u))

class MosiacTexture (Texture):
    """
        {layer: [(Texture, u_offset, v_offset, u_scale, v_scale)], etc}
        
        layer: 0 = top
    
    """
    def __init__(self, mosiac_data, default_colour):
        self.default_colour = default_colour
        self.ordered_layers = sorted(list(mosiac_data))
        
        mosiac = {}

        for layer_index in self.ordered_layers:
            layer = mosiac_data[layer_index]
            processed_layer = []
            for mosiac_item in layer:
                processed_layer.append ({
                    'texture': mosiac_item[0],
                    'u_min': mosiac_item[1],
                    'u_max': mosiac_item[1] + mosiac_item[3],
                    'v_min': mosiac_item[2],
                    'v_max': mosiac_item[2] + mosiac_item[4],                
                    'u_scale': mosiac_item[3],
                    'v_scale': mosiac_item[4]
                })
            
            mosiac[layer_index] = processed_layer
        
        self.mosiac = mosiac
       
    def colour(self, uv_tuple):
       u = uv_tuple[0]
       v = uv_tuple[1]
        
       for layer_index in self.ordered_layers:
            layer = self.mosiac[layer_index]   
            for item in layer:
                
                if u <= item['u_max'] and v <= item['v_max'] and \
                    u >= item['u_min'] and v >= item['v_min']:
                        
                        u = (u - item['u_min'])/ item['u_scale']
                        v = (v - item['v_min'])/ item['v_scale']   
                       
                        
                        return item['texture'].colour((u,v))
                        
       return self.default_colour 
    
    
class BandedSprialTexture(Texture):
    """ A texture of spirally banded colours
    """

    def __init__(self, colour_array, twists=5):
        """
        Class constructor
                :param colour_array: an array of colour tuples
                :param twists: the number of times each colour spirals
                               from the centre to the edge

        """
        self.__colour_array__ = colour_array

        self.___point707__ = sqrt(.5)
        self.__twists__ = twists
        self.__twist_width__ = 1.0 / mpfr(twists)
        self.__band_width__ = self.__twist_width__ / len(colour_array)

    def colour(self, uv_tuple):

        u = (uv_tuple[0] * 2.0) - 1.0
        v = (uv_tuple[1] * 2.0) - 1.0

        dist = sqrt((u * u) + (v * v))

        y_from_ctr = v

        if dist != 0:
            x_on_circ = (u / dist)
        else:
            x_on_circ = 0

        angle = degrees(acos(x_on_circ))

        if y_from_ctr < 0:
            angle = 90 + (90 - angle)
        else:
            angle = 180 + angle

        dist = dist * self.___point707__

        twist = math.trunc(dist / self.__twist_width__)
        if twist > (self.__twists__ - 1):
            twist = (self.__twists__ - 1)

        pos_in_twist = (dist - (twist * self.__twist_width__))
        pos_in_twist = pos_in_twist - ((angle / 360.0) * self.__twist_width__)

        band = pos_in_twist / self.__band_width__
        if band < 0:
            band = len(self.__colour_array__) + band

        return self.__colour_array__[int(math.trunc(band))]


class PILImageTexture(Texture):
    """
    Class for holding a PIL image as a texture
    """

    def __init__(self, filename):
        """
        Class constructor
                :param filename: the path of the image file to use

        """

        self.__image__ = Image.open(filename)
        self.__pixels__ = None;

    def colour(self, uv_tuple):

        u = uv_tuple[0]
        v = uv_tuple[1]

        if u > 1:
            u = 1
        if v > 1:
            v = 1
        if u < 0:
            u = 0
        if v < 0:
            v = 0

        x = int(u * self.__image__.width) - 1
        y = int(v * self.__image__.height) - 1

        if x < 0:
            x = 0
        if y < 0:
            y = 0

        if self.__pixels__ == None:
            self.__pixels__ = self.__image__.load()
        clr = self.__pixels__[x, y]

        return ('colour', clr[0] / 255.0, clr[1] / 255.0, clr[2] / 255.0)


def sphere_map_to_rect(intersect_result):
    """
    Maps an intersection result for a sphere to a UV pair.
            :return: tuple (u, v)
            :param intersect_result: the intersection result dictionary
    """
    p = intersect_result['raw_point']

    radius = sqrt((p[1] * p[1]) + (p[3] * p[3]))

    if (radius == 0):
        return (0, 0)

    x = p[1] / radius

    if x < -1:
        x = -1
    if x > 1:
        x = 1

    a1 = math.degrees(asin(x))
    a1 = a1 + 90

    if (p[3] >= 0):
        a1 = 180 + (180 - a1)

    u = a1 / mpfr(360.0)
    if p[2] > 1: a2 = 90
    elif p[2] < -1: a2 =-90
    else:  
        a2 = math.degrees(asin(p[2]))
        
    a2 = a2 + 90

    v = a2 / mpfr(180.0)

    return (u, v)


def cylinder_map_to_rect(intersect_result):
    """
    Maps an intersection result for a cylinder to a UV pair.
            :return: tuple (u, v)
            :param intersect_result: the intersection result dictionary
    """
    p = intersect_result['raw_point']

    x = p[1]

    if x < -1:
        x = -1
    if x > 1:
        x = 1

    a1 = math.degrees(asin(x))
    a1 = a1 + 90
    if (p[3] >= 0):
        a1 = 180 + (180 - a1)

    u = a1 / mpfr(360.0)
    v = (p[2]) + 0.5

    return (u, v)

def cone_map_to_rect(intersect_result):
    """
    Maps an intersection result for a cylinder to a UV pair.

            :return: tuple (u, v)
            :param intersect_result: the intersection result dictionary
    """
    p = intersect_result['raw_point']
    p[2] = 0
    p = cartesian_normalise(p)

    x = p[1]

    if x < -1:
        x = -1
    if x > 1:
        x = 1

    a1 = math.degrees(asin(x))
    a1 = a1 + 90
    if (p[3] >= 0):
        a1 = 180 + (180 - a1)

    u = a1 / mpfr(360.0)
    v = (p[2] - shape[SHAPE_DATA]['y_top']) / shape[SHAPE_DATA]['y_height']

    return (u, v)

def disc_map_to_rect_cookie (intersect_result):
    """
    Maps an intersection result for a disc to a UV pair.

            :return: tuple (u, v)
            :param intersect_result: the intersection result dictionary
    """

    p = intersect_result['raw_point']

    return (
        (p[1] + 1.0) / 2.0,
        (p[2] + 1.0) / 2.0)

def disc_map_to_rect (intersect_result):
    """
    Maps an intersection result for a disc to a UV pair.

            :return: tuple (u, v)
            :param intersect_result: the intersection result dictionary
    """
    p = intersect_result['raw_point']
    radius = sqrt((p[1] * p[1]) + (p[2] * p[2]))

    angle = math.degrees(acos(p[1]))
    if p[2] < 1.0:
        angle = 180 + math.degrees(0 - acos(p[1]))
    else:
        math.degrees(acos(p[1]))

    return (radius, angle / 360.0)

def rectangle_map_to_rect (intersect_result):
    rect = intersect_result['shape'][SHAPE_DATA]
    width = rect['right'] - rect['left']
    height  = rect['top'] - rect['bottom']
    p = intersect_result['raw_point']
    u = (p[1] - rect['left']) / width
    v = (p[2] - rect['top']) / height
    return (u, v)

def polygon_map_to_rect (intersect_result):
    p2d = shape_polygon_convert2d(
        intersect_result['shape'], intersect_result['raw_point'])
    
    u = (p2d[0] - rect['left']) / rect['width']
    v = (p2d[1] - rect['top']) / rect['height']
    return (u, v)    

def triangle_map_to_rect_cookie (intersect_result):
    p2d = shape_triangle_convert2d(
        intersect_result['shape'], intersect_result['raw_point'])
    
    u = (p2d[0]- shape[SHAPE_DATA]['p2_bounds'][0]['min']) / \
        shape[SHAPE_DATA]['p2_bounds'][0]['size']
        
    v = (p2d[1]- shape[SHAPE_DATA]['p2_bounds'][1]['min']) / \
        shape[SHAPE_DATA]['p2_bounds'][1]['size']
    
    return (u,v)

def triangle_map_to_rect (intersect_result):
    
    if not 'raw_point' in intersect_result:
        intersect_result['raw_point'] = \
            ray_calc_pt (intersect_result['ray'] , intersect_result['t'])
    
    coords = shape_triangle_barycentric_coords(
        intersect_result['shape'],
        intersect_result['raw_point'])
    
    return (coords[0], coords[1])

def capped_cylinder_map_to_rect (intersect_result):
    pass
from cartesian import *
from colour import *
from matrix import *
from transformation import *
from shape import *

###################################
# Code for a disc
###################################


def shape_sphere_intersect(shape, ray):

    a = cartesian_dot(ray[2], ray[2])
    b = mpfr(2) * cartesian_dot(ray[2], ray[1])
    c = cartesian_dot(ray[1], ray[1]) - mpfr(1)

    discriminant = ((b * b) - (mpfr(4) * a * c))
    if (discriminant < 0):
        return False
    sqroot = sqrt(discriminant)

    two_a = mpfr(2) * a
    t1 = ((0 - b) + sqroot) / (two_a)
    t2 = ((0 - b) - sqroot) / (two_a)

    if t1 < 0 and t2 < 0:
        return False
    elif t1 < 0 and t2 >= 0:
        t = t2
    elif t1 >= 0 and t2 < 0:
        t = t1
    else:
        if t1 < t2:
            t = t1
        else:
            t = t2

    result = {'t': t}

    result['raw_point'] = ray_calc_pt(ray, t)
    result['raw_normal'] = result['raw_point']
    return result


def shape_sphere_create(colour, specular, transform=None):
    shape = shape_emptyShape()
    shape[SHAPE_DIFFUSECOLOUR] = colour
    shape[SHAPE_SPECULARCOLOUR] = specular
    shape[SHAPE_INTERSECT_FUNC] = shape_sphere_intersect
    shape_setTransform(shape, transform)
    return shape
#====================


class Cylinder(Shape):

    def intersect(self, ray):
        four = mpfr(4)
        two = mpfr(2)
        zero = mpfr(0)

        # if the ray is parallel to the cylinder, no intersection

        if ray[RAY_VECTOR][3] == zero and ray[RAY_VECTOR][1] == zero:
            return False
        #o =Vector(ray[RAY_START].x, ray[RAY_START].y,  ray[RAY_START].z)
        #l =Vector(ray[RAY_VECTOR].x, ray[RAY_VECTOR].y,ray[RAY_VECTOR].z)
        #l.y =0
        #o.y =0
        o = cartesian_create(ray[RAY_START][1], 0, ray[RAY_START][3])
        l = cartesian_create(ray[RAY_VECTOR][1], 0, ray[RAY_VECTOR][3])

        o_c = o
        #a = l.dot(l)
        #b = two*(l.dot(o_c))
        #c = o_c.dot(o_c)-mpfr(1)

        a = cartesian_dot(l, l)
        b = two * cartesian_dot(l, o_c)
        c = cartesian_dot(o_c, o_c) - mpfr(1)

        discriminant = ((b * b) - (four * a * c))

        if (discriminant < zero):
            return False
        sqroot = sqrt(discriminant)

        two_a = two * a
        t1 = ((zero - b) + sqroot) / (two_a)
        t2 = ((zero - b) - sqroot) / (two_a)
        t = None

        if t1 < zero and t2 < zero:
            return False
        elif t1 < zero and t2 >= zero:
            t = t2
        elif t1 >= zero and t2 < zero:
            t = t1
        else:
            if t1 < t2:
                t = t1
            else:
                t = t2

        result = {'t': t}
        #result['raw_point'] = ray[RAY_START]+(ray[RAY_VECTOR].scale(result['t']))

        #result['raw_point'] = cartesian_add(ray[RAY_START], cartesian_scale(ray[RAY_VECTOR],t))
        result['raw_point'] = ray_calc_pt(ray, t)
        #result['raw_normal'] = Vector (result['raw_point'].x, 0, result['raw_point'].z).normalise()
        result['raw_normal'] = cartesian_create(
            result['raw_point'][1], 0, result['raw_point'][3])

        if (result != False):

            if result['raw_point'][2] > mpfr(0.5) or result['raw_point'][2] < mpfr(-0.5):
                result = False
        return result


class CappedCylinder(Cylinder):
    __topCap = None
    __bottomCap = None

    def __init__(self, colour, reflection, topcap={}, bottomcap={}, transform=None):
        super().__init__(colour, reflection, transform)
        if type(topcap) is dict:
            self.__topcap = topcap
        if type(bottomcap) is dict:
            self.__bottomcap = bottomcap

    def diffuseColour(self, intersectResult):
        #print ("intersectResult %s"%intersectResult)
        default = False
        if not 'shape_part' in intersectResult:
            return self.basicColour
        if intersectResult['shape_part'] == 'topcap_result' and self.__topcap != None and 'colour' in self.__topcap:
            return self.__topcap['colour']
        elif intersectResult['shape_part'] == 'bottomcap_result' and self.__bottomcap != None and 'colour' in self.__bottomcap:
            return self.__bottomcap['colour']
        else:
            return self.basicColour

    def reflectColour(self, intersectResult):
        #print ("intersectResult %s"%intersectResult)
        default = False
        if not 'shape_part' in intersectResult:
            return self.refelectColour
        if intersectResult['shape_part'] == 'topcap_result' and self.__topcap != None and 'colour' in self.__topcap:
            return self.__topcap['colour']
        elif intersectResult['shape_part'] == 'bottomcap_result' and self.__bottomcap != None and 'colour' in self.__bottomcap:
            return self.__bottomcap['colour']
        else:
            return self.refelectColour

    def intersect(self, ray):

        if ray[RAY_VECTOR][2] == 0:
            topcap_result = False
            bottomcap_result = False
        else:
            d = ray[RAY_VECTOR]

            topcap_t = (mpfr(-0.5) + (0 - ray[RAY_START][2])) / d[2]
            bottomcap_t = (mpfr(0.5) + (0 - ray[RAY_START][2])) / d[2]
            if topcap_t > 0:
                topcap_result = {'normal': cartesian_create(
                    0, -1, 0), 'shape': self, 't': topcap_t}
                #topcap_result['point'] = ray[RAY_START]+d.scale(topcap_t)
                #topcap_result['point'] = cartesian_add(ray[RAY_START], cartesian_scale(d,topcap_t))
                topcap_result['point'] = ray_calc_pt(ray, topcap_t)
                d = (topcap_result['point'][1] * topcap_result['point'][1]) + \
                    (topcap_result['point'][3] * topcap_result['point'][3])
                if d > mpfr(1):
                    topcap_result = False
            else:
                topcap_result = False
            d = ray[RAY_VECTOR]
            if bottomcap_t > 0:
                bottomcap_result = {'normal': cartesian_create(
                    0, 1, 0), 'shape': self, 't': bottomcap_t}
                #bottomcap_result['point'] = ray[RAY_START]+d.scale(bottomcap_t)
                #bottomcap_result['point'] = cartesian_add(ray[RAY_START], cartesian_scale(d,bottomcap_t))
                bottomcap_result['point'] = ray_calc_pt(bottom, topcap_t)
                d = (bottomcap_result['point'][1] * bottomcap_result['point'][1]) + (
                    bottomcap_result['point'][3] * bottomcap_result['point'][3])
                if d > mpfr(1):
                    bottomcap_result = False
            else:
                bottomcap_result = False

        results = {'cyl_result': super().intersect(ray),
                   'topcap_result': topcap_result,
                   'bottomcap_result': bottomcap_result,
                   }

        final_result = False
        for key in results:
            result = results[key]
            if result != False:
                if final_result != False:
                    if result['t'] < final_result['t']:
                        final_result = result
                        final_result['shape_part'] = key
                else:
                    final_result = result
                    final_result['shape_part'] = key

        return final_result


class Cone(Shape):

    __y_top = mpfr(0)
    __y_bottom = mpfr(1)

    def __init__(self, colour, reflection, y_top=None, y_bottom=None, transform=None):
        super().__init__(colour, reflection, transform)
        if y_top != None and y_top >= 0:
            self.__y_top = mpfr(y_top)
        if y_bottom != None and y_bottom >= 0:
            self.__y_bottom = mpfr(y_bottom)

        if self.__y_top > self.__y_bottom:
            j = self.__y_bottom
            self.__y_bottom = self.__y_top
            self.__y_top = j

    def ytop(self):
        return self.__y_top

    def ybottom(self):
        return self.__y_bottom

    def intersect(self, ray, extra=0):

        zero = mpfr(0)

        # if the ray is parallel to the cone and y_top is more than 0, no
        # intersection
        if self.__y_top > zero and ray[RAY_VECTOR][3] == zero and ray[RAY_VECTOR][1] == zero:
            return False
        #print (ray)
        one = mpfr(1)
        four = mpfr(4)
        two = mpfr(2)

        o = ray[RAY_START]
        d = ray[RAY_VECTOR]

        #a = (d.x*d.x)+(d.z*d.z)-(d.y*d.y)
        #b = (2.0*(d.x*o.x)) + (2.0*(o.z*d.z)) - (2.0*(d.y*o.y))
        #c = (o.x*o.x)+(o.z*o.z)-(o.y*o.y)

        a = (d[1] * d[1]) + (d[3] * d[3]) - (d[2] * d[2])
        b = (2.0 * (d[1] * o[1])) + \
            (2.0 * (o[3] * d[3])) - (2.0 * (d[2] * o[2]))
        c = (o[1] * o[1]) + (o[3] * o[3]) - (o[2] * o[2])

        discriminant = ((b * b) - (four * a * c))

        if (discriminant < zero):
            return False
        sqroot = sqrt(discriminant)

        two_a = two * a
        t1 = ((zero - b) + sqroot) / (two_a)
        t2 = ((zero - b) - sqroot) / (two_a)

        t2_used = False
        t1_used = False

        if t1 < zero and t2 < zero:
            return False
        elif t1 < zero and t2 >= zero:
            t = t2
            t2_used = True
        elif t1 >= zero and t2 < zero:
            t = t1
            t1_used = True
        else:
            if t1 < t2:
                t = t1
                t1_used = True
            else:
                t = t2
                t2_used = True

        result = {'t': t}
        #result['raw_point'] = ray[RAY_START]+(ray[RAY_VECTOR].scale(result['t']))
        #result['raw_point'] = cartesian_add(ray[RAY_START], cartesian_scale(ray[RAY_VECTOR],t))
        result['raw_point'] = ray_calc_pt(ray, t)
        extra = extra + 1

        if (result != False):

            if not self.__testPoint(result['raw_point']):

                if not t1_used and t1 > zero:

                    #p2 = ray[RAY_START]+(ray[RAY_VECTOR].scale(t1))
                    #p2= cartesian_add(ray[RAY_START], cartesian_scale(ray[RAY_VECTOR],t1))
                    p2 = ray_calc_pt(ray, t1)
                    if not self.__testPoint(p2):
                        if 'reintersct_count' in result and result['reintersct_count'] < 5:
                            result = self.__reIntersect(ray, result, extra)
                        else:
                            return False
                    else:
                        result['t'] = t1
                        result['raw_point'] = p2

                elif not t2_used and t2 > zero:

                    #p2 = ray[RAY_START]+(ray[RAY_VECTOR].scale(t2))
                    #p2= cartesian_add(ray[RAY_START], cartesian_scale(ray[RAY_VECTOR],t2))
                    p2 = ray_calc_pt(ray, t2)
                    if not self.__testPoint(p2):
                        if 'reintersct_count' in result and result['reintersct_count'] < 5:
                            result = self.__reIntersect(ray, result, extra)
                        else:
                            return False
                    else:
                        result['t'] = t2
                        result['raw_point'] = p2
                else:
                    return False
        if (result != False):
            #result['raw_normal'] = 	Vector (result['raw_point'].x, 0, result['raw_point'].z).normalise()
            result['raw_normal'] = cartesian_normalise(cartesian_create(
                result['raw_point'][1], 0, result['raw_point'][3]))
        return result

    def __testPoint(self, point):

        return not(point[2] > self.__y_bottom or point[2] < self.__y_top)

    def __reIntersect(self, ray, result, extra):
        #p_new = ray[RAY_START]+(ray[RAY_VECTOR].scale(result['t']+mpfr("0.00001")))
        #p_new = cartesian_add(ray[RAY_START], cartesian_scale(ray[RAY_VECTOR],result['t']+mpfr("0.00001")))
        new_ray = ray_create(ray_calc_pt(
            ray, result['t'] + mpfr("0.00001")), ray[RAY_VECTOR])
        new_result = self.intersect(new_ray, {'ignorecaps': True}, extra)
        if (new_result != False):
            original_t = result['t']
            result = new_result
            result['t'] = result['t'] + original_t + mpfr("0.00001")

        else:
            result = False

        return result


class CappedCone(Cone):
    __topcap = None
    __bottomcap = None

    def __init__(self, colour, reflection, topcap={}, bottomcap={}, y_top=None, y_bottom=None, transform=None):
        super().__init__(colour, reflection, y_top, y_bottom, transform)
        if type(topcap) is dict:
            self.__topcap = topcap
        if type(bottomcap) is dict:
            self.__bottomcap = bottomcap

    def diffuseColour(self, intersectResult):
        default = False
        if not 'shape_part' in intersectResult:
            return self.basicColour
        if intersectResult['shape_part'] == 'topcap_result' and self.__topcap != None and 'colour' in self.__topcap:
            return self.__topcap['colour']
        elif intersectResult['shape_part'] == 'bottomcap_result' and self.__bottomcap != None and 'colour' in self.__bottomcap:
            return self.__bottomcap['colour']
        else:
            return self.basicColour

    def refelectColour(self, intersectResult):
        default = False
        if not 'shape_part' in intersectResult:
            return self.refelectColour
        if intersectResult['shape_part'] == 'topcap_result' and self.__topcap != None and 'colour' in self.__topcap:
            return self.__topcap['colour']
        elif intersectResult['shape_part'] == 'bottomcap_result' and self.__bottomcap != None and 'colour' in self.__bottomcap:
            return self.__bottomcap['colour']
        else:
            return self.refelectColour

    def intersect(self, ray, extra=0):
        if type(extra) is dict and 'ignorecaps' in extra and extra['ignorecaps']:
            return super().intersect(ray, extra)
        zero = mpfr(0)
        ytop = self.ytop()
        do_top_cap = (ytop > zero)
        if ray[RAY_VECTOR][2] == zero:
            topcap_result = False
            bottomcap_result = False
        else:
            d = ray[RAY_VECTOR]

            ytop_r2 = (ytop * ytop)
            ybottom = self.ybottom()
            ybottom_r2 = (ybottom * ybottom)

            if do_top_cap:
                topcap_t = (ytop + (zero - ray[RAY_START][2])) / d[2]
            bottomcap_t = (ybottom + (zero - ray[RAY_START][2])) / d[2]
            if do_top_cap and topcap_t > zero:
                topcap_result = {'raw_normal': cartesian_create(
                    0, -1, 0), 'shape': self, 't': topcap_t}
                #topcap_result['raw_point'] = ray[RAY_START]+d.scale(topcap_t)
                #topcap_result['point'] = cartesian_add(ray[RAY_START], cartesian_scale(d,topcap_t))
                topcap_result['point'] = ray_calc_pt(ray, topcap_t)
                d = (topcap_result['raw_point'][1] * topcap_result['point'][1]
                     ) + (topcap_result['point'][3] * topcap_result['point'][3])
                if d > ytop_r2:
                    topcap_result = False
            else:
                topcap_result = False
            d = ray[RAY_VECTOR]
            if bottomcap_t > zero:
                bottomcap_result = {'raw_normal': cartesian_create(
                    0, 1, 0), 'shape': self, 't': bottomcap_t}
                #bottomcap_result['raw_point'] = ray[RAY_START]+d.scale(bottomcap_t)
                #bottomcap_result['point'] = cartesian_add(ray[RAY_START], cartesian_scale(d,bottomcap_t))
                bottomcap_result['point'] = ray_calc_pt(ray, bottomcap_t)
                d = (bottomcap_result['raw_point'][1] * bottomcap_result['raw_point'][1]) + (
                    bottomcap_result['raw_point'][3] * bottomcap_result['raw_point'][3])
                if d > ybottom_r2:
                    bottomcap_result = False
            else:
                bottomcap_result = False

        results = {'cyl_result': super().intersect(ray),
                   'bottomcap_result': bottomcap_result,
                   }
        if do_top_cap:
            results['topcap_result'] = topcap_result

        final_result = False
        for key in results:
            result = results[key]
            if result != False:
                if final_result != False:
                    if result['t'] < final_result['t']:
                        final_result = result
                        final_result['shape_part'] = key
                else:
                    final_result = result
                    final_result['shape_part'] = key

        return final_result

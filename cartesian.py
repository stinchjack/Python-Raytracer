"""
	Functions for dealing with cartesian values and rays.
   A cartesian is stored as a tuple, with the first element being the
	string 'cartesian' as an identifier, and the last three being X, Y and Z
	values. A cartesian can be used for either vectors (directions) or points.

	A ray is a tuple with four elements, the first being the string 'ray' as an
	identifier, the second is a cartesian being the start point of the ray,
	the third is a cartesian being the direction of the ray, and the fourth is
	a boolean indicating weather the ray is a shadow-ray. 

	A lineseg2d is a tuple used to store a line segment, where that line is in two
	dimensions, the thrid being discarded. (Used for polygon intersection tests).

	Authour: Jack Stinchcombe <stinchjack@gmail.com>

"""

import gmpy2
from gmpy2 import *
from private import *

# ['cartesian',0,0,0,NONe]
CARTESIAN_X = 1
CARTESIAN_Y = 2
CARTESIAN_Z = 3
CARTESIAN_LEN = 4
CARTESIAN_NORMALISED = 5

POINT_X = 1
POINT_Y = 2
POINT_Z = 3
POINT_LEN = 4
POINT_NORMALISED = 5

VECTOR_X = 1
VECTOR_Y = 2
VECTOR_Z = 3
VECTOR_LEN = 4
VECTOR_NORMALISED = 5


def cartesian_create(x, y, z):
    """Creates a cartesian tuple
	
	x: The x part of the co-ordinate
	y: The y part of the co-ordinate
	z: The z part of the co-ordinate
	
	Returns: a tuple representing a cartesian
	"""
    return ('cartesian', x, y, z)


def cartesian_copy(c):
    """Creates a copy of a cartesian

	c: a cartesian to copy
	
	Returns: a copy of c
	
	"""
    return ('cartesian', c[1], c[2], c[3], c[4], c[5])


def cartesian_add(c1, c2):
    """Adds two cartesians together
	
	c1: a cartesian
	c2: a cartesian
	
	Returns: a cartesian ,the result of adding c1 and c2
	"""
    return ('cartesian', c1[1] + c2[1], c1[2] + c2[2], c1[3] + c2[3])


def cartesian_sub(c1, c2):
    """Subtracts cartesian c2 from cartesian c1
	
	c1: a cartesian
	c2: a cartesian
	Returns: a cartesian, the result of subtracting c2 from c1
	"""
    return ('cartesian', c1[1] - c2[1], c1[2] - c2[2], c1[3] - c2[3])


def cartesian_dot(c1, c2):
    """Calculates the dot product of cartesians c1 and c2
	c1: a cartesian
	c2: a cartesian
	Returns: the dot product of cartesians c1 and c2"""
    return (c1[1] * c2[1]) + (c1[2] * c2[2]) + (c1[3] * c2[3])


def cartesian_scale(c1, scale):
    """Multiples the cartesian by the scalar value given. Useful for Vectors 
	
	c1: a cartesian
	scale: the value to scale/multiply the c1 by.
	
	Returns: c1 multiplied by scale
	
	"""
    return ('cartesian', c1[1] * scale, c1[2] * scale, c1[3] * scale)


def cartesian_len(c):
    """Calculates the length of given cartesian.   Useful for vectors.
	
	c1: a cartesian
	returns: the length of given c1
	
	"""
    return sqrt((c[1] * c[1]) + (c[2] * c[2]) + (c[3] * c[3]))


def cartesian_normalise(c):
    """Creates a cartesian with a length of 1 from the given
    cartesian. Useful for Vectors
	
	c: a cartesian
	returns: a normalised cartesian
	"""
    return cartesian_scale(c, mpfr(1.0) / sqrt((c[1] * c[1]) + (c[2] * c[2]) + (c[3] * c[3])))


def cartesian_cross(c1, c2):
    """Calculates the cross product of two cartesians.
	
	c1: a cartesian
	c2: a cartesian
	
	Returns: cross-product of c1 and c2
	
	"""
    return ('cartesian', (c1[2] * c2[3]) - (c1[3] * c2[2]), (c1[3] * c2[1]) - (c1[1] * c2[3]), (c1[1] * c2[2]) - (c1[2] * c2[1]), None, None)

# ['ray',cartesian,cartesian,False]
RAY_START = 1
RAY_VECTOR = 2
RAY_ISSHADOW = 3


def ray_create(start, vector, shadow=False):
    """Creates a ray tuple
	
	start: a cartesian point, being the start of the ray
	vector: a cartesian vector, being the direction of the ray
	shadow: a boolean, indicating if the ray is being used for shadow
		detection.
	
	Returns: a ray tuple
	"""
    return ('ray', start, vector, shadow)


def ray_scale(ray, scale):
    """Multiples the lenth of the ray by the given scale
	
	ray: a ray tuple
	scale: the value to scale the length by
	
	Returns: a new ray, being the a ray with the same
	start point as the given ray, and the vector from the given ray but
	scaled by the given amount
	"""
    return ('ray', ray[1], vector_scale(ray[2], scale), ray[3])


def ray_is_shadow(ray):
    """Determines if the ray is used for shadow detection
	
	ray: a ray tuple
	
	Returns: the fourth element from the tuple, being a boolean.
	"""
    return ray[3]


def ray_calc_pt(ray, t):
    """Calculates a point along a ray, returning a cartesian. The vector part of the the 
    ray is scaled by t and added to the start point of the array.
	
	ray: a ray tuple
	t: the position along the ray, proportional to the vector component of the ray.
	
	returns: a cartesian, calculated by the expression  ray start + (ray vector * t)
	"""
    return ('cartesian', ray[1][1] + (ray[2][1] * t), ray[1][2] + (ray[2][2] * t), ray[1][3] + (ray[2][3] * t), None, None)


def lineseg2d_create(start, end):
    """Creates a lineseg2d tuple"""
    return ('lineseg2d', start, end)


def lineseg2d_ccw(A, B, C):
    """
    Line intersection code derived from 
    http://bryceboe.com/2006/10/23/line-segment-intersection-algorithm/
    """
    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])


def lineseg2d_intersect(ls1, ls2):
    """
    Determines if two line segments intersect with each other. (Used for polygon 
    intersection tests).

    Line intersection code derived from 
    http://bryceboe.com/2006/10/23/line-segment-intersection-algorithm/
    """
    return lineseg2d_ccw(ls1[1], ls2[1], ls2[2]) != lineseg2d_ccw(ls1[2], ls2[1], ls2[2]) and lineseg2d_ccw(ls1[1], ls1[2], ls2[1]) != lineseg2d_ccw(ls1[1], ls1[2], ls2[2])

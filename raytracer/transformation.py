try:
    from gmpy2 import *
except ImportError:
    from math import *
    from raytracer.mpfr_dummy import *

from raytracer.matrix import *
from raytracer.cartesian import *
from copy import *

"""Support for transformations of points, vectors and rays"""


class Transform:
    """A class to support matrix transformations of rays and cartesians"""
    

    def __str__(self):
        """Returns a string representation of a Transform.

        :return: String representation of a Transformation."""

        return ("{no_transform: %s options: %s " +
                "matrix: %s inverse_matrix: %s}" %
                (self.__no_transform__, self.__options__, self.__matrix__,
                 self.__inverse_matrix__))

    def __init__(self, options):
        """Class constructor. Calls self.set_options.

        :param options: a dictionary with the following optional elements:

        * 'translate': a dictionary with the following elements:
            o 'x': the distance to translate in the X dimension
            o 'y': the distance to translate in the Y dimension
            o 'z': the distance to translate in the Z dimension

        * 'scale': a dictionary with the following elements:
            o 'x': the amount to scale in the X dimension
            o 'y': the amount to scale in the Y dimension
            o 'z': the amount to scale in the Z dimension

        * 'rotation': a dictionary with the following elements:
            o 'vector': a cartesian vector to use as an axis to rotate about
            o 'angle': the angle to rotate about the vector, in degrees
        """
        self.__options__ = {}
        self.__inverse_matrix__ = None
        self.__matrix__ = None
        self.__inverse_matrix__ = None
        self.__no_transform__ = True
        self.set_options(options)

    def no_transform(self):
        """Returns True if the transform would not result in any change to a
        ray or cartesian, else False

        :return: boolean
        """
        return self.__no_transform__

    def matrix(self):
        """Returns the calculated matrix.

        :return: Matrix object
        """
        return self.__matrix__

    def options(self):
        """Returns a dictionary of transformation options.

        :return: dictionary
        """
        return self.__options__

    def set_options(self, options):
        """Sets transformation options.

        :param options: a dictionary with the following optional elements:

        * 'translate': a dictionary with the following elements:
            o 'x': the distance to translate in the X dimension
            o 'y': the distance to translate in the Y dimension
            o 'z': the distance to translate in the Z dimension

        * 'scale': a dictionary with the following elements:
            o 'x': the amount to scale in the X dimension
            o 'y': the amount to scale in the Y dimension
            o 'z': the amount to scale in the Z dimension

        * 'rotation': a dictionary with the following elements:
            o 'vector': a cartesian vector to use as an axis to rotate about
            o 'angle': the angle to rotate about the vector, in degrees
        """

        scalematrix = None
        rotatematrix = None
        translatematrix = None
        __inverse_matrix__ = None
        if ('translate' in options):
            if 'cartesian' not in options['translate']:
                options['translate'] = cartesian_create(
                    mpfr(options['translate']['x']),
                    mpfr(options['translate']['y']),
                    mpfr(options['translate']['z']))


        self.__options__ = options

        if ('scale' not in options and
                'translate' not in options and 'rotate' not in options):
            self.__matrix__ = Matrix()
            self.__no_transform__ = True
            return
        else:
            self.__no_transform__ = False

        if 'scale' in options:
            scalematrix = ScaleMatrix(
                1.0 / mpfr(options['scale']['x']),
                1.0 / mpfr(options['scale']['y']),
                1.0 / mpfr(options['scale']['z']))
        if 'rotate' in options:
            vector = cartesian_normalise(options['rotate']['vector'])
            rotatematrix = RotationMatrix(
                vector, mpfr(options['rotate']['angle']))

        if rotatematrix is not None and scalematrix is None:
            self.__matrix__ = rotatematrix
            self.__inverse_matrix__ = rotatematrix.inversed()
        elif scalematrix is not None and rotatematrix is not None:
            self.__matrix__ = scalematrix * rotatematrix
            # deepcopy(rotatematrix.inversed()) # *
            # deepcopy(scalematrix.inversed())
            self.__inverse_matrix__ = self.__matrix__.inversed()
        elif scalematrix is not None and rotatematrix is None:
            self.__matrix__ = scalematrix
            self.__inverse_matrix__ = scalematrix.inversed()
        else:
            self.__matrix__ = Matrix()
            self.__inverse_matrix__ = Matrix()

    def transform(self, ray):
        """Transforms a given ray.

        :param ray: a ray to transform.

        :return: the ray, transformed
        """

        ray_dir = ray[RAY_VECTOR]
        ray_point = ray[RAY_START]

        if 'translate' in self.__options__:
            ray_point = cartesian_sub(
                ray_point, self.__options__['translate'])

        if isinstance(self.__matrix__, Matrix):
            ray_dir = transform_matrix_mul_cartesian(
                self.__matrix__.matrix, ray_dir)
            ray_point = transform_matrix_mul_cartesian(
                self.__matrix__.matrix, ray_point)



        return ray_create(ray_point, ray_dir, ray[RAY_ISSHADOW])
        

    def transform_cartestian(self, cartesian):
        if self.__no_transform__:
            return cartesian        
        
        if isinstance(self.__matrix__, Matrix):
            new_cartesian = transform_matrix_mul_cartesian(
                self.__matrix__.matrix, cartesian)
  
        if 'translate' in self.__options__:
            new_cartesian = cartesian_sub(
                new_cartesian, self.__options__['translate']) 
        return new_cartesian              
                
    def transform_point(self, point, inverse=False):
        """Transforms a point. (A point can only be transformed by
        translation.)

        :param point: a cartesian to transform

        :param inverse: A boolean. If True the inverse transformation is
                        applied

        :return: the translated point
        """

        if 'translate' in self.__options__:
            if inverse:
                return cartesian_add(point, self.__options__['translate'])
            else:
                return cartesian_sub(point, self.__options__['translate'])

    def inverse_transform(self, normal, translate=False):
        """Applies inverse transformation to a vector. (Used for normals.)

        :param normal: a cartesian to transform
        :return: the transformed vector
        """

        if self.__no_transform__:
            return normal

        if self.__inverse_matrix__ is not None:
            normal = (self.__inverse_matrix__ * (normal))

        if translate and 'translate' in self.__options__:
            return cartesian_add(normal, self.__options__['translate'])

        return normal

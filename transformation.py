import gmpy2
from gmpy2 import *
from matrix import *
from cartesian import *
from copy import *

"""Support for transformations of points, vectors and rays."""


class Transform:
    """A class to support matrix transformations of rays and cartesians."""
    __options = {}

    def __str__(self):
        """Returns a string representation of a Transform.

        Returns: String representation of object.
        """
        return "{noTransform: %s options: %s matrix: %s inverseMatrix: %s}" % (self.__no_transform, self.__options, self.__matrix, self.__inverse_matrix)

    def __init__(self, options):
        """Class constructor. Calls self.set_options.

        options: a dictionary with the following optional elements:

                'translate': a dictionary with the following elements:
                        'x': the distance to translate in the X dimension
                        'y': the distance to translate in the Y dimension
                        'z': the distance to translate in the Z dimension

                'scale': a dictionary with the following elements:
                        'x': the amount to scale in the X dimension
                        'y': the amount to scale in the Y dimension
                        'z': the amount to scale in the Z dimension

                'rotation': a dictionary with the following elements:
                        'vector': a cartesian vector to use as an axis to rotate about
                        'angle': the angle to rotate about the vector, in degrees	"""
        self.set_options(options)

    def no_transform(self):
        """Returns True if the transform would not result in any change to a ray or cartesian, else False

        Returns: boolean
        """
        return self.__no_transform

    def matrix(self):
        """Returns the calculated matrix.

        Returns: Matrix object

        """
        return self.__matrix

    def options(self):
        """
        Returns a dictionary of transformation options.

        Returns: dictionary

        """
        return self.__options

    def set_options(self, options):
        """Sets transformation options.

        options: a dictionary with the following optional elements:

                'translate': a dictionary with the following elements:
                        'x': the distance to translate in the X dimension
                        'y': the distance to translate in the Y dimension
                        'z': the distance to translate in the Z dimension

                'scale': a dictionary with the following elements:
                        'x': the amount to scale in the X dimension
                        'y': the amount to scale in the Y dimension
                        'z': the amount to scale in the Z dimension

                'rotation': a dictionary with the following elements:
                        'vector': a cartesian vector to use as an axis to rotate about
                        'angle': the angle to rotate about the vector, in degrees

        """
        self.__options = options
        scalematrix = None
        rotatematrix = None
        translatematrix = None
        __inverse_matrix = None
        if 'translate' in options:
            if not 'cartesian' in options['translate']:
                options['translate'] = cartesian_create(mpfr(options['translate']['x']), mpfr(
                    options['translate']['y']), mpfr(options['translate']['z']))

        if not 'scale' in options and not 'translate' in options and not 'rotate' in options:
            self.__matrix = Matrix()
            self.__no_transform = True
            return
        else:
            self.__no_transform = False

        if 'scale' in options:
            scalematrix = ScaleMatrix(1.0 / mpfr(options['scale']['x']), mpfr(
                1.0 / options['scale']['y']), 1.0 / mpfr(options['scale']['z']))
        if 'rotate' in options:
            vector = cartesian_normalise(options['rotate']['vector'])
            rotatematrix = RotationMatrix(
                vector, mpfr(options['rotate']['angle']))

        if rotatematrix != None and scalematrix == None:
            self.__matrix = rotatematrix
            self.__inverse_matrix = rotatematrix.inversed()
        elif scalematrix != None and rotatematrix != None:
            self.__matrix = scalematrix * rotatematrix
            # deepcopy(rotatematrix.inversed()) #*
            # deepcopy(scalematrix.inversed())
            self.__inverse_matrix = self.__matrix.inversed()
        elif scalematrix != None and rotatematrix == None:
            self.__matrix = scalematrix
            self.__inverse_matrix = scalematrix.inversed()
        else:
            self.__matrix = Matrix()
            self.__inverse_matrix = Matrix()

    def transform(self, ray):
        """Transforms a given ray.

        ray: a ray to transform.

        returns: ray, transformed
        """
        if self.__no_transform:
            return ray

        ray_dir = ray[RAY_VECTOR]
        ray_point = ray[RAY_START]

        if 'translate' in self.__options:
            ray_point = cartesian_sub(ray_point, self.__options['translate'])

        if isinstance(self.__matrix, Matrix):
            ray_dir = transform_matrix_mul_cartesian(
                self.__matrix.matrix, ray_dir)
            ray_point = transform_matrix_mul_cartesian(
                self.__matrix.matrix, ray_point)
        return ray_create(ray_point, ray_dir, ray[RAY_ISSHADOW])

    def transform_point(self, point, inverse=False):
        """Transforms a point. (A point can only be transformed by translation.)

        point: a cartesian to transform

        inverse: a boolean. If true the inverse transformation is applied.

        returns: the translated point.
        """
        if 'translate' in self.__options:
            if inverse:
                return cartesian_add(point, self.__options['translate'])
            else:
                return cartesian_sub(point, self.__options['translate'])

    def inverse_transform(self, normal, translate=False):
        """Applies inverse transformation to a vector. (Used for normals.)

        normal: a cartesian to transform

        returns: the transformed vector.


        """
        if self.__no_transform:
            return normal

        if self.__inverse_matrix != None:
            normal = (self.__inverse_matrix * (normal))
            #ray_point = transform_matrix_mul_cartesian(self.__inverse_matrix.matrix, n)

        if translate and 'translate' in self.__options:
            return cartesian_add(normal, self.__options['translate'])

        #print (result)
        return normal

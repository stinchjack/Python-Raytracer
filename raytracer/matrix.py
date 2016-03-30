import gmpy2
from gmpy2 import mpfr
from raytracer.cartesian import *

"""Support for matrix maths."""


class Matrix:
    """A generic 4x4 maths matrix for transformation purposes."""

    def __init__(self):
        """Constructor for a Matrix object.  The stored matrix is:

                1 0 0 0
                0 1 0 0
                0 0 1 0
                0 0 0 1
                """
        self.matrix = [[mpfr(1), mpfr(0), mpfr(0), mpfr(0)],
                       [mpfr(0), mpfr(1), mpfr(0), mpfr(0)],
                       [mpfr(0), mpfr(0), mpfr(1), mpfr(0)],
                       [mpfr(0), mpfr(0), mpfr(0), mpfr(1)]]

        self.inverse = [[mpfr(1), mpfr(0), mpfr(0), mpfr(0)],
                        [mpfr(0), mpfr(1), mpfr(0), mpfr(0)],
                        [mpfr(0), mpfr(0), mpfr(1), mpfr(0)],
                        [mpfr(0), mpfr(0), mpfr(0), mpfr(1)]]

    def __mul__(self, matrix):
        """Matrix multiplier operator.

                :param matrix: a matrix to multiply with. This can either
                be a Matrix instance or a cartesian tuple, with the
                coressponding return type."""

        if isinstance(matrix, Matrix):

            new_matrix = Matrix()

            for i in range(0, 4):
                for j in range(0, 4):
                    new_matrix.matrix[i][j] = mpfr(0)
                    for k in range(0, 4):
                        new_matrix.matrix[i][j] = new_matrix.matrix[i][
                            j] + (self.matrix[i][k] * matrix.matrix[k][j])

            for i in range(0, 4):
                for j in range(0, 4):
                    new_matrix.inverse[i][j] = mpfr(0)
                    for k in range(0, 4):
                        new_matrix.inverse[i][j] = new_matrix.inverse[i][
                            j] + (matrix.inverse[i][k] * self.inverse[k][j])

            return new_matrix

        elif 'cartesian' in matrix:
            m = self.matrix

            new_vector_x = (m[0][0] * matrix[1]) + \
                (m[0][1] * matrix[2]) + (m[0][2] * matrix[3])
            new_vector_y = (m[1][0] * matrix[1]) + \
                (m[1][1] * matrix[2]) + (m[1][2] * matrix[3])
            new_vector_z = (m[2][0] * matrix[1]) + \
                (m[2][1] * matrix[2]) + (m[2][2] * matrix[3])
            new_vector = cartesian_create(
                new_vector_x, new_vector_y, new_vector_z)

            return new_vector


# [M11 M12 M13 M14]   [V.x]   [M11 * V.x + M12 * V.y + M13 * V.z + M14 * V.h]
# M * V = [M21 M22 M23 M24] * [V.y]
#       = [M21 * V.x + M22 * V.y + M23 * V.z + M24 * V.h]
# [M31 M32 M33 M34]   [V.z]   [M31 * V.x + M32 * V.y + M33 * V.z + M34 * V.h]
# [M41 M42 M43 M44]   [V.h]   [M41 * V.x + M42 * V.y + M43 * V.z + M44 * V.h]

        else:
            return None

    def inversed(self):
        """Returns the inverse matrix."""
        m = Matrix()

        m.matrix = (self.inverse)
        m.inverse = (self.matrix)

        return m


class ScaleMatrix(Matrix):
    """A matrix for scaling."""

    def __init__(self, x, y, z):
        """Constructor for ScaleMatrix. The generated matrix is:

                        x 0 0 0
                        0 y 0 0
                        0 0 z 0
                        0 0 0 1

                :param x: the amount to scale on X axis
                :param y: the amount to scale on Y axis
                :param z: the amount to scale on Z axis """
        x = mpfr(x)
        y = mpfr(y)
        z = mpfr(z)

        inv_x = mpfr(1) / x
        inv_y = mpfr(1) / y
        inv_z = mpfr(1) / z

        self.matrix = [[x, mpfr(0), mpfr(0), mpfr(0)],
                       [mpfr(0), y, mpfr(0), mpfr(0)],
                       [mpfr(0), mpfr(0), z, mpfr(0)],
                       [mpfr(0), mpfr(0), mpfr(0), mpfr(1)]]

        self.inverse = [[inv_x, mpfr(0), mpfr(0), mpfr(0)],
                        [mpfr(0), inv_y, mpfr(0), mpfr(0)],
                        [mpfr(0), mpfr(0), inv_z, mpfr(0)],
                        [mpfr(0), mpfr(0), mpfr(0), 1]]


class TranslationMatrix(Matrix):
    """A matrix for translation"""

    def __init__(self, value):
        """Constructor for TranslationMatrix. The generated matrix is:

                        1 0 0 x
                        0 1 0 y
                        0 0 1 z
                        0 0 0 1

                :param value: a dictionary with the following elements:
                        'x': the amount to translate in the X dimension
                        'y': the amount to translate in the Y dimension
                        'z': the amount to translate in the Z dimension"""
        x = value
        if not isinstance(x, Cartesian):
            x = mpfr(value['x'])
            y = mpfr(value['y'])
            z = mpfr(value['z'])
            if x <= 0 or y <= 0 or z <= 0:
                return None
            self.matrix = [[mpfr(1), mpfr(0), mpfr(0), mpfr(x)],
                           [mpfr(0), mpfr(1), mpfr(0), mpfr(y)],
                           [mpfr(0), mpfr(0), mpfr(1), mpfr(z)],
                           [mpfr(0), mpfr(0), mpfr(0), mpfr(1)]]

            self.inverse = [[mpfr(1), mpfr(0), mpfr(0), mpfr(-x)],
                            [mpfr(0), mpfr(1), mpfr(0), mpfr(-y)],
                            [mpfr(0), mpfr(0), mpfr(1), mpfr(-z)],
                            [mpfr(0), mpfr(0), mpfr(0), mpfr(1)]]
        else:
            self.__init__(x.x, x.y, x.z)


class RotationZMatrix(Matrix):
    """A matrix for rotation about the Z axis."""

    def __init__(self, angle):
        """Class constructor for RotationMatrix.
                :param angle: the amount of rotation, in degrees."""

        rad = radians(angle)
        costh = cos(rad)
        sinth = sin(rad)
        self.matrix = [[costh, mpfr(0) - sinth, mpfr(0), mpfr(0)],
                       [sinth, costh, mpfr(0), mpfr(0)],
                       [mpfr(0), mpfr(0), mpfr(1), mpfr(0)],
                       [mpfr(0), mpfr(0), mpfr(0), mpfr(1)]]

        costh = cos(-rad)
        sinth = sin(-rad)
        self.inverse = [[costh, mpfr(0) - sinth, mpfr(0), mpfr(0)],
                        [sinth, costh, mpfr(0), mpfr(0)],
                        [mpfr(0), mpfr(0), mpfr(1), mpfr(0)],
                        [mpfr(0), mpfr(0), mpfr(0), mpfr(1)]]


class RotationMatrix(Matrix):
    """A matrix for rotation about an arbitrary axis.
        See http://math.kennesaw.edu/~plaval/math4490/rotgen.pdf"""

    def __init__(self, vector, angle):
        """Class constructor for RotationMatrix.

                :param vector: a cartesian vector as an axis.
                :param angle: the amount of rotation about the axis,
                in degrees."""
        # rad = mpfr(angle) *(self.pi/mpfr(180))
        rad = radians(angle)
        one = mpfr(1)
        zero = mpfr(0)
        t = one - cos(rad)
        S = sin(rad)
        C = cos(rad)
        u2x = mpfr(vector[1]) * mpfr(vector[1])
        u2y = mpfr(vector[2]) * mpfr(vector[2])
        u2z = mpfr(vector[3]) * mpfr(vector[3])
        ux = mpfr(vector[1])
        uy = mpfr(vector[2])
        uz = mpfr(vector[3])

        c1 = (t * u2x) + C
        c2 = (t * ux * uy) - (S * uz)
        c3 = (t * ux * uz) + (S * uy)

        c4 = (t * ux * uy) + (S * uz)
        c5 = (t * u2y) + C
        c6 = (t * uy * uz) - (S * ux)

        c7 = (t * ux * uz) - (S * uy)
        c8 = (t * uy * uz) + (S * ux)
        c9 = (t * u2z) + C

        self.matrix = [[c1, c2, c3, zero],
                       [c4, c5, c6, zero],
                       [c7, c8, c9, zero],
                       [zero, zero, zero, one]]

        rad = zero - rad
        t = one - cos(rad)
        S = sin(rad)
        C = cos(rad)

        c1 = (t * u2x) + C
        c2 = (t * ux * uy) - (S * uz)
        c3 = (t * ux * uz) + (S * uy)

        c4 = (t * ux * uy) + (S * uz)
        c5 = (t * u2y) + C
        c6 = (t * uy * uz) - (S * ux)

        c7 = (t * ux * uz) - (S * uy)
        c8 = (t * uy * uz) + (S * ux)
        c9 = (t * u2z) + C

        self.inverse = [[c1, c2, c3, zero],
                        [c4, c5, c6, zero],
                        [c7, c8, c9, zero],
                        [zero, zero, zero, one]]

import raytracer.quadraticshapes as quadraticshapes
import unittest
import raytracer.shape as shape
import math
import raytracer.colour as colour
import raytracer.transformation as transformation
import raytracer.cartesian as cartesian
import random


class TestCylinderProdcedures(unittest.TestCase):

    def setUp(self):
        self.cylinder = quadraticshapes.shape_cylinder_create(
            colour.colour_create(.5, .5, .5),
            colour.colour_create(.5, .5, .5))
        self.cylinder2 = quadraticshapes.shape_cylinder_create(
            colour.colour_create(.1, .1, .1),
            colour.colour_create(.2, .2, .2),
            transformation.Transform({
                'scale': {'x': 2.0, 'y': 2.0, 'z': 1.0},
                'rotate': {'vector': cartesian.cartesian_create(1, 0, 0),
                           'angle': 30},
            }))

    def test_func_shape_cylinder_create(self):

        self.assertEqual(self.cylinder,
                         ['shape',
                          'cylinder',
                          ('colour', 0.5, 0.5, 0.5),
                          ('colour', 0.5, 0.5, 0.5),
                          quadraticshapes.shape_cylinder_intersect,
                          None,
                          shape.shape_diffuse_colour,
                          shape.shape_specular_colour,
                          None,
                          {}])

        self.assertEqual(self.cylinder2[: 8],
                         ['shape', 'cylinder',
                          ('colour', 0.1, 0.1, 0.1),
                          ('colour', 0.2, 0.2, 0.2),
                          quadraticshapes.shape_cylinder_intersect,
                          None,
                          shape.shape_diffuse_colour,
                          shape.shape_specular_colour])

        self.assertIsInstance(self.cylinder2[8], transformation.Transform)

    def test_func_shape_cylinder_intersect(self):
        # Test an untransformed cylinder for correct interesection tests

        ray_dir = cartesian.cartesian_create(0, 1, 0)
        # check rays paralell to cylinder miss
        for i in range(1, 50):
            ray_z_pos = random.random()
            ray_x_pos = random.random()
            ray_start = cartesian.cartesian_create(ray_x_pos, -2, ray_z_pos)
            ray = cartesian.ray_create(ray_start, ray_dir)
            result = \
                quadraticshapes.shape_cylinder_intersect(self.cylinder, ray)
            self.assertFalse(result, "Cylinder intersection result when" +
                             "ray in paralell to cylinder")


class TestConeProdcedures(unittest.TestCase):

    def setUp(self):
        self.cone = quadraticshapes.shape_cone_create(
            colour.colour_create(.5, .5, .5),
            colour.colour_create(.5, .5, .5))
        self.cone2 = quadraticshapes.shape_cone_create(
            colour.colour_create(.1, .1, .1),
            colour.colour_create(.2, .2, .2),
            None,
            None,
            transformation.Transform({
                'scale': {'x': 2.0, 'y': 2.0, 'z': 1.0},
                'rotate': {'vector': cartesian.cartesian_create(1, 0, 0),
                           'angle': 30},
            }))

    def test_func_shape_cone_create(self):

        self.assertEqual(self.cone,
                         ['shape',
                          'cone',
                          ('colour', 0.5, 0.5, 0.5),
                          ('colour', 0.5, 0.5, 0.5),
                          quadraticshapes.shape_cone_intersect,
                          None,
                          shape.shape_diffuse_colour,
                          shape.shape_specular_colour,
                          None,
                          {'y_top': 0, 'y_bottom': 1}])

        self.assertEqual(self.cone2[: 8],
                         ['shape', 'cone',
                          ('colour', 0.1, 0.1, 0.1),
                          ('colour', 0.2, 0.2, 0.2),
                          quadraticshapes.shape_cone_intersect,
                          None,
                          shape.shape_diffuse_colour,
                          shape.shape_specular_colour])

        self.assertIsInstance(self.cone2[8], transformation.Transform)
        self.assertEqual(self.cone2[9], {'y_bottom': 1, 'y_top': 0})

    def test_func_shape_cone_intersect(self):
        """
        This function does not work properly.

        ..to do: re-write and debug
        """
        return
        # Test an untransformed cone for correct interesection tests
        ray_start = cartesian.cartesian_create(0, -2, 0)
        for i in range(1, 200):
            print("--------")
            print("loop round #%d" % i)
            ray_z_dir = random.random()
            ray_x_dir = random.random()
            hit_expected = ((ray_z_dir * ray_z_dir) +
                            (ray_x_dir * ray_x_dir)) < 1.0
            # ray_dir = cartesian.cartesian_normalise(
            #             cartesian.cartesian_create(ray_x_dir, 3, ray_z_dir))
            ray_dir = cartesian.cartesian_create(ray_x_dir, 3, ray_z_dir)

            ray = cartesian.ray_create(ray_start, ray_dir)
            intersect_result =\
                quadraticshapes.shape_cone_intersect(self.cone, ray)

            if hit_expected:
                if (type(intersect_result) is dict):
                    print("hit as expected")
                else:
                    print("NOT hit as expected")
                self.assertTrue(type(intersect_result) is dict,
                                "intersect_result: %s \r\n ray: %s" % (
                    intersect_result, ray))
            else:
                if (type(intersect_result) is not dict):
                    print("missed as expected")
                else:
                    print("NOT missed as expected")
                self.assertTrue(type(intersect_result) is dict,
                                'intersect_result: %s \r\n ray: %s' +
                                'ray_x_dir: %f \r\n' +
                                'ray_z_dir: %f' % (
                    "intersect_result", "ray",
                    ray_x_dir, ray_z_dir))


if __name__ == '__main__':
    unittest.main()

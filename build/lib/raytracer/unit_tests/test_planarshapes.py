import raytracer.planarshapes as planarshapes
import unittest
import raytracer.shape as shape
import math
import raytracer.colour as colour
import raytracer.transformation as transformation
import raytracer.cartesian as cartesian


class TestPlanarShapeProdcedures(unittest.TestCase):

    def setUp(self):
        self.disc = planarshapes.shape_disc_create(
            colour.colour_create(.5, .5, .5),
            colour.colour_create(.5, .5, .5))
        self.disc2 = planarshapes.shape_disc_create(
            colour.colour_create(.1, .1, .1),
            colour.colour_create(.2, .2, .2),
            transformation.Transform({
                'scale': {'x': 2.0, 'y': 2.0, 'z': 1.0},
                'rotate': {'vector': cartesian.cartesian_create(1, 0, 0),
                           'angle': 30},
            }))

    def test_func_shape_disc_create(self):
        self.assertEqual(self.disc, ['shape', 'disc',
                                     ('colour', 0.5, 0.5, 0.5),
                                     ('colour', 0.5, 0.5, 0.5),
                                     planarshapes.shape_disc_intersect,
                                     None, None, None, None, {}])

        self.assertEqual(self.disc2[: 8], ['shape', 'disc',
                                           ('colour', 0.1, 0.1, 0.1),
                                           ('colour', 0.2, 0.2, 0.2),
                                           planarshapes.shape_disc_intersect,
                                           None,
                                           None, None])
        self.assertIsInstance(self.disc2[8], transformation.Transform)
        self.assertEqual(self.disc2[9], {})

    def test_func_shape_disc_intersect(self):

        pass

if __name__ == '__main__':
    unittest.main()

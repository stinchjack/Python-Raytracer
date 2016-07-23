import raytracer.shape as shape
import raytracer.planarshapes as planrshapes
import unittest


class TestEmptyShapeProdcedures(unittest.TestCase):

    def setUp(self):
        self.shape = shape.shape_empty_shape()

    def test_func_shape_empty_shape(self):
        self.assertEqual(self.shape, ['shape', None, None, None, None,
                                      None, None, None, None, {}])


if __name__ == '__main__':
    unittest.main()

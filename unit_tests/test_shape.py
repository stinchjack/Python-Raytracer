import shape
import planarshapes
import unittest

class TestEmptyShapeProdcedures(unittest.TestCase):
	def setUp(self):
		self.shape = shape.shape_empty_shape()
		
	def test_func_shape_empty_shape(self):		
		self.assertEqual (self.shape, ['shape', None, None, None, None, \
		None, shape.shape_diffuse_colour, shape.shape_specular_colour, None, {}])
		
	def test_func_shape_diffuse_colour(self):

		colour = shape.shape_diffuse_colour(self.shape, None)
		self.assertEqual (colour, None)
		
	def test_func_shape_specular_colour(self):
		colour = shape.shape_specular_colour(self.shape, None)
		self.assertEqual (colour, None)	
	
if __name__ == '__main__':
    unittest.main()
#shape_disc_intersect(shape, ray)
#shape_disc_create(colour, specular, transform=None):
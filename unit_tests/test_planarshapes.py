import planarshapes
import unittest
import shape
import math
import colour


class TestPlanarShapeProdcedures(unittest.TestCase):
	def setUp(self):
		self.disc = planarshapes.shape_disc_create(
			colour.colour_create(.5,.5,.5),
			colour.colour_create(.5,.5,.5))
				
	def test_func_shape_disc_create(self):
		self.assertEqual (self.disc, ['shape', 'disc', ('colour', 0.5, 0.5, 0.5),
			('colour', 0.5, 0.5, 0.5), planarshapes.shape_disc_intersect, \
			None, shape.shape_diffuse_colour, shape.shape_specular_colour, None, {}])

		disc2 = lanarshapes.shape_disc_create(
			colour.colour_create(.1,.1,.1),
			colour.colour_create(.2,.2,.2),
			Transform)
		
	def test_func_shape_disc_intersect(self):
		pass	
	
if __name__ == '__main__':
    unittest.main()

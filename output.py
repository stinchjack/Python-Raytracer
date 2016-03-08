"""
Classes for managing output from the raytracer. 
"""
from PIL import Image
from colour import *


class Output:
    """Abstract class covering all types of output."""

    def setRectangle(self, rectangle):
		"""Sets the rectangle for the output.
		
		rectangle: a dictionary with 'top','left','bottom', and 'right' values
		
		"""
        if not type(rectangle) is dict:
            return None
        if rectangle['left'] != 0:
            rectangle['right'] = rectangle['right'] - rectangle['left']
            rectangle['left'] = 0

        if rectangle['top'] != 0:
            rectangle['bottom'] = rectangle['bottom'] - rectangle['top']
            rectangle['top'] = 0

        self.rectangle = rectangle

    def setPixel(self, x, y, colour):
		"""
		Placeholder method for setting a colour at a specified co-ordinate 
		
		x: the x co-ordinate of the colour to set.
		y: the y co-ordinate of the colour to set.
		colour: the colour to set
		
		Returns: False
		"""
        return False

    def getOutput(self):
		"""
		Placeholder method for getting a generated image 

		Returns: None
		"""
        return None


class PIL_Output(Output):
    image = None
    pixels = None

    def setRectangle(self, rectangle):
        """Creates a new PIL Image based on the specified rectangle and readies it for use.
		
		rectangle: a dictionary with 'top','left','bottom', and 'right' values
		"""
        super().setRectangle(rectangle)
        self.image = Image.new(
            'RGB', (self.rectangle['right'], self.rectangle['bottom']))
        self.pixels = self.image.load()

    def setPixel(self, x, y, colour):
		""" Sets a colour at a specified co-ordinate 
		
		x: the x co-ordinate of the colour to set.
		y: the y co-ordinate of the colour to set.
		colour: the colour to set"""
	
        self.pixels[x, y] = (colour[1] * 255, colour[2] * 255, colour[3] * 255)

    def getOutput(self):
        """Returns the PIL image created"""
        return self.image

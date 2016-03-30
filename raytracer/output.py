"""
Classes for managing output from the raytracer.
"""
from PIL import Image
from raytracer.colour import *


class Output:
    """Abstract class covering all types of output."""

    def set_rectangle(self, rectangle):
        """Sets the rectangle for the output.

        :param rectangle: a dictionary with 'top', 'left',
                          'bottom', and 'right' values"""
        if not type(rectangle) is dict:
            return None
        if rectangle['left'] != 0:
            rectangle['right'] = rectangle['right'] - rectangle['left']
            rectangle['left'] = 0

        if rectangle['top'] != 0:
            rectangle['bottom'] = rectangle['bottom'] - rectangle['top']
            rectangle['top'] = 0

        self.rectangle = rectangle

    def set_pixel(self, x, y, colour):
        """Placeholder method for setting a colour at a specified co-ordinate

                :param x: the x co-ordinate of the colour to set.
                :param y: the y co-ordinate of the colour to set.
                :param colour: the colour to set

                :return: False
        """
        return False

    def get_output(self):
        """
                Placeholder method for getting a generated image

                :return: None
                """
        return None


class PIL_Output(Output):
    image = None
    pixels = None

    def set_rectangle(self, rectangle):
        """Creates a new PIL Image based on the specified rectangle and
        readies it for use.

                :param rectangle: a dictionary with 'top', 'left', 'bottom',
                                  and 'right' values"""
        super().set_rectangle(rectangle)
        self.image = Image.new(
            'RGB', (self.rectangle['right'], self.rectangle['bottom']))
        self.pixels = self.image.load()

    def set_pixel(self, x, y, colour):
        """ Sets a colour at a specified co-ordinate

                :param x: the x co-ordinate of the colour to set.
                :param y: the y co-ordinate of the colour to set.
                :param colour: the colour to set"""

        self.pixels[x, y] = (colour[1] * 255, colour[2] * 255, colour[3] * 255)

    def get_output(self):
        """Returns the PIL image created"""
        return self.image

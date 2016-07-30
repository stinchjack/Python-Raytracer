

try:
    from PIL import Image
    has_PIL = True
except ImportError:
    has_PIL = False

from raytracer.colour import *

""" Classes for managing output from the raytracer"""


class Output:
    """Abstract class covering all types of output"""

    def set_rectangle(self, rectangle):
        """Sets the rectangle for the output.

        :param rectangle: a dictionary with 'top', 'left',
                          'bottom', and 'right' value"""
        if not type(rectangle) is dict:
            return None
        if rectangle['left'] != 0:
            rectangle['right'] = rectangle['right'] - rectangle['left']
            rectangle['left'] = 0

        if rectangle['top'] != 0:
            rectangle['bottom'] = rectangle['bottom'] - rectangle['top']
            rectangle['top'] = 0

        self.__rectangle__ = rectangle

    def set_pixel(self, x, y, colour):
        """Placeholder method for setting a colour at a specified co-ordinate

        :param x: the x co-ordinate of the colour to set.
        :param y: the y co-ordinate of the colour to set.
        :param colour: the colour to set

        :return: False"""

        return False

    def get_output(self):
        """Placeholder method for getting a generated image

        :return: None"""
        return None

if has_PIL:
    class PIL_Output(Output):
        __image__ = None
        __pixels__ = None

        def set_rectangle(self, rectangle):
            """Creates a new PIL Image based on the specified rectangle and
            readies it for use.

            :param rectangle: a dictionary with 'top', 'left', 'bottom',
                              and 'right' value"""
            super().set_rectangle(rectangle)
            self.__image__ = Image.new(
                'RGB', (self.__rectangle__['right'], self.__rectangle__['bottom']))
            self.__pixels__ = self.__image__.load()

        def set_pixel(self, x, y, colour):
            """ Sets a colour at a specified co-ordinate

                    :param x: the x co-ordinate of the colour to set.
                    :param y: the y co-ordinate of the colour to set.
                    :param colour: the colour to set"""

            colour = ['colour', colour[1], colour[2], colour[3]]
            if colour[1] < 0:
                colour[1] = 0
            if colour[2] < 0:
                colour[2] = 0
            if colour[3] < 0:
                colour[3] = 0
            	# import pdb; pdb.set_trace();
            try:
	            self.__pixels__[x, y] = (
	                int(colour[1] * 255), int(colour[2] * 255), int(colour[3] * 255))
            except:
	            import pdb;pdb.set_trace();

        def get_output(self):
            """Returns the PIL image created"""
            return self.__image__

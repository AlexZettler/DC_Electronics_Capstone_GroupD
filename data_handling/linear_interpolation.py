"""
Created by author: Lauritz V. Thaulow
Created on: September 8, 2011

Posed to stack Overflow linked below:
    https://stackoverflow.com/questions/7343697/how-to-implement-linear-interpolation

Modified by: Alexander Zettler
Modified on: March 8, 2019
    Modified to support edge cases, increase readability, and create documentation.
"""

from bisect import bisect_left


class Line(object):
    def __init__(self, x1, x2, y1, y2):
        # Empty initialization
        self._x1, self._x2 = None, None
        self._y1, self._y2 = None, None
        self.m = None
        self.b = None

        # Define our points
        self.x1, self.x2 = x1, x2
        self.y1, self.y2 = y1, y2

        self.recalculate()

    def recalculate(self):
        delta_x = self._x2 - self._x1
        delta_y = self._y2 - self._y1

        self.m = delta_y / delta_x
        self.b = self._y1 - (self._x1 * self.m)

    @property
    def x1(self):
        return self._x1

    @x1.setter
    def x1(self, other):
        self._x1 = other

    @property
    def x2(self):
        return self._x1

    @x2.setter
    def x2(self, other):
        self._x2 = other

    @property
    def y1(self):
        return self._y1

    @y1.setter
    def y1(self, other):
        self._y1 = other

    @property
    def y2(self):
        return self._y2

    @y2.setter
    def y2(self, other):
        self._y2 = other

    def __getitem__(self, item):
        return self.m * item + self.b

    @staticmethod
    def test_line():
        l = Line(0, 10, -2, 2)
        assert l[0] == -2
        assert l[2.5] == -1
        assert l[5] == 0
        assert l[7.5] == 1
        assert l[10] == 2
        assert l[20] == 6


class Interpolate(object):
    """
    This class is used to get linearly interpolated data points given a list of
    """

    # todo: Implement each section lookup as a line object

    def __init__(self, x_list: list, y_list: list):

        # Verify that x point are in ascending order
        if any(y - x <= 0 for x, y in zip(x_list, x_list[1:])):
            raise ValueError("x_list must be in strictly ascending order!")

        # Create new lists of floating point values from the two lists
        self.x_list = [float(x) for x in x_list]
        self.y_list = [float(y) for y in y_list]

        # Create an x1,x2,y1,y2 structure to construct slopes from
        intervals = zip(x_list, x_list[1:], y_list, y_list[1:])

        # Calculate a list of slopes from x and y deltas
        self.slopes = [(y2 - y1) / (x2 - x1) for x1, x2, y1, y2 in intervals]

    def __getitem__(self, x):
        """
        Retrieves a y value given an x point on the graph

        :param x: The x point to interpolate from
        :return: The y value at this point
        """

        # Handle edge cases
        try:
            return self.y_list[x]

        # Handle cases between x points
        except KeyError:
            i = bisect_left(self.x_list, x) - 1
            y = self.y_list[i] + self.slopes[i] * (x - self.x_list[i])
            return y


if __name__ == "__main__":
    Line.test_line()

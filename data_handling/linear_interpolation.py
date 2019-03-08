"""
Created by author: Lauritz V. Thaulow
Created on: September 8, 2011

Modified by: Alexander Zettler
Modified on: March 8, 2019
    Modified to support edge cases, increase readability, and create documentation.

Posed to stack Overflow linked below:
    https://stackoverflow.com/questions/7343697/how-to-implement-linear-interpolation
"""

from bisect import bisect_left


class Line(object):
    def __init__(self, x1, x2, y1, y2):
        delta_x = x2 - x1
        delta_y = y2 - y1

        self.m = delta_y / delta_x
        self.b = y2

    def __getitem__(self, item):
        y = self.m * item + self.b
        return y


class Interpolate(object):
    """
    This class is used to get linearly interpolated data points given a list of
    """

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
    pass

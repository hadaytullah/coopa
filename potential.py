"""Base implementation of a potential field.
"""

import numpy as np


class PotentialField:
    """Base implementation of a potential field.

    Holds property :attr:`field` which is the current potential field and some basic field manipulation methods.
    """

    def __init__(self, width, height):
        self._pf = np.zeros((width, height))

    @property
    def field(self):
        return self._pf

    def update(self, x, y, val):
        self._pf[x, y] = val

    def add(self, x, y, val):
        self._pf[x, y] += val

    def subtract(self, x, y, val):
        self._pf[x, y] -= val

    def update_mask(self, x, y, mask):
        """Update a rectangular area of the potential field where (x, y) is the upper left corner of the rectangle.
        """
        s = mask.shape
        self._pf[x:x+s[0], y:y+s[1]] = mask

    def add_mask(self, x, y, mask):
        s = mask.shape
        self._pf[x:x+s[0], y:y+s[1]] += mask

    def subtract_mask(self, x, y, mask):
        s = mask.shape
        self._pf[x:x+s[0], y:y+s[1]] -= mask



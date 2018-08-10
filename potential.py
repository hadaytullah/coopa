"""Base implementation of a potential field.
"""
import random

import numpy as np

# Clock wise index differences from a center point, starting from the upper left corner.
clock_wise = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]
clock_wise4 = [(-1, 0), (0, 1), (1, 0), (0, -1)]


class PotentialField:
    """Base implementation of a potential field.

    Holds property :attr:`field` which is the current potential field and some basic field manipulation methods.
    """

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self._pf = np.zeros((width, height))

    @property
    def field(self):
        """Current potential field as 2D real valued numpy matrix.
        """
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

    def follow(self, pos, impassable=None, moore=True):
        """Follow potential field from a given position to the descending direction.

        :param tuple pos: Current position.
        :param impassable: Optional 2D numpy matrix where impassable cells are marked with values smaller than zero.
        :param bool moore: Are diagonal movements allowed (True) or not (False).
        """
        neighbor_deltas = clock_wise if moore else clock_wise4

        current_min = self._pf[pos]
        min_deltas = [(0, 0)]
        for delta in neighbor_deltas:
            new_pos = (pos[0] + delta[0], pos[1] + delta[1])
            if 0 <= new_pos[0] < self._pf.shape[0] and 0 <= new_pos[1] < self._pf.shape[1]:
                current = self._pf[new_pos]
                if impassable is not None and impassable[new_pos] < 0:
                    # Impassable terrain
                    pass
                elif current < current_min:
                    current_min = current
                    min_deltas = [delta]
                elif current == current_min:
                    min_deltas.append(delta)

        delta = random.choice(min_deltas)
        new_pos = (pos[0] + delta[0], pos[1] + delta[1])
        return new_pos



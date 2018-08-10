"""Potential field which draws the agent towards the nearest hot spot.
"""
import numpy as np

from search.bfs import bfs
from potential import PotentialField


class HotSpotPotentialField(PotentialField):
    """Potential field which has one or several hot spots. The potential (monotonously) decreases towards the hot spots.

    That is, following the potential field to the descending direction will bring the agent to the nearest hot spot
    (given that the agent's current belief of the environment is valid).
    """

    def __init__(self, width, height, hot_spots):
        super().__init__(width, height)
        self._hot_spots = set(hot_spots)

    @property
    def hot_spots(self):
        """Currently known hot spots.
        """
        return self._hot_spots

    def add_hot_spot(self, hot_spot):
        if hot_spot not in self._hot_spots:
            self._hot_spots.add(hot_spot)

    def remove_hot_spot(self, hot_spot):
        try:
            self._hot_spots.remove(hot_spot)
        except KeyError:
            pass

    def update(self, map, moore=True):
        """Update potential field with agent's new belief of the current map (passable cells).

        :param map: 2D numpy array, agent's current belief of the environment where zeros are passable cells.
        :param bool moore: Is the agent able to move diagonally (True) or not (False).
        """
        if map.shape != self.field.shape:
            raise ValueError("Map's shape must be the same as the field's shape. Now {} != {}"
                             .format(map.shape, self.field.shape))

        if len(self._hot_spots) == 0:
            self._pf = np.zeros((self.width, self.height))
            return

        hot_spot_fields = []
        for hot_spot in self._hot_spots:
            hot_spot_field = bfs(map, hot_spot, moore=moore)
            hot_spot_fields.append(hot_spot_field)

        if len(hot_spot_fields) == 1:
            self._pf = hot_spot_fields[0]
        else:
            self._pf = np.minimum.reduce(hot_spot_fields)






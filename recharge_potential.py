"""Potential field for recharging stations.
"""
import numpy as np

from search.bfs import bfs
from potential import PotentialField


class RechargePotentialField(PotentialField):
    """Following the potential field to the descending direction will bring the agent to the nearest recharge station
    (given that the agent's current belief of the environment is valid).
    """

    def __init__(self, width, height, recharge_points):
        super.__init__(width, height)
        self._rps = set(recharge_points)

    @property
    def recharge_points(self):
        """Currently known places of recharge points.
        """
        return self._rps

    def add_recharge_point(self, rp):
        if rp not in self._rps:
            self._rps.add(rp)

    def remove_recharge_point(self, rp):
        try:
            self._rps.remove(rp)
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

        if len(self._rps) == 0:
            raise ValueError("Cannot compute the potential field because the set of recharge points is empty.")

        rp_fields = []
        for rp in self._rps:
            rp_field = bfs(map, rp, moore=moore)
            rp_fields.append(rp_field)

        if len(rp_fields) == 1:
            self._pf = rp_fields[0]
        else:
            self._pf = np.minimum.reduce(rp_fields)






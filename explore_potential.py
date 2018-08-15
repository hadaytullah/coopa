import cv2
import numpy as np

from search.bfs import bfs
from hot_spot_potential import HotSpotPotentialField


class ExplorePotentialField(HotSpotPotentialField):
    """Potential field for agent's exploration goal.

    Following this potential field, the agent tries to first explore the whole map (see every cell once) and is then
    driven towards cells that have not been seen in the longest time.
    """

    def __init__(self, width, height, hot_spots):
        super().__init__(width, height, hot_spots)

    def update(self, map, pos, current_clock, seen_time, moore=True):
        """Update explore potential field given agents belief of the current map (passable cells) and when each
        cell was last seen.

        :param map:
            2D numpy array of the currently known passable (>=0) and impassable (<0) cells.
        :param tuple pos:
            Agent's current location
        :param int current_clock:
            Current time, i.e. the simulation step.
        :param seen_time:
            2D numpy array representing the time when each cell was last seen. Unseen cells are marked as -1.
        :param bool moore:
            Are diagonal movements allowed (True) or not (False).
        """
        # TODO: threshold seen_time in relation to current_clock?
        unseen = np.array(seen_time < 0, dtype=np.uint8)
        distance_type = cv2.DIST_C if moore else cv2.DIST_L1

        # If we have not seen every cell already, we go for nearest unseen cell which we think is reachable.
        if not np.all(unseen):
            # Compute distance to the nearest seen cell from each unseen cell.
            distances = cv2.distanceTransform(unseen, distanceType=distance_type, maskSize=3)
            # Border pixels are the unseen cells which are next to any seen cell
            border_indices = np.nonzero(distances == 1)
            border_indices_t = np.transpose(border_indices)
            # Compute distances from current agent's location to every reachable cell
            dist_from_pos = bfs(map, pos)
            # np.set_printoptions(threshold=np.nan, linewidth=220)
            # print(dist_from_pos)
            # Remove border cells that are not reachable
            border_indices = [index for index in border_indices_t if dist_from_pos[tuple(index)] >= 0]
            if len(border_indices) == 0:
                print("No unseen reachable cells left!")
                self._hot_spots = set([])
                super().update(map, moore=moore)
            else:
                # Select border pixel which is closest to the agent's current position and put it as a hot spot.
                border_indices = np.transpose(border_indices)
                argmin = np.argmin(dist_from_pos[border_indices[0], border_indices[1]], axis=None)
                self._hot_spots = set([tuple(np.transpose(border_indices)[argmin, :])])
                #print("ARGMIN", argmin, self._hot_spots)
                super().update(map, moore=moore)
        else:
            print("All cells seen!!")













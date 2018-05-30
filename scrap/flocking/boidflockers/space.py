import numpy as np

from mesa.space import ContinuousSpace


class FixedContinuousSpace(ContinuousSpace):

    def get_heading(self, pos_1, pos_2):
        one = np.array(pos_1)
        two = np.array(pos_2)
        heading = two - one
        if self.torus:
            if heading[0] > self.size[0] / 2:
                heading[0] = two[0] - (one[0] + self.size[0])
            elif heading[0] < -self.size[0] / 2:
                heading[0] = (two[0] + self.size[0]) - one[0]
            if heading[1] > self.size[1] / 2:
                heading[1] = two[1] - (one[1] + self.size[1])
            elif heading[1] < -self.size[1] / 2:
                heading[1] = (two[1] + self.size[1]) - one[1]
        #heading = two - one
        if isinstance(pos_1, tuple):
            heading = tuple(heading)
        return heading
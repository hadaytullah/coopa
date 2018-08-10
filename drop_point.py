from mesa import Agent
from mesa.time import RandomActivation
import random


class DropPoint(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self._trash_count = 0
        self.name = "DropPoint#{:0<3}".format(self.unique_id)

    @property
    def trash_count (self):
        return self._trash_count

    def pick_trash(self, num):
        self._trash_count += num

    def drop_trash(self, num):
        self._trash_count -= num
        if self._trash_count < 0:
            self._trash_count = 0

    def step(self):
        print(self)

    def __repr__(self):
        return "{}(cp:{}, rc:{})".format(self.name, self.pos, self._trash_count)

    def __str__(self):
        return self.__repr__()


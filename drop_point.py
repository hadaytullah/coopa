from mesa import Agent
from mesa.time import RandomActivation
import random


class DropPoint(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self._resource_count = 0
        self.name = "DropPoint#{:0<3}".format(self.unique_id)

    @property
    def resource_count (self):
        return self._resource_count

    def add_resources (self, num):
        self._resource_count += num

    def remove_resources (self, num):
        self._resource_count -= num

    def step(self):
        print(self)

    def __repr__(self):
        return "{}(cp:{}, rc:{})".format(self.name, self.pos, self._resource_count)

    def __str__(self):
        return self.__repr__()


from mesa import Agent
from mesa.time import RandomActivation
import random

class Resource(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self._resource_count = 1

    @property
    def resource_count (self):
        return self._resource_count

    def add_resources (self, num):
        self._resource_count+=count

    def remove_resources (self, num):
        self._resource_count-=num

    #def step(self):
    #    pass
        #pint('drop point has resources: %s'.format(self.resource_count))


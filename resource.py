from mesa import Agent
from mesa.time import RandomActivation
import random

class Resource(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.resource_count = 1

    def step(self):
        pass
        #pint('drop point has resources: %s'.format(self.resource_count))


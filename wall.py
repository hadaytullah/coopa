from mesa import Agent
from mesa.time import RandomActivation
import random

class Wall(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass


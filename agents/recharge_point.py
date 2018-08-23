from mesa import Agent
from mesa.time import RandomActivation
import random

class RechargePoint(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self._resource_count = 0

    @property
    def resource_count (self):
        return self._resource_count

    def add_resources (self, num):
        self._resource_count+=num

    def remove_resources (self, num):
        self._resource_count-=num

    def step(self):
        print('This is a recharge point point. Ping!')


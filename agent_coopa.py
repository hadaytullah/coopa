from agent_basic import AgentBasic
from mesa.time import RandomActivation
from resource import Resource
from drop_point import DropPoint
import random

# TODO: add cooperation awareness
class AgentCoopa(AgentBasic):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.wealth = 1 #random.choice([0,5])
    
    def step(self):
        super(AgentCoopa,self).step()
        #self.move()
        #self.pick_resource()

    def receive(self, message):
        if type(message) is Message:
            self.destination_x = message.resource_x
            self.destination_y = message.resource_y
    
    #def move(self):
    #    super(self).move()
    
    #def pick_resource(self):
    #    super(self).pick_resource()

from agent_basic import AgentBasic
from mesa.time import RandomActivation
from resource import Resource
from drop_point import DropPoint
import random

# TODO: add cooperation awareness
class Message:
    def __init__(self, sender, resource_x, resource_y):
        self.sender = sender
        self.resource_x = resource_x
        self.resource_y = resource_y


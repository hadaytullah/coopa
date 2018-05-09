from agent_basic import AgentBasic
from mesa.time import RandomActivation
from resource import Resource
from drop_point import DropPoint
import random

# TODO: add cooperation awareness
class Message:
    def __init__(self, sender, resource_x, resource_y):
        self._sender = sender
        self._resource_x = resource_x
        self._resource_y = resource_y

    @property
    def sender (self):
        return self._sender

    @property
    def resource_x (self):
        return self._resource_x

    @property
    def resource_y (self):
        return self._resource_x




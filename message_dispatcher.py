from agent_basic import AgentBasic
from mesa.time import RandomActivation
from resource import Resource
from drop_point import DropPoint
import random

# TODO: add cooperation awareness
class MessageDispatcher:

    def __init__(self, agents):
        self.agents = agents

    def broadcast(self, message):
        print('Broad casting for agent#%i'.format(message.sender.unique_id))
        for agent in self.agents:
            if agent is not message.sender:
                agent.receive(sender, message)

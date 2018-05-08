from agent_basic import AgentBasic
from mesa.time import RandomActivation
from resource import Resource
from drop_point import DropPoint
import random

# TODO: add cooperation awareness
class MessageDispatcher:

    def __init__(self):
        self.agents = []

    def broadcast(self, message):
        print('-- Broad casting for agent# {}'.format(message.sender.unique_id))
        for agent in self.agents:
            if agent is not message.sender:
                agent.receive(message)

    def register(self, agent):
        self.agents.append(agent)

    def unregister(self, agent):
        self.agents.remove(agent)


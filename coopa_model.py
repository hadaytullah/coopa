from mesa import Model
from agent_basic import AgentBasic
from agent_coopa import AgentCoopa
from resource import Resource
from drop_point import DropPoint
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from message_dispatcher import MessageDispatcher
import random

def compute_gini(model):
    agent_resources = [agent.resource_count for agent in model.schedule.agents]
    x = sorted(agent_resources)
    N = model.num_agents
    B = sum( xi * (N-i) for i,xi in enumerate(x) ) / (N*sum(x))
    return (1 + (1/N) - 2*B)

class CoopaModel(Model):
    """A model with some number of agents."""
    def __init__(self, N, width, height):
        self.running = True
        self.num_agents = N
        self.num_resources = 20
        self.grid = MultiGrid(width, height, True) #True=toroidal
        self.schedule = RandomActivation(self)
        self.message_dispatcher = MessageDispatcher()
        #self.agents = []
        # adding a single drop point

        #self.grid.place_agent(DropPoint(1, self), (0,0))
        #self.grid.place_agent(DropPoint(1, self), (0,height-1))
        #self.grid.place_agent(DropPoint(1, self), (width-1,0))
        #self.grid.place_agent(DropPoint(1, self), (width-1,height-1))

        # adding many drop points, will fixed and few later
        for i in range(10):
            drop_point = DropPoint(i, self)
            self.schedule.add(drop_point)

            #add to grid
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(drop_point, (x,y)) # agent.pos has (x,y)

        # adding initial resources
        for i in range(self.num_resources):
            resource = Resource(i, self)
            self.schedule.add(resource)

            #add to grid
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(resource, (x,y)) # agent.pos has (x,y)

        # the mighty agents arrive
        for i in range(self.num_agents):
            a = AgentCoopa(i, self)
            #self.agents.add(a)
            self.schedule.add(a)
            
            #add to grid
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(a, (x,y)) # agent.pos has (x,y)

        #let messaging bus know about agents
        #self.message_dispatcher.set_agents(self.agents)

        #data collector, don't really know how it works yet
        self.datacollector = DataCollector(
            model_reporters={"Gini": compute_gini},  # A function to call
            agent_reporters={"Resource": "resource_count"})  # An agent attribute
            
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

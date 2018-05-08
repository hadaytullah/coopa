from mesa import Model
from agent_basic import AgentBasic
from agent_coopa import AgentCoopa
from resource import Resource
from drop_point import DropPoint
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import random

def compute_gini(model):
    agent_wealths = [agent.wealth for agent in model.schedule.agents]
    x = sorted(agent_wealths)
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

        # adding a single drop point
        drop_point = DropPoint(1, self)
        self.grid.place_agent(drop_point, (0,0))

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
            self.schedule.add(a)
            
            #add to grid
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(a, (x,y)) # agent.pos has (x,y)

        #data collector, don't really know how it works yet
        self.datacollector = DataCollector(
            model_reporters={"Gini": compute_gini},  # A function to call
            agent_reporters={"Wealth": "wealth"})  # An agent attribute
            
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

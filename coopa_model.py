from mesa import Model
from agent_coopa import AgentCoopa
from mesa.time import RandomActivation
from mesa.space import MultiGrid
import random


class CoopaModel(Model):
    """A model with some number of agents."""
    def __init__(self, N, width, height):
        self.num_agents = N
        self.grid = MultiGrid(width, height, True) #True=toroidal
        self.schedule = RandomActivation(self)
        # Create agents
        for i in range(self.num_agents):
            a = AgentCoopa(i, self)
            self.schedule.add(a)
            
            #add to grid
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(a, (x,y)) # agent.pos has (x,y)
            
    def step(self):
        self.schedule.step()
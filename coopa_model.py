from mesa import Model
from resource import Resource
from drop_point import DropPoint
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector
from message_dispatcher import MessageDispatcher
from layout import Layout
from ui_styling import AGENT_TYPES

def compute_gini(model):
    agent_resources = [agent.resource_count for agent in model.schedule.agents]
    x = sorted(agent_resources)
    N = model.num_agents
    B = sum( xi * (N-i) for i,xi in enumerate(x) ) / (N*sum(x))
    return (1 + (1/N) - 2*B)

class CoopaModel(Model):
    """A model with some number of agents."""
    def __init__(self, N, width, height, agent_type):
        self.running = True
        self.num_agents = N
        self.num_resources = 20
        self.grid = SingleGrid(width, height, False) #True=toroidal
        self.schedule = RandomActivation(self)
        self.message_dispatcher = MessageDispatcher()
        self.layout = Layout()
        self.agent_type = AGENT_TYPES[agent_type]
        #self.agents = []
        # adding a single drop point

        #self.grid.place_agent(DropPoint(1, self), (0,0))
        #self.grid.place_agent(DropPoint(1, self), (0,height-1))
        #self.grid.place_agent(DropPoint(1, self), (width-1,0))
        #self.grid.place_agent(DropPoint(1, self), (width-1,height-1))

        self.layout.draw(self.grid)
        # adding many drop points, will fixed and few later
        for i in range(10):
            drop_point = DropPoint(i, self)
            self.schedule.add(drop_point)
            self.grid.position_agent(drop_point)

            #add to grid
            #x = random.randrange(self.grid.width)
            #y = random.randrange(self.grid.height)
            #self.grid.place_agent(drop_point, (x,y)) # agent.pos has (x,y)
            #self.grid.move_to_empty(drop_point)

        # adding initial resources
        for i in range(self.num_resources):
            resource = Resource(i, self)
            self.schedule.add(resource)
            self.grid.position_agent(resource)
#            #add to grid
#            x = random.randrange(self.grid.width)
#            y = random.randrange(self.grid.height)
#            self.grid.place_agent(resource, (x,y)) # agent.pos has (x,y)
#            self.grid.move_to_empty(resource)

        # the mighty agents arrive
        for i in range(self.num_agents):
            a = self.agent_type(i, self)
            #self.agents.add(a)
            self.schedule.add(a)
            self.grid.position_agent(a)
            
#            #add to grid
#            x = random.randrange(self.grid.width)
#            y = random.randrange(self.grid.height)
#            self.grid.place_agent(a, (x,y)) # agent.pos has (x,y)
#            self.grid.move_to_empty(a)

        #let messaging bus know about agents
        #self.message_dispatcher.set_agents(self.agents)

        #data collector, don't really know how it works yet
        self.datacollector = DataCollector(
            model_reporters={"Gini": compute_gini},  # A function to call
            agent_reporters={"Resource": "resource_count"})  # An agent attribute

            
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

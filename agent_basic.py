from mesa import Agent
from mesa.time import RandomActivation
from resource import Resource
from drop_point import DropPoint
import random


class AgentBasic(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.resource_count = 1 #random.choice([0,5])

    def step(self):
        self.move()
        self.pick_resource()


    def move(self):
        #moore: up,down,left,right and diagonal movements
        #von neumann: up, down, left, right
        # include_center = false, mean do not consider its current location
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        new_position = random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def pick_resource(self):
        print('AgentBasic#%s, before resource_count, %i' %(self.unique_id,self.resource_count))
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) > 1:
            other = random.choice(cellmates)
            if type(other) is Resource:
                other.resource_count -= 1
                self.resource_count += 1
                self.model.grid.remove_agent(other)
            elif type(other) is DropPoint:
                other.resource_count += self.resource_count
                self.resource_count = 0

        print('AgentBasic#%s, after resource_count, %i' %(self.unique_id,self.resource_count))

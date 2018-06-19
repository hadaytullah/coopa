from mesa import Agent
from mesa.time import RandomActivation
from resource import Resource
from drop_point import DropPoint
import random


class AgentBasic(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self._resource_count = 1 #random.choice([0,5])
       
    @property
    def resource_count (self):
        return self._resource_count
    
    @property
    def battery_power (self):
        return self._battery_power

    def add_resources (self, num):
        self._resource_count+=count

    def remove_resources (self, num):
        self._resource_count-=num

    def step(self):
       
        self.move()
        self.process()

    def move(self):
        #moore: up,down,left,right and diagonal movements
        #von neumann: up, down, left, right
        # include_center = false, mean do not consider its current location
        possible_steps = []
        for cell in self.model.grid.iter_neighborhood(self.pos, moore=True):
            #print('cell is empty {}'.format(cell))
            if self.model.grid.is_cell_empty(cell):
                print('cell is empty {}'.format(cell))
                possible_steps.append(cell)
        if len(possible_steps) > 0:
            new_position = random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)

    def process(self):
        print('AgentBasic#%s, before resource_count, %i' %(self.unique_id,self._resource_count))
        #cellmates = self.model.grid.get_cell_list_contents([self.pos])
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=1)
        for neighbor in neighbors:
            if type(neighbor) is Resource:
                self._resource_count += 1
                self.model.grid.remove_agent(neighbor)
            elif type(neighbor) is DropPoint:
                neighbor.add_resources(self._resource_count)
                self._resource_count = 0

        print('AgentBasic#%s, after resource_count, %i' %(self.unique_id,self._resource_count))

    def process_(self):
        print('AgentBasic#%s, before resource_count, %i' %(self.unique_id,self._resource_count))
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) > 1:
            other = random.choice(cellmates)
            if type(other) is Resource:
                self._resource_count += 1
                self.model.grid.remove_agent(other)
            elif type(other) is DropPoint:
                other.add_resources(self._resource_count)
                self._resource_count = 0

        print('AgentBasic#%s, after resource_count, %i' %(self.unique_id,self._resource_count))

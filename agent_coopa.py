from mesa import Agent
from mesa.time import RandomActivation
import random

class AgentCoopa(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.wealth = random.choice([0,5])
    
    def step_(self):
        print('AgentCoopa#%s, before wealth, %i' %(self.unique_id,self.wealth))
        if self.wealth == 0:
            return
        else:
            other_agent = random.choice(self.model.schedule.agents)
            other_agent.wealth += 1
            self.wealth -= 1
        print('AgentCoopa#%s, after wealth, %i' %(self.unique_id,self.wealth))
    
    def step(self):
        self.move()
        if self.wealth > 0:
            self.give_money()
    
    def move(self):
        #moore: up,down,left,right and diagonal movements
        #von neumann: up, down, left, right
        # include_center = false, mean do not consider its current location
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        new_position = random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)
    
    def give_money(self):
        print('AgentCoopa#%s, before wealth, %i' %(self.unique_id,self.wealth))
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) > 1:
            other = random.choice(cellmates)
            other.wealth += 1
            self.wealth -= 1
        print('AgentCoopa#%s, after wealth, %i' %(self.unique_id,self.wealth))

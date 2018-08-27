import logging
import random

from mesa import Agent

from .trash import Trash
from .trashcan import Trashcan
from battery import Battery


class BasicAgent(Agent):
    def __init__(self, unique_id, model, log_path=None):
        super().__init__(unique_id, model)
        self._trash_count = 0
        self._log_path = log_path
        self._battery = Battery(320)

    @property
    def time(self):
        return self.model.time
       
    @property
    def trash_count(self):
        return self._trash_count

    @property
    def battery(self):
        return self._battery

    def pick_trash(self, num):
        self._trash_count += num

    def drop_trash(self, num):
        self._trash_count -= num

    def step(self):
        self.observe()
        self.move()
        self.process()

    def observe(self):
        pass

    def move(self):
        #moore: up,down,left,right and diagonal movements
        #von neumann: up, down, left, right
        # include_center = false, mean do not consider its current location
        possible_steps = []
        for cell in self.model.grid.iter_neighborhood(self.pos, moore=True):
            #print('cell is empty {}'.format(cell))
            if self.model.grid.is_cell_empty(cell):
                #print('cell is empty {}'.format(cell))
                possible_steps.append(cell)
        if len(possible_steps) > 0:
            new_position = random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)

    def process(self):
        print('AgentBasic#%s, before trash_count, %i' % (self.unique_id,self._trash_count))
        #cellmates = self.model.grid.get_cell_list_contents([self.pos])
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=1)
        for neighbor in neighbors:
            if type(neighbor) is Trash:
                self._trash_count += 1
                self.model.grid.remove_agent(neighbor)
            elif type(neighbor) is Trashcan:
                neighbor.pick_trash(self._trash_count)
                self._trash_count = 0

        print('AgentBasic#%s, after trash_count, %i' % (self.unique_id, self._trash_count))

    def process_(self):
        print('AgentBasic#%s, before trash_count, %i' % (self.unique_id, self._trash_count))
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) > 1:
            other = random.choice(cellmates)
            if type(other) is Trash:
                self._trash_count += 1
                self.model.grid.remove_agent(other)
            elif type(other) is Trashcan:
                other.pick_trash(self._trash_count)
                self._trash_count = 0

        print('AgentBasic#%s, after trash_count, %i' % (self.unique_id, self._trash_count))

    def _log(self, msg, lvl=logging.DEBUG):
        self._logger.log(lvl, msg, extra={'time': self.time})

from agent_basic import AgentBasic
from mesa.time import RandomActivation
from resource import Resource
from drop_point import DropPoint
from message import Message
from cooperation import Cooperation
from awareness import Awareness
from knowledge_base import KnowledgeBase
from recharge_point import RechargePoint
from wall import Wall
import search
from utils import get_line
import random
import pdb
import numpy as np


class AgentCoopa(AgentBasic):
    """AgentCoopa cooperates with other agents"""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

        model.message_dispatcher.register(self)

        #self._resource_count = 1 #random.choice([0,5])
        #self._pos_resource = None # potential resource location
        #self._pos_drop_point = None # they shall discover the drop point

        #self._cooperation = {}
        self._capacity = random.choice([1,2,3])
        self._awareness = Awareness(self)

        # Create map of the environment for the agent, i.e. the agent knows its environment beforehand.
        self._map = search.build_map(model.grid, [Wall])

        #self._knowledge_base = KnowledgeBase()

        # self._goals = {
        #     'random':{
        #         'name' : 'random',
        #         'pos' : None # potential resource location
        #     },
        #     'find_resource':{
        #         'name' : 'find_resource',
        #         'pos' : None # potential resource location
        #     },
        #     'find_drop_point':{
        #         'name' : 'find_drop_point',
        #         'pos' : None # potential drop point location

        #     }
        # }

        #self._current_goal = self._goals['find_resource']
        #self._current_goal = self._knowledge_base.goals['random']
        self._target_pos = None
         # resource
        self._battery_power = 320 # each step will consume one unit
        self._is_recharging = False
        self.scan_radius = 5
        
    
    def step(self):
        if self._battery_power > 0:
            if self._is_recharging is False:
                self._awareness.step()
                super(AgentCoopa,self).step()
                self._battery_power -= 1
            else:
                print ("Agent#{} is recharging.".format(self.unique_id)) 
                self._recharge_battery()   
        else:
            print ("Agent#{} out of power.".format(self.unique_id))

    def receive(self, message):
        self._awareness.cooperation_awareness(message) #have to improve this, temporary solution
    
    def _recharge_battery(self):
        self._battery_power += 10
        if self._battery_power >= 320:
            self._is_recharging = False

    @property
    def target_pos(self):
        return self._target_pos

    @target_pos.setter
    def target_pos(self, position):
        self._target_pos = position

    @property
    def capacity(self):
        return self._capacity
    
    @property
    def battery_power(self):
        return self._battery_power

    def move(self):
        #if self._current_goal is not None and self._current_goal['pos'] is not None:
        if self._target_pos is not None:
            self._move_towards_point(self._target_pos)
        else:
            super(AgentCoopa, self).move()

#        if self._current_goal['name'] is 'find_resource' and random.randrange(1,100) < 50:
#                self._move_towards_point (self._current_goal['pos'])
#        elif self._current_goal['name'] is 'find_drop_point' and self._current_goal['pos'] is not None:
#            self._move_towards_point (self._current_goal['pos'])
#        else:
#            super(AgentCoopa,self).move()

    def _move_towards_point(self, point):
        #print('-- destination point {}'.format(point))
        #pdb.set_trace()
        #moore: up,down,left,right and diagonal movements
        #von neumann: up, down, left, right
        # include_center = false, mean do not consider its current location
        #possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        possible_steps = []
        for cell in self.model.grid.iter_neighborhood(self.pos, moore=True):
            #print('cell is empty {}'.format(cell))
            if self.model.grid.is_cell_empty(cell):
                #print('cell is empty {}'.format(cell))
                possible_steps.append(cell)

        if len(possible_steps) > 0:
            # find the step that takes the agent closer to a resource
            # assuming that other resources exisits in proximity of a found resource
            x_distance_shortest = abs(possible_steps[0][0] - point[0])
            y_distance_shortest = abs(possible_steps[0][1] - point[1])
            new_position = possible_steps[0]

            for step in possible_steps:
                x_distance = abs(step[0] - point[0])
                y_distance = abs(step[1] - point[1])
                #print('step:{}, x_distance:{} , y_distance:{}'.format(step, x_distance, y_distance))
                if x_distance <= x_distance_shortest and y_distance <= y_distance_shortest:
                    new_position = step
                    #print('new position for agent#{}: {}'.format(self.unique_id, new_position))
                    x_distance_shortest = x_distance
                    y_distance_shortest = y_distance

            #new_position = random.choice(possible_steps)
            #print('new position for agent#{}: {}'.format(self.unique_id, new_position))
            self.model.grid.move_agent(self, new_position)

    def _filter_nonvisible_neighbors(self, neighbors):
        def is_visible(neighbor, walls):
            line_cells = get_line(neighbor.pos, self.pos)
            for cell in line_cells:
                if cell in walls:
                    return False

            # import numpy as np
            # length = self.scan_radius * 2 + 1
            # grid = np.full((length, length), '.')
            # for cell in line_cells:
            #     x = self.scan_radius + (cell[0] - self.pos[0])
            #     y = self.scan_radius + (cell[1] - self.pos[1])
            #     grid[x][y] = '*'
            # for wall in walls:
            #     x = self.scan_radius + (wall[0] - self.pos[0])
            #     y = self.scan_radius + (wall[1] - self.pos[1])
            #     grid[x][y] = 'W'
            # x = self.scan_radius + (neighbor.pos[0] - self.pos[0])
            # y = self.scan_radius + (neighbor.pos[1] - self.pos[1])
            # grid[x][y] = 'O'
            # grid[self.scan_radius][self.scan_radius] = 'A'
            # for i in range(length):
            #     row = ''
            #     for j in range(length):
            #         row += grid[i][j] + ' '
            #     print(row)
            return True

        # Get the walls and non-walls
        walls = set()
        others = []
        for neighbor in neighbors:
            if type(neighbor) == Wall:
                walls.add(neighbor.pos)
            else:
                others.append(neighbor)

        # If no walls everything is visible
        if len(walls) <= 0:
            return neighbors

        # Proceed to check which neighbors are visible
        visible_neighbors = []
        for neighbor in others:
            visible = is_visible(neighbor, walls)
            if visible:
                visible_neighbors.append(neighbor)

        return visible_neighbors


    def process(self): #default GOAL: find resources and pick
        
        #print('Coopa.pickresource()')
        #resource_before = self._resource_count
        #print('AgentCoopa %s #%s, before resource_count, %i' %(self._current_goal['name'], self.unique_id,self._resource_count))
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=self.scan_radius)
        neighbors = self._filter_nonvisible_neighbors(neighbors)
        for neighbor in neighbors:
            if type(neighbor) is Resource:
                #TODO: abstract out the cooperation and goal awareness
                #self.model.message_dispatcher.broadcast(Message(self, 'resource', self.pos[0], self.pos[1]))
                if self._resource_count < self._capacity:
                    self._resource_count += 1
                    self.model.grid.remove_agent(neighbor)
                #else: #GOAL changed: look for drop point and not resources
                #    self._current_goal = self._goals['find_drop_point']

            elif type(neighbor) is DropPoint:
                #print('-- Drop point found -------------------')
                #self.model.message_dispatcher.broadcast(Message(self, 'drop_point', self.pos[0], self.pos[1]))
                neighbor.add_resources(self._resource_count)
                self._resource_count = 0
                #GOAL changed: look for drop point and not resources
                #self._goals['find_resource']['pos'] = None
                #self._current_goal = self._goals['find_resource']
            
            elif type(neighbor) is RechargePoint:
                if self._battery_power < 120:
                    self._is_recharging = True
                    #self._battery_power = 360
                    #TODO: the agent shall wait for charging, depending on the amount of recharging required
                

        print('AgentCoopa#{}, target:{}, resource_count:{}'.format(self.unique_id,self._target_pos, self._resource_count))

    # def process_(self): #default GOAL: find resources and pick
    #     #print('Coopa.pickresource()')
    #     #resource_before = self._resource_count
    #     print('AgentCoopa %s #%s, before resource_count, %i' %(self._current_goal['name'], self.unique_id,self._resource_count))
    #     cellmates = self.model.grid.get_cell_list_contents([self.pos])
    #     if len(cellmates) > 1:
    #         for other in cellmates:
    #             if type(other) is Resource:
    #                 #TODO: abstract out the cooperation and goal awareness
    #                 self.model.message_dispatcher.broadcast(Message(self, 'resource', self.pos[0], self.pos[1]))
    #                 if self._resource_count < self._capacity:
    #                     self._resource_count += 1
    #                     self.model.grid.remove_agent(other)
    #                 else: #GOAL changed: look for drop point and not resources
    #                     self._current_goal = self._goals['find_drop_point']

    #             elif type(other) is DropPoint:
    #                 print('-- Drop point found -------------------')
    #                 self.model.message_dispatcher.broadcast(Message(self, 'drop_point', self.pos[0], self.pos[1]))
    #                 other.add_resources(self._resource_count)
    #                 self._resource_count = 0
    #                 #GOAL changed: look for drop point and not resources
    #                 self._goals['find_resource']['pos'] = None
    #                 self._current_goal = self._goals['find_resource']

    #     print('AgentCoopa #%s, after resource_count, %i' %(self.unique_id,self._resource_count))

    #     #if self._resource_count > resource_before: #resource found

    
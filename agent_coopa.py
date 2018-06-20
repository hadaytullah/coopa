import random
import pdb
import numpy as np

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


class AgentCoopa(AgentBasic):
    """AgentCoopa cooperates with other agents"""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

        model.message_dispatcher.register(self)

        #self._resource_count = 1 #random.choice([0,5])
        #self._pos_resource = None # potential resource location
        #self._pos_drop_point = None # they shall discover the drop point

        #self._cooperation = {}
        self.name = "AgentCoopa#{:0>3}".format(self.unique_id)
        self._capacity = random.choice([1, 2, 3])
        self._awareness = Awareness(self)

        # Map with different layers
        self._map = {}
        self._impassables = [Wall, DropPoint, RechargePoint, Resource]
        # Create map of the environment for the agent, i.e. the agent knows its environment beforehand
        self._map['impassable'] = search.build_map(model.grid, self._impassables)
        self._map['seen'] = np.full((model.grid.width, model.grid.height), None)
        self._map['seen_time'] = np.zeros((model.grid.width, model.grid.height))

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
        self._target_pos_path = []
         # resource

        # each step will consume units depending on speed, scan radius, etc.
        self._battery_power = 320
        self._max_battery_power = 320
        self._is_recharging = False

        self._speed = 1
        self._scan_radius = 1
        self._grid = model.grid

    def step(self):
        if self._battery_power > 0:
            if self._is_recharging is False:
                self._awareness.step()
                super(AgentCoopa, self).step()
                self.drain_battery()
            else:
                print("{} is recharging.".format(self.name))
                self.recharge_battery()
        else:
            print("{} out of power.".format(self.name))

    def receive(self, message):
        self._awareness.cooperation_awareness(message) #have to improve this, temporary solution
    
    def recharge_battery(self):
        self._battery_power += 10
        if self._battery_power >= self._max_battery_power:
            self._battery_power = self._max_battery_power
            self._is_recharging = False
            self._target_pos = None

    @property
    def target_pos(self):
        return self._target_pos

    @target_pos.setter
    def target_pos(self, position):
        self._target_pos = position
        if self._target_pos is not None:
            # Ensure that all positions are marked as tuples.
            self._target_pos = tuple(self._target_pos)
            self._target_pos_path = search.astar(self._map['impassable'], self.pos, self._target_pos)[1:-1]

    @property
    def capacity(self):
        return self._capacity
    
    @property
    def battery_power(self):
        return self._battery_power

    @property
    def speed(self):
        return self._speed

    @property
    def scan_radius(self):
        return self._scan_radius

    def drain_battery(self):
        """Drain battery based on the current agent configuration (speed, scan radius, etc.).
        """
        scan_drain = (self.scan_radius - 1) ** 1.5  # Magic number
        speed_drain = self._speed  # Currently agents have fixed speed
        self._battery_power -= scan_drain + speed_drain

    def move(self):
        #if self._current_goal is not None and self._current_goal['pos'] is not None:
        if self._target_pos is not None:
            if len(self._target_pos_path) > 0:
                # Consume a movement from the path if it is available
                new_pos = self._target_pos_path[0]
                if self.model.grid.is_cell_empty(new_pos):
                    self.model.grid.move_agent(self, new_pos)
                    self._target_pos_path = self._target_pos_path[1:]
                    print("{}: Moving on path to {}, {} steps left.".format(self.name, new_pos, len(self._target_pos_path)))
            else:
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

    def _filter_nonvisible_objects(self, objects):
        """Filters the objects the agent can't see from the objects list."""
        def add_visible(obj, walls):
            line_cells = get_line(obj.pos, self.pos)
            for cell in line_cells[1:-1]:
                if cell in walls:
                    return False

            # import numpy as np
            # length = self._scan_radius * 2 + 1
            # grid = np.full((length, length), '.')
            # for cell in line_cells:
            #     x = self._scan_radius + (cell[0] - self.pos[0])
            #     y = self._scan_radius + (cell[1] - self.pos[1])
            #     grid[x][y] = '*'
            # x = self._scan_radius + (object.pos[0] - self.pos[0])
            # y = self._scan_radius + (object.pos[1] - self.pos[1])
            # grid[x][y] = 'O'
            # grid[self._scan_radius][self._scan_radius] = 'A'
            # for wall in walls:
            #     x = self._scan_radius + (wall[0] - self.pos[0])
            #     y = self._scan_radius + (wall[1] - self.pos[1])
            #     grid[x][y] = 'W'
            # for i in range(length):
            #     row = ''
            #     for j in range(length):
            #         row += grid[i][j] + ' '
            #     print(row)
            # print()
            return True

        # Get the walls and non-walls
        walls = set()

        for obj in objects:
            if type(obj) == Wall:
                walls.add(obj.pos)

        # If no walls everything is visible
        if len(walls) <= 0:
            return objects

        # Proceed to check which neighbors are visible
        visible_objects = []
        for obj in objects:
            visible = add_visible(obj, walls)
            if visible:
                visible_objects.append(obj)

        return visible_objects

    def _get_neighborhood_objects(self):
        """Gets all the objects in the agent's scan radius, including empty cells."""
        objects = []
        neighborhood = self._grid.iter_neighborhood(self.pos, moore=True, include_center=False,
                                                    radius=self._scan_radius)
        for cell in neighborhood:
            x, y = cell
            if self._grid[x][y] is None:
                objects.append(type('emptyclass', (object,), {'pos': cell})())
            else:
                objects.append(self._grid[x][y])
        return objects

    def process(self): #default GOAL: find resources and pick
        
        #print('Coopa.pickresource()')
        #resource_before = self._resource_count
        #print('AgentCoopa %s #%s, before resource_count, %i' %(self._current_goal['name'], self.unique_id,self._resource_count))
        objects = self._get_neighborhood_objects()
        visible_objects = self._filter_nonvisible_objects(objects)

        # Update map
        for obj in visible_objects:
            x, y = obj.pos
            # Update impassable map
            if type(obj) in self._impassables:
                self._map['impassable'][x][y] = 1
            else:
                self._map['impassable'][x][y] = 0
            # Update map of seen cells
            if type(obj).__name__ is 'emptyclass':
                self._map['seen'][x][y] = None
            else:
                self._map['seen'][x][y] = type(obj)
            # Update the time that cell was seen
            self._map['seen_time'][x][y] = self._awareness._clock

        neighbors = []
        for obj in visible_objects:
            if abs(obj.pos[0] - self.pos[0]) <= 1 and abs(obj.pos[1] - self.pos[1]) <= 1:
                neighbors.append(obj)

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
                

        print(self)

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

    def __repr__(self):
        return "{}(bp:{:.2f}, rc:{}, cp:{}, tp:{}, cg:{})".format(self.name, self.battery_power, self.resource_count,
                                                                  self.pos, self.target_pos, self._awareness._current_goal)

    def __str__(self):
        return self.__repr__()

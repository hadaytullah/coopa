import random
import pdb
import numpy as np
import logging

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
from utils import get_line, create_logger


class AgentCoopa(AgentBasic):
    """AgentCoopa cooperates with other agents"""

    def __init__(self, unique_id, model, log_path=None):
        super().__init__(unique_id, model)

        model.message_dispatcher.register(self)
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

        # Agent next target position (cell) and a possible path to it (if computed).
        self._target_pos = None
        self._target_pos_path = []

        # each step will consume units depending on speed, scan radius, etc.
        self._battery_power = 320
        self._max_battery_power = 320
        self._is_recharging = False

        self._speed = 1
        self._scan_radius = 1
        self._grid = model.grid

        self._logger = create_logger(self.name, log_path=log_path)

        self._direction_matrix =[0,0,0,0,0,0,0,0,0]

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

    def move_old(self):
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

    def move(self):

        # Matrix
        # 0,1,2
        # 3,4,5
        # 6,7,8
        #TODO: have to make DM class 
        # (-1,1), (0,1), (1,1)
        # (-1,0), (0,0), (1,0)
        # (-1,-1), (0,-1), (1,-1)
        self._direction_matrix = np.random.randint(1,100,9)
        highest_score = 0
        highest_index = 0
        for index, score in enumerate(self._direction_matrix):
            if score > highest_score:
                highest_score = score
                highest_index = index
        
        destination_point = [self.pos[0], self.pos[1]]
        print('Highest index, direction is {}'.format(highest_index))
        if highest_index is 0:
            destination_point[0] = self.pos[0] - 1
            destination_point[1] = self.pos[1] + 1
        elif highest_index is 1:
            destination_point[0] = self.pos[0]
            destination_point[1] = self.pos[1] + 1
        elif highest_index is 2:
            destination_point[0] = self.pos[0] + 1
            destination_point[1] = self.pos[1] + 1
        elif highest_index is 3:
            destination_point[0] = self.pos[0] - 1
            destination_point[1] = self.pos[1]
        elif highest_index is 4:
            destination_point[0] = self.pos[0]
            destination_point[1] = self.pos[1]
        elif highest_index is 5:
            destination_point[0] = self.pos[0] + 1
            destination_point[1] = self.pos[1]
        elif highest_index is 6:
            destination_point[0] = self.pos[0] - 1
            destination_point[1] = self.pos[1] - 1
        elif highest_index is 7:
            destination_point[0] = self.pos[0]
            destination_point[1] = self.pos[1] - 1
        elif highest_index is 8:
            destination_point[0] = self.pos[0] + 1
            destination_point[1] = self.pos[1] - 1

        if self.model.grid.is_cell_empty(destination_point) is True and self.model.grid.out_of_bounds(destination_point) is False:
            self.model.grid.move_agent(self, destination_point)
          

        # if self._target_pos is not None:
        #     if len(self._target_pos_path) > 0:
        #         # Consume a movement from the path if it is available
        #         new_pos = self._target_pos_path[0]
        #         if self.model.grid.is_cell_empty(new_pos):
        #             self.model.grid.move_agent(self, new_pos)
        #             self._target_pos_path = self._target_pos_path[1:]
        #             print("{}: Moving on path to {}, {} steps left.".format(self.name, new_pos, len(self._target_pos_path)))
        #     else:
        #         self._move_towards_point(self._target_pos)
        # else:
        #     super(AgentCoopa, self).move()
    def _move_towards_point(self, point):
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
                # Collect resources in the neighborhood
                if self._resource_count < self._capacity:
                    self._resource_count += 1
                    self.model.grid.remove_agent(neighbor)

            elif type(neighbor) is DropPoint:
                # Drop resources to a drop point.
                neighbor.add_resources(self._resource_count)
                self._resource_count = 0
            
            elif type(neighbor) is RechargePoint:
                # Recharge
                if self._battery_power < 120:
                    self._is_recharging = True

        self._log(str(self))

    def _log(self, msg, lvl=logging.DEBUG):
        self._logger.log(lvl, msg, extra={'clock': self.model._clock})

    def __repr__(self):
        return "{}(bp:{:.2f}, rc:{}, cp:{}, tp:{}, cg:{})".format(self.name, self.battery_power, self.resource_count,
                                                                  self.pos, self.target_pos, self._awareness._current_goal)

    def __str__(self):
        return self.__repr__()


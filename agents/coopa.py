import logging
import random

import numpy as np

import search
from metasystem import MetaSystem
from utils import get_line, create_logger
from .basic import BasicAgent
from .recharge_point import RechargePoint
from .trash import Trash
from .trashcan import Trashcan
from .wall import Wall


class CoopaAgent(BasicAgent):
    """AgentCoopa cooperates with other agents."""

    settable_parameters = ['trash_capacity', 'speed', 'scan_radius', 'battery_threshold']

    def __init__(self, unique_id, model, log_path=None):
        super().__init__(unique_id, model, log_path=log_path)

        model.message_dispatcher.register(self)
        self.name = "AgentCoopa#{:0>3}".format(self.unique_id)
        self._trash_capacity = random.choice([1, 2, 3])
        self._meta_system = MetaSystem(self)

        # Map with different layers
        self._map = {}
        self._impassables = [Wall, Trashcan, RechargePoint, Trash]
        # Create map of the environment for the agent, i.e. the agent knows its environment beforehand
        self._map['impassable'] = search.build_map(model.grid, self._impassables)
        self._map['seen'] = np.full((model.grid.width, model.grid.height), None)
        self._map['seen_time'] = np.zeros((model.grid.width, model.grid.height))

        # Agent next target position (cell) and a possible path to it (if computed).
        self._target_pos = None
        self._target_pos_path = []

        # each step will consume units depending on speed, scan radius, etc.
        self._battery_threshold = self._battery.max_charge / 3
        self._is_recharging = False

        self._speed = 1
        self._scan_radius = 1
        self._grid = model.grid

        self._logger = create_logger(self.name, log_path=log_path)

    def step(self):
        if self.battery.charge > 0:
            if self._is_recharging is False:
                self._meta_system.step()
                super(CoopaAgent, self).step()
                self.battery.consume_charge(self.get_configuration())
            else:
                self._log("{} is recharging.".format(self.name), logging.INFO)
                self.recharge_battery()
        else:
            self._log("{} out of power.".format(self.name), logging.INFO)

    def receive(self, message):
        self._meta_system.cooperation_awareness(message) #have to improve this, temporary solution
    
    def recharge_battery(self):
        self.battery.recharge()
        if self.battery.charge == self.battery.max_charge:
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

    def get_configuration(self):
        """Get agent's current internal configuration.
        """
        return {'scan_radius': self.scan_radius,
                'speed': self.speed,
                'trash_capacity': self.trash_capacity,
                'trash_count': self.trash_count,
                'battery_threshold': self.battery_threshold}

    def update_configuration(self, config):
        """Update agent's current internal configuration.
        """
        for key, value in config:
            if key in CoopaAgent.settable_parameters:
                setattr(self, key, value)

    @property
    def trash_capacity(self):
        return self._trash_capacity

    @trash_capacity.setter
    def trash_capacity(self, new_capacity):
        assert not new_capacity < 0
        self._trash_capacity = new_capacity

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, new_speed):
        assert not new_speed < 0
        self._speed = new_speed

    @property
    def scan_radius(self):
        return self._scan_radius

    @scan_radius.setter
    def scan_radius(self, new_radius):
        assert new_radius > 0
        self._scan_radius = new_radius

    @property
    def battery_threshold(self):
        return self._battery_threshold

    @battery_threshold.setter
    def battery_threshold(self, new_threshold):
        assert new_threshold > 0
        self._battery_threshold = new_threshold

    def move(self):
        if self._target_pos is not None:
            if len(self._target_pos_path) > 0:
                # Consume a movement from the path if it is available
                new_pos = self._target_pos_path[0]
                if self.model.grid.is_cell_empty(new_pos):
                    self.model.grid.move_agent(self, new_pos)
                    self._target_pos_path = self._target_pos_path[1:]
                    self._log("{}: Moving on path to {}, {} steps left.".format(self.name, new_pos, len(self._target_pos_path)), logging.DEBUG)
            else:
                self._move_towards_point(self._target_pos)
        else:
            super(CoopaAgent, self).move()

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
        """Gets all the objects in the agent's scan radius, including empty cells.
        """
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

    def update_maps(self, objects):
        """Update agents internal maps with given objects.
        """
        for obj in objects:
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
            self._map['seen_time'][x][y] = self.time

    def filter_neighbors(self, objects):
        """Return only the objects that are currently neighboring the agent.
        """
        neighbors = []
        for obj in objects:
            if abs(obj.pos[0] - self.pos[0]) <= 1 and abs(obj.pos[1] - self.pos[1]) <= 1:
                neighbors.append(obj)
        return neighbors

    def process(self): #default GOAL: find resources and pick
        objects = self._get_neighborhood_objects()
        visible_objects = self._filter_nonvisible_objects(objects)
        neighbors = self.filter_neighbors(visible_objects)
        self.update_maps(visible_objects)

        for neighbor in neighbors:
            if type(neighbor) is Trash:
                # Collect resources in the neighborhood
                if self._trash_count < self._trash_capacity:
                    self._trash_count += 1
                    self.model.grid.remove_agent(neighbor)

            elif type(neighbor) is Trashcan:
                # Drop carried trash to a trashcan.
                neighbor.pick_trash(self._trash_count)
                self._trash_count = 0
            
            elif type(neighbor) is RechargePoint:
                # Recharge
                if self.battery.charge < 120:
                    self._is_recharging = True

        self._log(str(self))

    def __repr__(self):
        return "{}(bp:{:.2f}, tc:{}, cp:{}, tp:{}, cg:{})".format(self.name, self.battery.charge, self.trash_count,
                                                                  self.pos, self.target_pos, self._meta_system._current_goal)

    def __str__(self):
        return self.__repr__()


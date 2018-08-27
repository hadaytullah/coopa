import logging

import numpy as np

import search
from battery import Battery
from explore_potential import ExplorePotentialField
from hot_spot_potential import HotSpotPotentialField
from pf_metasystem import PotentialFieldMetaSystem
from utils import get_line, create_logger
from .basic import BasicAgent
from .recharge_point import RechargePoint
from .trash import Trash
from .trashcan import Trashcan
from .wall import Wall


class PotentialFieldAgent(BasicAgent):
    """Agent which uses potential fields for awarenesses."""

    settable_parameters = ['trash_capacity', 'speed', 'scan_radius', 'battery_threshold']

    def __init__(self, unique_id, model, log_path=None):
        super().__init__(unique_id, model)

        model.message_dispatcher.register(self)
        self.name = "AgentPF#{:0>3}".format(self.unique_id)
        self._logger = create_logger(self.name, log_path=log_path)

        self._meta_system = PotentialFieldMetaSystem(self)

        # Map with different layers
        self._map = {}
        self._impassables = [Wall, Trashcan, RechargePoint, Trash]
        # Initialize the whole environment to be thought to be an empty grid. The belief of the environment state is
        # then updated through observations
        self._map['impassable'] = np.zeros((model.grid.width, model.grid.height))
        self._map['seen'] = np.full((model.grid.width, model.grid.height), None)
        # -1 means not seen at all
        self._map['seen_time'] = np.zeros((model.grid.width, model.grid.height)) - 1

        # Agent next target position (cell) and a possible path to it (if computed).
        self._target_pos = None
        self._target_pos_path = []

        # each step will consume units depending on speed, scan radius, etc.
        self._battery_threshold = self._battery.max_charge / 3
        self._is_recharging = False

        # Known battery recharge and trashcan positions.
        self._recharge_point = self.model.recharge_points[0].pos
        self._map['impassable'][self._recharge_point] = -1
        self._map['seen'][self._recharge_point] = RechargePoint
        self._trashcan = self.model.trashcans[0].pos
        self._map['impassable'][self._trashcan] = -1
        self._map['seen'][self._trashcan] = Trashcan

        # List of current neighboring objects, populated on each step by 'observe' and used by 'process'.
        self._current_neighbors = None

        self._trash_capacity = 3  # Trash carrying capacity
        # self._capacity = random.choice([1, 2, 3])
        self._speed = 1
        self._scan_radius = 1
        self._grid = model.grid

        # Different potential fields which agent uses to move in different situations.
        self._recharge_pf = HotSpotPotentialField(self._grid.width, self._grid.height, [self._recharge_point])
        self._recharge_pf.update(self._map['impassable'])
        self._trashcan_pf = HotSpotPotentialField(self._grid.width, self._grid.height, [self._trashcan])
        self._trashcan_pf.update(self._map['impassable'])
        self._trash_pf = HotSpotPotentialField(self._grid.width, self._grid.height, [])
        self._explore_pf = ExplorePotentialField(self._grid.width, self._grid.height, [])

    def step(self):
        if self.battery.charge > 0:
            if self._is_recharging is False:
                self._meta_system.step()
                super(PotentialFieldAgent, self).step()
                self.battery.consume_charge(self.get_configuration())
            else:
                self._log("Recharging...", logging.INFO)
                self.recharge_battery()
        else:
            self._log("Out of power.", logging.WARNING)

    def receive(self, message):
        self._meta_system.cooperation_awareness(message) #have to improve this, temporary solution
    
    def recharge_battery(self):
        self.battery.recharge()
        if self.battery.charge == self.battery.max_charge:
            self._is_recharging = False
            self._target_pos = None

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
            if key in PotentialFieldAgent.settable_parameters:
                setattr(self, key, value)

    def observe(self):
        objects = self._get_neighborhood_objects()
        visible_objects = self._filter_nonvisible_objects(objects)
        self._current_neighbors = self.filter_neighbors(visible_objects)
        belief_changed = self.update_maps(visible_objects)

        # Update potential fields.
        if belief_changed:
            '''
            self._log("Belief of environment changed: Updating potential fields", logging.INFO)
            self._recharge_pf.update(self._map['impassable'])
            self._drop_pf.update(self._map['impassable'])
            self._trash_pf.update(self._map['impassable'])
            self._explore_pf.update(self._map['impassable'], self.model._clock, self._map['seen_time'])
            '''
        #np.set_printoptions(threshold=np.nan, linewidth=220, precision=0)
        #print(self._map['impassable'])

    def move(self):
        if self.battery.charge <= self._battery_threshold:
            self._recharge_pf.update(self._map['impassable'])
            self._log("Following recharge pf", logging.DEBUG)
            new_pos = self._recharge_pf.follow(self.pos, self._map['impassable'])
        elif self.trash_count == self.trash_capacity:
            self._trashcan_pf.update(self._map['impassable'])
            self._log("Following trashcan pf", logging.DEBUG)
            new_pos = self._trashcan_pf.follow(self.pos, self._map['impassable'])
            #self.follow_pf(self._drop_pf.field)
        elif len(self._trash_pf.hot_spots) > 0:
            self._trash_pf.update(self._map['impassable'])
            self._log("Following trash pf", logging.DEBUG)
            new_pos = self._trash_pf.follow(self.pos, self._map['impassable'])
            #self.follow_pf(self._resource_pf.field)
        else:
            self._explore_pf.update(self._map['impassable'], self.pos, self.time, self._map['seen_time'])
            self._log("Following explore pf", logging.DEBUG)
            new_pos = self._explore_pf.follow(self.pos, self._map['impassable'])
            #self.follow_pf(self._resource_pf.field)

        if new_pos != self.pos:
            self.model.grid.move_agent(self, new_pos)

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
        belief_changed = False
        for obj in objects:
            x, y = obj.pos
            # Update impassable map
            if type(obj) in self._impassables:
                if self._map['impassable'][x][y] == 0:
                    self._map['impassable'][x][y] = -1
                    belief_changed = True
            else:
                if self._map['impassable'][x][y] != 0:
                    self._map['impassable'][x][y] = 0
                    belief_changed = True
            # Update map of seen cells
            if type(obj).__name__ is 'emptyclass':
                self._map['seen'][x][y] = None
            else:
                old = self._map['seen'][x][y]
                self._map['seen'][x][y] = type(obj)
                if isinstance(obj, Trash) and old is None:
                    self._trash_pf.add_hot_spot(obj.pos)
                    belief_changed = True
            # Update the time that cell was seen
            self._map['seen_time'][x][y] = self.time

        self._map['seen_time'][self.pos] = self.time

        return belief_changed

    def filter_neighbors(self, objects):
        """Return only the objects that are currently neighboring the agent.
        """
        neighbors = []
        for obj in objects:
            if abs(obj.pos[0] - self.pos[0]) <= 1 and abs(obj.pos[1] - self.pos[1]) <= 1:
                neighbors.append(obj)
        return neighbors

    def process(self):
        """Process agent's current situation, i.e. its current neighbors.

        Process is executed after moving on each time step.
        """

        # TODO: pick up all trash before processing trash dropping to trashcan.
        for neighbor in self._current_neighbors:
            if isinstance(neighbor, Trash):
                # Collect resources in the neighborhood
                if self._trash_count < self._trash_capacity:
                    nb_pos = neighbor.pos
                    self._trash_count += 1
                    self.model.grid.remove_agent(neighbor)
                    # Free the cell from the internal maps
                    self._map['seen'][nb_pos] = None
                    self._map['impassable'][nb_pos] = 0
                    self._trash_pf.remove_hot_spot(nb_pos)
                    '''
                    self._trash_pf.update(self._map['impassable'])
                    self._recharge_pf.update(self._map['impassable'])
                    self._drop_pf.update(self._map['impassable'])
                    self._explore_pf.update(self._map['impassable'], self.model._clock, self._map['seen_time'])
                    '''

            elif isinstance(neighbor, Trashcan):
                # Drop resources to a drop point.
                neighbor.pick_trash(self._trash_count)
                self._trash_count = 0
            
            elif isinstance(neighbor, RechargePoint):
                # Recharges
                if self.battery.charge < self._battery_threshold:
                    self._is_recharging = True

        self._log(str(self))

    def __repr__(self):
        return "{}(bp:{:.2f}, tc:{}, cp:{})".format(self.name, self.battery.charge, self.trash_count, self.pos)

    def __str__(self):
        return self.__repr__()


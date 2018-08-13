import random
import pdb
import numpy as np
import logging

from agent_basic import AgentBasic
from trash import Trash
from drop_point import DropPoint
from message import Message
from cooperation import Cooperation
from pf_metasystem import PotentialFieldMetaSystem
from knowledge_base import KnowledgeBase
from recharge_point import RechargePoint
from hot_spot_potential import HotSpotPotentialField
from wall import Wall
import search
from utils import get_line, create_logger


class AgentPotentialField(AgentBasic):
    """Agent which uses potential fields for awarenesses."""

    def __init__(self, unique_id, model, log_path=None):
        super().__init__(unique_id, model)

        model.message_dispatcher.register(self)
        self.name = "AgentPF#{:0>3}".format(self.unique_id)
        self._logger = create_logger(self.name, log_path=log_path)

        self._meta_system = PotentialFieldMetaSystem(self)

        # Map with different layers
        self._map = {}
        self._impassables = [Wall, DropPoint, RechargePoint, Trash]
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
        self._battery_power = 320
        self._max_battery_power = 320
        self._battery_threshold = self._max_battery_power / 3 + 20
        self._is_recharging = False

        # Known battery recharge and resource drop points.
        self._recharge_point = self.model.recharge_points[0].pos
        self._map['impassable'][self._recharge_point] = -1
        self._map['seen'][self._recharge_point] = RechargePoint
        self._drop_point = self.model.drop_points[0].pos
        self._map['impassable'][self._drop_point] = -1
        self._map['seen'][self._drop_point] = DropPoint

        # List of current neighboring objects, populated on each step by 'observe' and used by 'process'.
        self._current_neighbors = None

        self._trash_capacity = 1  # Trash carrying capacity
        # self._capacity = random.choice([1, 2, 3])
        self._speed = 1
        self._scan_radius = 1
        self._grid = model.grid

        # Different potential fields which agent uses to move in different situations.
        self._recharge_pf = HotSpotPotentialField(self._grid.width, self._grid.height, [self._recharge_point])
        self._recharge_pf.update(self._map['impassable'])
        self._drop_pf = HotSpotPotentialField(self._grid.width, self._grid.height, [self._drop_point])
        self._drop_pf.update(self._map['impassable'])
        self._trash_pf = HotSpotPotentialField(self._grid.width, self._grid.height, [])

        # main potential field
        self._potential_field = HotSpotPotentialField(self._grid.width, self._grid.height, [])
        
    def step(self):
        if self._battery_power > 0:
            if self._is_recharging is False:
                self._meta_system.step()
                super(AgentPotentialField, self).step()
                self.drain_battery()
            else:
                self._log("Recharging...", logging.INFO)
                self.recharge_battery()
        else:
            self._log("Out of power.", logging.WARNING)

    def receive(self, message):
        self._meta_system.cooperation_awareness(message) #have to improve this, temporary solution
    
    def recharge_battery(self):
        self._battery_power += 10
        if self._battery_power >= self._max_battery_power:
            self._battery_power = self._max_battery_power
            self._is_recharging = False
            self._target_pos = None

    @property
    def trash_capacity(self):
        return self._trash_capacity
    
    @property
    def battery_power(self):
        return self._battery_power

    @property
    def speed(self):
        return self._speed

    @property
    def scan_radius(self):
        return self._scan_radius

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

    def drain_battery(self):
        """Drain battery based on the current agent configuration (speed, scan radius, etc.).
        """
        scan_drain = (self.scan_radius - 1) ** 1.5  # Magic number
        scan_drain = 0
        speed_drain = self._speed  # Currently agents have fixed speed
        self._battery_power -= scan_drain + speed_drain

    def observe(self):
        objects = self._get_neighborhood_objects()
        visible_objects = self._filter_nonvisible_objects(objects)
        self._current_neighbors = self.filter_neighbors(visible_objects)
        belief_changed = self.update_maps(visible_objects)

        # Update potential fields.
        if belief_changed:
            self._log("Belief of environment changed: Updating potential fields", logging.INFO)
            self._recharge_pf.update(self._map['impassable'])
            self._drop_pf.update(self._map['impassable'])
            self._trash_pf.update(self._map['impassable'])
        
        self._update_potential_field()
            
    def _update_potential_field(self):
        self._potential_field.merge(self._recharge_pf.field)
        self._potential_field.merge(self._drop_pf.field)
        self._potential_field.merge(self._trash_pf.field)
            

    def move(self):
#        if self._battery_power <= self._battery_threshold:
#            self._log("Following recharge pf", logging.DEBUG)
#            new_pos = self._recharge_pf.follow(self.pos, self._map['impassable'])
#        elif self.trash_count == self.trash_capacity:
#            self._log("Following drop pf", logging.DEBUG)
#            new_pos = self._drop_pf.follow(self.pos, self._map['impassable'])
#            #self.follow_pf(self._drop_pf.field)
#        else:
#            self._log("Following trash pf", logging.DEBUG)
#            new_pos = self._trash_pf.follow(self.pos, self._map['impassable'])
#            #self.follow_pf(self._resource_pf.field)
        self._log("Following the main pf", logging.DEBUG)
        new_pos = self._potential_field.follow(self.pos, self._map['impassable'])
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
            self._map['seen_time'][x][y] = self._meta_system._clock

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

        # TODO: pick up all trash before processing drop point.
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
                    self._trash_pf.update(self._map['impassable'])
                    self._recharge_pf.update(self._map['impassable'])
                    self._drop_pf.update(self._map['impassable'])

            elif isinstance(neighbor, DropPoint):
                # Drop resources to a drop point.
                neighbor.pick_trash(self._trash_count)
                self._trash_count = 0
            
            elif isinstance(neighbor, RechargePoint):
                # Recharge
                if self._battery_power < 120:
                    self._is_recharging = True

        self._log(str(self))

    def _log(self, msg, lvl=logging.DEBUG):
        self._logger.log(lvl, msg, extra={'clock': self.model._clock})

    def __repr__(self):
        return "{}(bp:{:.2f}, tc:{}, cp:{}, tp:{}, cg:{})".format(self.name, self.battery_power, self.trash_count,
                                                                  self.pos, self.target_pos, self._meta_system._current_goal)

    def __str__(self):
        return self.__repr__()


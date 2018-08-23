import logging
import time

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import SingleGrid
from mesa.time import RandomActivation

import utils
from agents.recharge_point import RechargePoint
from agents.trashcan import Trashcan
from context import Context
from layout import Layout
from message_dispatcher import MessageDispatcher
from reporters import *
from ui_styling import AGENT_TYPES


class CoopaModel(Model):
    """A model with some number of agents."""
    def __init__(self, N, width, height, agent_type, log_path=None):
        self.running = True
        self.num_agents = N
        self.grid = SingleGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)
        self.message_dispatcher = MessageDispatcher()
        self.layout = Layout()
        self._context = Context()
        self.agent_type = AGENT_TYPES[agent_type]
        self.current_id = 0

        self.layout.draw(self.grid)

        # Add drop point(s)
        self.trashcans = [Trashcan(1, self)]
        self.grid.place_agent(self.trashcans[0], (5, 5))

        # Add recharging station(s)
        self.recharge_points = [RechargePoint(1, self)]
        self.grid.place_agent(self.recharge_points[0], (55, 5))

        # Place resources tactically
        self._context.place_few_trash_in_all_rooms(self)

        # the mighty agents arrive
        for i in range(self.num_agents):
            a = self.agent_type(i, self, log_path=log_path)
            self.schedule.add(a)
            self.grid.position_agent(a)

        self.datacollector = DataCollector(
            model_reporters={"Trash collected": compute_dropped_trashes,
                             "Average battery power": compute_average_battery_power,
                             "Max battery power": compute_max_battery_power,
                             "Min battery power": compute_min_battery_power
                             },
            # agent_reporters={"Trash": "trash_count"}
            ) # An agent attribute

        self.name = "CoopaModel"
        self._logger = utils.create_logger(self.name, log_path=log_path)

    @property
    def time(self):
        return self.schedule.time

    def step(self):
        t = time.monotonic()
        self.datacollector.collect(self)
        self.schedule.step()
        self._log("Finished in {:.5f} seconds.".format(time.monotonic() - t), logging.INFO)

    def next_id(self):
        self.current_id += 1
        return self.current_id

    def _log(self, msg, lvl=logging.DEBUG):
        self._logger.log(lvl, msg, extra={'time': self.time})

import logging

from mesa import Model
from resource import Resource
from drop_point import DropPoint
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector
from message_dispatcher import MessageDispatcher
from layout import Layout
from ui_styling import AGENT_TYPES
from recharge_point import RechargePoint
from context import Context
import utils


def compute_gini(model):
    agent_resources = [agent.resource_count for agent in model.schedule.agents]
    x = sorted(agent_resources)
    N = model.num_agents
    if sum(x) > 0:
        B = sum(xi * (N-i) for i, xi in enumerate(x)) / (N*sum(x))
        return 1 + (1/N) - 2*B
    else:
        return 0


def compute_dropped_resources(model):
    drop_point_resources = [dp.resource_count for dp in model.drop_points]
    return sum(drop_point_resources)


def compute_average_battery_power(model):
    bps = [agent.battery_power for agent in model.schedule.agents if hasattr(agent, 'battery_power')]
    return sum(bps) / len(bps)


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
        self._clock = 0

        self.layout.draw(self.grid)

        # Add drop point(s)
        self.drop_points = [DropPoint(1, self)]
        self.grid.place_agent(self.drop_points[0], (5,5))

        # Add recharging station(s)
        self.recharge_points = [RechargePoint(1, self)]
        self.grid.place_agent(self.recharge_points[0], (55,5))

        # Place resources tactically
        self._context.place_few_resource_in_all_rooms(self)

        # the mighty agents arrive
        for i in range(self.num_agents):
            a = self.agent_type(i, self, log_path=log_path)
            self.schedule.add(a)
            self.grid.position_agent(a)

        self.datacollector = DataCollector(
            model_reporters={"Gini": compute_gini,
                             "Drop point resources": compute_dropped_resources,
                             "Average Battery power": compute_average_battery_power},
            agent_reporters={"Resource": "resource_count"})  # An agent attribute

        self.name = "CoopaModel"
        self._logger = utils.create_logger(self.name, log_path=log_path)

    def step(self):
        self._clock += 1
        self.datacollector.collect(self)
        self.schedule.step()
        self._log("Finished.", logging.INFO)

    def _log(self, msg, lvl=logging.DEBUG):
        self._logger.log(lvl, msg, extra={'clock': self._clock})

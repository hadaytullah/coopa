import math
import random
from collections import deque

from agent_basic import AgentBasic
from mesa.time import RandomActivation
from trash import Trash
from drop_point import DropPoint
from message import Message
from cooperation import Cooperation
from knowledge_base import KnowledgeBase
from recharge_point import RechargePoint
from pf_metasystem import PotentialFieldMetaSystem

class PotentialFieldMape:
    """Potential field MAPE, monitor, analyse, plan, execute
    """

    def __init__ (self, agent):
        self._agent = agent
        self._cooperation = {}
        self._knowledge_base = KnowledgeBase()
        self._meta_system = PotentialFieldMetaSystem(self, self._knowledge_base)

    def step (self):
        self._meta_system.step()

        self._analyse()
        self._plan()
        self._execute()

    def _analyse (self):
        pass

    def _plan (self):
        pass

    def _execute (self):
        pass

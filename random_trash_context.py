import random

from agents.trash import Trash
from context import Context


class RandomTrashContext(Context):
    """Context which spawns trash randomly.

    :param float spawn_probability: Probability to spawn new trash on each step
    :param int max_trash_count:
        Maximum number of trashes in the environment. No new trashes are spawned if the maximum count is reached.
    """

    def __init__(self, spawn_probability=0.01, max_trash_count=20):
        self._spawn_probability = spawn_probability
        self._max_trash_count = max_trash_count

    def current_trash_count(self, model):
        return len(model.grid.get_agents(Trash))

    def spawn_trash(self, model):
        if random.random() < self._spawn_probability:
            if self.current_trash_count(model) < self._max_trash_count:
                trash = Trash(model.next_id(), model)
                model.schedule.add(trash)
                model.grid.position_agent(trash)




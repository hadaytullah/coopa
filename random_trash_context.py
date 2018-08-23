import random

from agents.trash import Trash
from context import Context


class RandomTrashContext(Context):
    """Context which spawns trash randomly.

    :param float spawn_probability: Probability to spawn new trash on each step
    :param int max_trash_count:
        Maximum number of trashes in the environment. No new trashes are spawned if the maximum count is reached.
    """

    def __init__(self, model, spawn_probability=0.01, max_trash_count=20):
        self._model = model
        self._spawn_probability = spawn_probability
        self._max_trash_count = max_trash_count

    def trash_count(self):
        count = 0
        for c in self._model.grid:
            if isinstance(c, Trash):
                count += 1
        return count

    def spawn_trash(self):
        if random.random() < self._spawn_probability:
            print("Trash count {}".format(self.trash_count()))
            if self.trash_count() < self._max_trash_count:
                trash = Trash(self._model.next_id(), self._model)
                self._model.schedule.add(trash)
                self._model.grid.position_agent(trash)




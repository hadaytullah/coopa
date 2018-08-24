import random

from mesa.space import SingleGrid

from agents.trash import Trash


class ContextGrid(SingleGrid):
    """Subclass of :class:`mesa.space.SingleGrid` with easy access to all agents of particular agent type and
    some trash placing functionality.
    """

    def __init__(self, width, height, torus):
        super().__init__(width, height, torus)
        self._agent_type_map = {}

    def _place_agent(self, pos, agent):
        super()._place_agent(pos, agent)
        agent_type = type(agent)
        if agent_type not in self._agent_type_map:
            self._agent_type_map[agent_type] = []
        self._agent_type_map[agent_type].append(agent)

    def remove_agent(self, agent):
        super().remove_agent(agent)
        agent_type = type(agent)
        self._agent_type_map[agent_type].remove(agent)

    def get_agents(self, agent_type):
        """Get all agents of the given type.

        :param agent_type: Type of the agent, i.e. Trash, Trashcan, etc..
        """
        return self._agent_type_map[agent_type]

    def place_few_trash_in_all_rooms (self, model):
        trash_positions = (
            (5,10), (10,10), (7,14), # bottom left room
            (40,10), (45,2), (50,14), # bottom right room
            (5,40), (10,45), (7,50), # top left room
            (40,40), (45,45), (50,50) # top right room
        )
        self._place_trashes(trash_positions, model)

    def place_trashes_randomly(self, model, num=20):
        for i in range(num):
            trash = Trash(model.next_id(), model)
            model.schedule.add(trash)
            self.position_agent(trash)

    def _place_trashes(self, trash_positions, model):
        for pos in trash_positions:
            trash = Trash(model.next_id(), model)
            model.schedule.add(trash)
            self.place_agent(trash, pos)


class RandomTrashContextGrid(ContextGrid):
    """Context which spawns trash randomly to free cells in the grid.

    :param float trash_spawn_prob: Probability to spawn a trash in each step
    :param int max_trash_count:
        The maximum number of trashes on a grid. A trash is only spawned if this limit has not been breached.
    """

    def __init__(self, width, height, torus, trash_spawn_prob=0.01, max_trash_count=20):
        super().__init__(width, height, torus)
        self._trash_spawn_prob = trash_spawn_prob
        self._max_trash_count = max_trash_count

    def current_trash_count(self):
        return len(self.get_agents(Trash))

    def spawn_trash(self, model):
        if random.random() < self._trash_spawn_prob:
            if self.current_trash_count() < self._max_trash_count:
                trash = Trash(model.next_id(), model)
                model.schedule.add(trash)
                self.position_agent(trash)

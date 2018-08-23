from mesa import Agent


class Trash(Agent):
    """Objects that agents are picking up.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self._count = 1

    @property
    def count(self):
        """Number of thrash pieces in this pile.
        """
        return self._count

    def add(self, num):
        self._count += num

    def subtract(self, num):
        self._count -= num
        if self._count < 0:
            self._count = 0



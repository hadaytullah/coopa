from agents.trash import Trash


class Context:

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
            model.grid.position_agent(trash)

    def _place_trashes(self, trash_positions, model):
        for pos in trash_positions:
            trash = Trash(model.next_id(), model)
            model.schedule.add(trash)
            model.grid.place_agent(trash, pos)




    


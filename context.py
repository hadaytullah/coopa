from mesa import Agent
from mesa.time import RandomActivation
from resource import Resource
import random

class Context:
    # def __init__(self):
    #     super().__init__(unique_id, model)
    #     self._resource_count = 0

    def place_few_resource_in_all_rooms (self, model):
        resource_positions = (
            (5,10), (10,10), (7,14), # bottom left room
            (40,10), (45,2), (50,14), # bottom right room
            (5,40), (10,45), (7,50), # top left room
            (40,40), (45,45), (50,50) # top right room
        )
        self._place_resources(resource_positions, model)
    

    def place_resources_randomly(self, model):
        for i in range(20):
            resource = Resource(i, model)
            model.schedule.add(resource)
            model.grid.position_agent(resource)

    def _place_resources(self, resource_positions, model):
        resource_id = 0
        for pos in resource_positions:
            resource = Resource(resource_id, model)
            model.schedule.add(resource)
            #model.grid.position_agent(resource)
            model.grid.place_agent(resource, pos)
            resource_id += 1



    


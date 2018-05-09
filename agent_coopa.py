from agent_basic import AgentBasic
from mesa.time import RandomActivation
from resource import Resource
from drop_point import DropPoint
from message import Message
from cooperation import Cooperation
import random
import pdb
# TODO: add cooperation awareness
class AgentCoopa(AgentBasic):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.resource_count = 1 #random.choice([0,5])
        model.message_dispatcher.register(self)
        self.pos_resource = None # potential resource location
        self.pos_drop_point = None # they shall discover the drop point
        self.cooperation = {}
    
    def step(self):
        super(AgentCoopa,self).step()
        #self.move()
        #self.pick_resource()

    def receive(self, message):
        if type(message) is Message:
            print('-- Message Received from Agent# {}'.format(message.sender.unique_id))

            if message.sender.unique_id not in self.cooperation:
                cooperation = Cooperation(message.sender)
                cooperation.set_trust(5) #initial trust, migh be reduced later
                cooperation.add_message(message)
                self.cooperation[message.sender.unique_id] = cooperation
                self.pos_resource = [message.resource_x, message.resource_y]
            elif self.cooperation[message.sender.unique_id].trust > 3: #ignore non trust worthy
                self.pos_resource = [message.resource_x, message.resource_y]



    def move(self):
        if self.pos_resource is None:
            super(AgentCoopa,self).move()
        else:
            if random.randrange(1,100) > 50:
                self._move_towards_point(self.pos_resource)
            else:
                super(AgentCoopa,self).move()

    def _move_towards_point(self, point):
        print('-- destination point {}'.format(point))
        #pdb.set_trace()
        #moore: up,down,left,right and diagonal movements
        #von neumann: up, down, left, right
        # include_center = false, mean do not consider its current location
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)

        # find the step that takes the agent closer to a resource
        # assuming that other resources exisits in proximity of a found resource
        x_distance_shortest = abs(possible_steps[0][0] - point[0])
        y_distance_shortest = abs(possible_steps[0][1] - point[1])
        new_position = possible_steps[0]

        for step in possible_steps:
            x_distance = abs(step[0] - point[0])
            y_distance = abs(step[1] - point[1])
            print('step:{}, x_distance:{} , y_distance:{}'.format(step, x_distance, y_distance))
            if x_distance <= x_distance_shortest and y_distance <= y_distance_shortest:
                new_position = step
                print('new position for agent#{}: {}'.format(self.unique_id, new_position))
                x_distance_shortest = x_distance
                y_distance_shortest = y_distance

        #new_position = random.choice(possible_steps)
        print('new position for agent#{}: {}'.format(self.unique_id, new_position))
        self.model.grid.move_agent(self, new_position)

    def pick_resource(self):
        #print('Coopa.pickresource()')
        resource_before = self.resource_count
        super(AgentCoopa,self).pick_resource()
        if self.resource_count > resource_before: #resource found
            self.model.message_dispatcher.broadcast(Message(self, self.pos[0], self.pos[1]))

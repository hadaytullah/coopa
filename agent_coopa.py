from agent_basic import AgentBasic
from mesa.time import RandomActivation
from resource import Resource
from drop_point import DropPoint
from message import Message
from cooperation import Cooperation
import random
import pdb

class AgentCoopa(AgentBasic):
    """AgentCoopa cooperates with other agents"""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

        model.message_dispatcher.register(self)

        #self._resource_count = 1 #random.choice([0,5])
        self._pos_resource = None # potential resource location
        self._pos_drop_point = None # they shall discover the drop point

        self._cooperation = {}
        self._capacity = random.choice([1,2,3])

        self._goals = {
            'random':{
                'name' : 'random',
                'pos' : None # potential resource location
            },
            'find_resource':{
                'name' : 'find_resource',
                'pos' : None # potential resource location
            },
            'find_drop_point':{
                'name' : 'find_drop_point',
                'pos' : None # potential drop point location

            }
        }
        self._current_goal = self._goals['find_resource']
    
    def step(self):
        super(AgentCoopa,self).step()
        #self.move()
        #self.pick_resource()

    def receive(self, message):
        if type(message) is Message:
            print('-- Message Received from Agent# {}'.format(message.sender.unique_id))

            if message.sender.unique_id not in self._cooperation:
                cooperation = Cooperation(message.sender)
                cooperation.set_trust(5) #initial trust, migh be reduced later
                cooperation.add_message(message)
                self._cooperation[message.sender.unique_id] = cooperation
                self._update_goals(message)
                #self._pos_resource = [message.resource_x, message.resource_y]
                #self._goals['find_resource']['pos'] = [message.resource_x, message.resource_y]
            elif self._cooperation[message.sender.unique_id].trust > 3: #ignore non trust worthy
                #self._pos_resource = [message.resource_x, message.resource_y]
                #self._goals['find_resource']['pos'] = [message.resource_x, message.resource_y]
                self._update_goals(message)

    def _update_goals(self, message):
        if message.position_of is 'resource':
            self._goals['find_resource']['pos'] = [message.x, message.y]
        elif message.position_of is 'drop_point':
            self._goals['find_drop_point']['pos'] = [message.x, message.y]


    def move(self):
        if self._current_goal is not None and self._current_goal['pos'] is not None:
            self._move_towards_point (self._current_goal['pos'])
            if self.pos[0] is self._current_goal['pos'][0] and self.pos[1] is self._current_goal['pos'][1]:
                if self._current_goal['name'] is 'find_resource':
                    self._current_goal['pos'] = None
                    print ('------- pos reset ------')
        else:
            super(AgentCoopa,self).move()



#        if self._current_goal['name'] is 'find_resource' and random.randrange(1,100) < 50:
#                self._move_towards_point (self._current_goal['pos'])
#        elif self._current_goal['name'] is 'find_drop_point' and self._current_goal['pos'] is not None:
#            self._move_towards_point (self._current_goal['pos'])
#        else:
#            super(AgentCoopa,self).move()

    def _move_towards_point(self, point):
        print('-- destination point {}'.format(point))
        #pdb.set_trace()
        #moore: up,down,left,right and diagonal movements
        #von neumann: up, down, left, right
        # include_center = false, mean do not consider its current location
        #possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        possible_steps = []
        for cell in self.model.grid.iter_neighborhood(self.pos, moore=True):
            #print('cell is empty {}'.format(cell))
            if self.model.grid.is_cell_empty(cell):
                print('cell is empty {}'.format(cell))
                possible_steps.append(cell)

        if len(possible_steps) > 0:
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

    def process(self): #default GOAL: find resources and pick
        #print('Coopa.pickresource()')
        #resource_before = self._resource_count
        print('AgentCoopa %s #%s, before resource_count, %i' %(self._current_goal['name'], self.unique_id,self._resource_count))
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=1)
        for neighbor in neighbors:
            if type(neighbor) is Resource:
                #TODO: abstract out the cooperation and goal awareness
                self.model.message_dispatcher.broadcast(Message(self, 'resource', self.pos[0], self.pos[1]))
                if self._resource_count < self._capacity:
                    self._resource_count += 1
                    self.model.grid.remove_agent(neighbor)
                else: #GOAL changed: look for drop point and not resources
                    self._current_goal = self._goals['find_drop_point']

            elif type(neighbor) is DropPoint:
                print('-- Drop point found -------------------')
                self.model.message_dispatcher.broadcast(Message(self, 'drop_point', self.pos[0], self.pos[1]))
                neighbor.add_resources(self._resource_count)
                self._resource_count = 0
                #GOAL changed: look for drop point and not resources
                self._goals['find_resource']['pos'] = None
                self._current_goal = self._goals['find_resource']

        print('AgentCoopa #%s, after resource_count, %i' %(self.unique_id,self._resource_count))

    def process_(self): #default GOAL: find resources and pick
        #print('Coopa.pickresource()')
        #resource_before = self._resource_count
        print('AgentCoopa %s #%s, before resource_count, %i' %(self._current_goal['name'], self.unique_id,self._resource_count))
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) > 1:
            for other in cellmates:
                if type(other) is Resource:
                    #TODO: abstract out the cooperation and goal awareness
                    self.model.message_dispatcher.broadcast(Message(self, 'resource', self.pos[0], self.pos[1]))
                    if self._resource_count < self._capacity:
                        self._resource_count += 1
                        self.model.grid.remove_agent(other)
                    else: #GOAL changed: look for drop point and not resources
                        self._current_goal = self._goals['find_drop_point']

                elif type(other) is DropPoint:
                    print('-- Drop point found -------------------')
                    self.model.message_dispatcher.broadcast(Message(self, 'drop_point', self.pos[0], self.pos[1]))
                    other.add_resources(self._resource_count)
                    self._resource_count = 0
                    #GOAL changed: look for drop point and not resources
                    self._goals['find_resource']['pos'] = None
                    self._current_goal = self._goals['find_resource']

        print('AgentCoopa #%s, after resource_count, %i' %(self.unique_id,self._resource_count))

        #if self._resource_count > resource_before: #resource found


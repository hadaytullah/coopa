
from agent_basic import AgentBasic
from mesa.time import RandomActivation
from resource import Resource
from drop_point import DropPoint
from message import Message
from cooperation import Cooperation
from knowledge_base import KnowledgeBase
from recharge_point import RechargePoint
from collections import deque

import math
import random
import pdb

class Awareness:
    """All awarenesses shall exist here."""

    def __init__(self, agent):
        #super().__init__(unique_id, model)
        self._agent = agent
        self._cooperation = {}
        self._knowledge_base = KnowledgeBase()
        self._current_goal = self._knowledge_base.goals['find_resource']
        self._clock = 0
        
        # time awareness
        self._time_resource_found = self._clock
        self._agent_resource_count_history = self._agent.resource_count
        # queue to maintain last 10 positions
        self._agent_position_history = deque([(0,0)],10) 

        # domain awareness
        self._time_domain_strategy_applied = self._clock
    
    def step(self):
        self._clock += 1

        self._time_awareness_step()
        self._goal_awareness_step() 
        self._cooperation_awareness_step() #self._context_awareness_step()
        self._domain_awareness_step()
        self._resource_awareness_step()
        
    def _resource_awareness_step(self):
        if self._agent.battery_power < 100: #TODO: take care of constants related to the grid size
            #find recharge point
            if len(self._knowledge_base.recharge_point_positions) > 0:
                self._agent.set_target_position(self._knowledge_base.recharge_point_positions[0])
                

    def _time_awareness_step(self):
        #TODO: do it properly. This is a quick solution to facilitate domain awareness
        if self._agent.resource_count > self._agent_resource_count_history:
            # a resource has been found, take a note of it
            self._agent_resource_count_history = self._agent.resource_count
            self._time_resource_found = self._clock
        
        # position history 
        # TODO: move to knowledge base?
        self._agent_position_history.appendleft(self._agent.pos)       

    def _domain_awareness_step(self):
        # domain strategy: typically changing the room or 
        # going far from current location improves the 
        # chances to find interesting things
        # WITH hiatus between applications of the strategy, otherwise, it keeps on chaning the target point
        if self._clock - self._time_resource_found > 100 and self._clock - self._time_domain_strategy_applied > 140: 
            self._time_domain_strategy_applied = self._clock
            print("It has been long time since last resource was discovered.")
            #long time no (resource) see
            #find a point a reasonable distance, probably in next room
            pos_x = int(self._agent.pos[0] - (self._agent.model.grid.width/3))
            pos_y = int(self._agent.pos[1] - (self._agent.model.grid.height/3))
            if pos_x < 0:
                pos_x = int(self._agent.pos[0] + (self._agent.model.grid.width/3))
            if pos_y < 0:
                pos_y = int(self._agent.pos[1] + (self._agent.model.grid.height/3))
            
            point = [pos_x, pos_y]
            if self._agent.model.grid.out_of_bounds(point) is False and self._agent.model.grid.is_cell_empty(point):
                self._agent.set_target_position(point)
                print('1.The new point is {}'.format(point))
            else:
                for i in range(int(self._agent.model.grid.width/3)):
                    right_pos_x = int(pos_x + i)
                    left_pos_x = int(pos_x - i)
                    up_pos_y = int(pos_y + i)
                    down_pos_y = int(pos_y - i)

                    points = [
                        [right_pos_x, pos_y],
                        [left_pos_x, pos_y],
                        [pos_x, up_pos_y],
                        [pos_x, down_pos_y]
                    ]
                    point_found = False
                    for point in points:
                        if self._agent.model.grid.out_of_bounds(point) is False and self._agent.model.grid.is_cell_empty(point):
                            self._agent.set_target_position(point)
                            point_found = True
                            print('2.The new point is {}'.format(point))
                            break
                    
                    if point_found:
                        break
                        
        #domain strategy: typically no resources in corridors

        #domain strategy: 

    def _goal_awareness_step(self):
        print('AgentCoopa %s #%s, before resource_count, %i' %(self._current_goal, self._agent.unique_id,self._agent.resource_count))

        if self._current_goal['name'] is 'find_resource':
            if self._agent.resource_count >= self._agent.capacity:
                self._current_goal = self._knowledge_base.goals[self._knowledge_base.goals[self._current_goal['name']]['next_goal']]

            elif self._agent.target_pos is not None:
                if self._agent.pos[0] is self._agent.target_pos[0] and self._agent.pos[1] is self._agent.target_pos[1]:
                    # the agent has reached the location point it was looking for, so move to the next goal or reset
                    if self._agent.resource_count >= self._agent.capacity:
                        self._current_goal = self._knowledge_base.goals[self._knowledge_base.goals[self._current_goal['name']]['next_goal']]
                    else:
                        #reset, or choose some other point wise, Have to figure out 'Wisely' part :)
                        self._agent.set_target_position(None)
                 #_agent._current_goal['pos'] = None
                 #print ('------- pos reset ------')
            else:
                length_resource_positions = len(self._knowledge_base.resource_positions)
                if length_resource_positions > 0:
                    #pict the last logged position as a target position
                    self._agent.set_target_position(self._knowledge_base.resource_positions[length_resource_positions-1])
    
        elif self._current_goal['name'] is 'find_drop_point':
            neighbors = self._agent.model.grid.get_neighbors(self._agent.pos, moore=True, include_center=False, radius=1)
            drop_point = None
            for neighbor in neighbors:
                if type(neighbor) is DropPoint:
                    drop_point = neighbor
                    break
            if drop_point is not None:#drop point found, move on to the next goal
                self._current_goal = self._knowledge_base.goals[self._knowledge_base.goals[self._current_goal['name']]['next_goal']]
                self._agent.set_target_position (None)
            else: #keep looking, a little help from knowledge base
                length_drop_point_positions = len(self._knowledge_base.drop_point_positions)
                if length_drop_point_positions > 0:
                    #pick the last logged position as a target position
                    self._agent.set_target_position (self._knowledge_base.drop_point_positions[length_drop_point_positions-1])
         
         #elif self._current_goal['name'] is 'find_recharge_point':  
         #    pass
        # print('AgentCoopa #%s, after resource_count, %i' %(self.unique_id,self._resource_count))
        # 
    
    def _cooperation_awareness_step(self):
        neighbors = self._agent.model.grid.get_neighbors(self._agent.pos, moore=True, include_center=False, radius=1)
        for neighbor in neighbors:
            if type(neighbor) is Resource:
                self._agent.model.message_dispatcher.broadcast(Message(self._agent, 'resource', self._agent.pos[0], self._agent.pos[1]))
            elif type(neighbor) is DropPoint:
                self._agent.model.message_dispatcher.broadcast(Message(self._agent, 'drop_point', self._agent.pos[0], self._agent.pos[1]))
            elif type(neighbor) is RechargePoint:
                self._agent.model.message_dispatcher.broadcast(Message(self._agent, 'recharge_point', self._agent.pos[0], self._agent.pos[1]))
            #elif type(neighbor) is RechargePoint: #TODO: make recharge point class
               
    def cooperation_awareness(self, message):
        if type(message) is Message:
            print('-- Message Received from Agent# {}'.format(message.sender.unique_id))
            
            # add a new cooperation
            if message.sender.unique_id not in self._cooperation:
                cooperation = Cooperation(message.sender)
                cooperation.set_trust(5) #initial trust, migh be reduced later
                cooperation.add_message(message)
                self._cooperation[message.sender.unique_id] = cooperation
                #self._update_goals(message)
                #self._pos_resource = [message.resource_x, message.resource_y]
                #self._goals['find_resource']['pos'] = [message.resource_x, message.resource_y]
            
            # collect data from the message, the data will influence other awarenesses
            if self._cooperation[message.sender.unique_id].trust > 3: #ignore non trust worthy
                if message.position_of is 'resource':
                    # we must tag data with agent ids. So we can remove the data of an agent that becomes non-trustworthy. 
                    self._knowledge_base.resource_positions.append([message.x, message.y])
                    #self._goals['find_resource']['pos'] = [message.x, message.y]
                elif message.position_of is 'drop_point':
                    self._knowledge_base.drop_point_positions.append([message.x, message.y])
                    #self._goals['find_drop_point']['pos'] = [message.x, message.y]
                elif message.position_of is 'recharge_point':
                    self._knowledge_base.recharge_point_positions.append([message.x, message.y])

    def _move_zig_zag_strategy(self, point):
        #Move in zig zag fashion, why not :)
        #print('-- destination point {}'.format(point))
        #pdb.set_trace()
        #moore: up,down,left,right and diagonal movements
        #von neumann: up, down, left, right
        # include_center = false, mean do not consider its current location
        #possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        possible_steps = []
        for cell in self._agent.model.grid.iter_neighborhood(self._agent.pos, moore=True):
            #print('cell is empty {}'.format(cell))
            if self._agent.model.grid.is_cell_empty(cell):
                #print('cell is empty {}'.format(cell))
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
                #print('step:{}, x_distance:{} , y_distance:{}'.format(step, x_distance, y_distance))
                if x_distance <= x_distance_shortest and y_distance <= y_distance_shortest:
                    new_position = step
                    #print('new position for agent#{}: {}'.format(self.unique_id, new_position))
                    x_distance_shortest = x_distance
                    y_distance_shortest = y_distance

            #new_position = random.choice(possible_steps)
            #print('new position for agent#{}: {}'.format(self.unique_id, new_position))
            self.model.grid.move_agent(self, new_position)
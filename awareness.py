
from agent_basic import AgentBasic
from mesa.time import RandomActivation
from resource import Resource
from drop_point import DropPoint
from message import Message
from cooperation import Cooperation
from knowledge_base import KnowledgeBase
import random
import pdb

class Awareness:
    """All awareness shall exist here."""

    def __init__(self, agent):
        #super().__init__(unique_id, model)
        self._agent = agent
        self._cooperation = {}
        self._knowledge_base = KnowledgeBase()
        self._current_goal = self._knowledge_base.goals['find_resource']
    
    def step(self):
        self._goal_awareness_step() 
        self._cooperation_awareness_step()
        #self._context_awareness_step()
    
    def _goal_awareness_step(self):
        print('AgentCoopa %s #%s, before resource_count, %i' %(self._current_goal, self._agent.unique_id,self._agent.resource_count))

        if self._current_goal['name'] is 'find_resource':
            if self._agent.resource_count >= self._agent.capacity:
                self._current_goal = self._knowledge_base.goals[self._knowledge_base.goals[self._current_goal['name']]['next_goal']]
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
            else: #keep looking, a little help from knowledge base
                length_drop_point_positions = len(self._knowledge_base.drop_point_positions)
                if length_drop_point_positions > 0:
                    #pick the last logged position as a target position
                    self._agent.set_target_position (self._knowledge_base.drop_point_positions[length_drop_point_positions-1])
            
        # print('AgentCoopa #%s, after resource_count, %i' %(self.unique_id,self._resource_count))
        # if _agent.pos[0] is _agent._current_goal['pos'][0] and _agent.pos[1] is _agent._current_goal['pos'][1]:
        #     if _agent._current_goal['name'] is 'find_resource':
        #         _agent._current_goal['pos'] = None
        #         print ('------- pos reset ------')
    
    def _cooperation_awareness_step(self):
        neighbors = self._agent.model.grid.get_neighbors(self._agent.pos, moore=True, include_center=False, radius=1)
        for neighbor in neighbors:
            if type(neighbor) is Resource:
                self._agent.model.message_dispatcher.broadcast(Message(self._agent, 'resource', self._agent.pos[0], self._agent.pos[1]))
            elif type(neighbor) is DropPoint:
                self._agent.model.message_dispatcher.broadcast(Message(self._agent, 'drop_point', self._agent.pos[0], self._agent.pos[1]))
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
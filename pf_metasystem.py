from collections import deque

from agents.recharge_point import RechargePoint
from agents.trash import Trash
from agents.trashcan import Trashcan
from cooperation import Cooperation
from knowledge_base import KnowledgeBase
from message import Message


class PotentialFieldMetaSystem:
    """Potential field meta-subsystem for the agent. Meta-subsystem contains individual awarenesses and orchestrates
    their interplay.
    """

    def __init__(self, agent):
        self._agent = agent
        self._cooperation = {}
        self._knowledge_base = KnowledgeBase()
        self._current_goal = self._knowledge_base.goals['find_trash']
        self._clock = 0
        
        # time awareness
        self._time_resource_found = self._clock
        self._agent_resource_count_history = self._agent.trash_count
        # queue to maintain last 10 positions
        self._agent_position_history = deque([(0, 0)], 10)

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
                self._agent.target_pos = self._knowledge_base.recharge_point_positions[0]

    def _time_awareness_step(self):
        #TODO: do it properly. This is a quick solution to facilitate domain awareness
        if self._agent.trash_count > self._agent_resource_count_history:
            # a resource has been found, take a note of it
            self._agent_resource_count_history = self._agent.trash_count
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
            print("It has been long time since last trash was discovered.")
            #long time no (resource) see
            #find a point a reasonable distance, probably in next room
            pos_x = int(self._agent.pos[0] - (self._agent.model.grid.width/3))
            pos_y = int(self._agent.pos[1] - (self._agent.model.grid.height/3))
            if pos_x < 0:
                pos_x = int(self._agent.pos[0] + (self._agent.model.grid.width/3))
            if pos_y < 0:
                pos_y = int(self._agent.pos[1] + (self._agent.model.grid.height/3))
            
            point = (pos_x, pos_y)
            if self._agent.model.grid.out_of_bounds(point) is False and self._agent.model.grid.is_cell_empty(point):
                self._agent.target_pos = point
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
                            self._agent.target_pos = point
                            point_found = True
                            print('2.The new point is {}'.format(point))
                            break
                    
                    if point_found:
                        break
                        
        #domain strategy: typically no resources in corridors

        #domain strategy: 

    def _goal_awareness_step(self):
        #print('AgentCoopa %s #%s, before resource_count, %i' %(self._current_goal, self._agent.unique_id,self._agent.resource_count))
       
        #base condition, once reached target, reset position, below goal check could set a target otherwise None
        if self._agent.target_pos is not None:
            if self._agent.pos[0] is self._agent.target_pos[0] and self._agent.pos[1] is self._agent.target_pos[1]:
                self._agent.target_pos = None
        
        if self._current_goal['name'] is 'find_trash':
            if self._agent.trash_count >= self._agent.trash_capacity:
                self._current_goal = self._knowledge_base.goals[self._knowledge_base.goals[self._current_goal['name']]['next_goal']]
            elif len(self._knowledge_base.trash_positions) > 0:
                #pict the last logged position as a target position
                self._agent.target_pos = self._knowledge_base.trash_positions[-1]
    
        elif self._current_goal['name'] is 'find_trashcan':
            neighbors = self._agent.model.grid.get_neighbors(self._agent.pos, moore=True, include_center=False, radius=1)
            trashcan = None
            for neighbor in neighbors:
                if type(neighbor) is Trashcan:
                    trashcan = neighbor
                    break
            if trashcan is not None:#drop point found, move on to the next goal
                self._current_goal = self._knowledge_base.goals[self._knowledge_base.goals[self._current_goal['name']]['next_goal']]
                self._agent.target_pos = None
            elif len(self._knowledge_base.trashcan_positions) > 0:
                #keep looking, a little help from knowledge base
                #pick the last logged position as a target position
                self._agent.target_pos = self._knowledge_base.trashcan_positions[-1]
    
    def _cooperation_awareness_step(self):
        neighbors = self._agent.model.grid.get_neighbors(self._agent.pos, moore=True, include_center=False, radius=1)
        for neighbor in neighbors:
            if type(neighbor) is Trash:
                self._agent.model.message_dispatcher.broadcast(Message(self._agent, 'trash', self._agent.pos[0], self._agent.pos[1]))
            elif type(neighbor) is Trashcan:
                self._agent.model.message_dispatcher.broadcast(Message(self._agent, 'trashcan', self._agent.pos[0], self._agent.pos[1]))
            elif type(neighbor) is RechargePoint:
                self._agent.model.message_dispatcher.broadcast(Message(self._agent, 'recharge_point', self._agent.pos[0], self._agent.pos[1]))
            elif type(neighbor) is RechargePoint:
                # TODO: make recharge point class
                pass
               
    def cooperation_awareness(self, message):
        if type(message) is Message:
            print('-- Message Received from Agent# {}: {}'.format(message.sender.unique_id, message))
            
            # add a new cooperation
            if message.sender.unique_id not in self._cooperation:
                cooperation = Cooperation(message.sender)
                cooperation.set_trust(5) #initial trust, migh be reduced later
                cooperation.add_message(message)
                self._cooperation[message.sender.unique_id] = cooperation
            
            # collect data from the message, the data will influence other awarenesses
            if self._cooperation[message.sender.unique_id].trust > 3: #ignore non trust worthy
                if message.position_of is 'trash':
                    # we must tag data with agent ids. So we can remove the data of an agent that becomes non-trustworthy. 
                    self._knowledge_base.trash_positions.append([message.x, message.y])
                    #self._goals['find_resource']['pos'] = [message.x, message.y]
                elif message.position_of is 'trashcan':
                    self._knowledge_base.trashcan_positions.append([message.x, message.y])
                    #self._goals['find_drop_point']['pos'] = [message.x, message.y]
                elif message.position_of is 'recharge_point':
                    self._knowledge_base.recharge_point_positions.append([message.x, message.y])


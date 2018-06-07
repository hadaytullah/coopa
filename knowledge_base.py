import random
        
class KnowledgeBase:

    def __init__(self):
        self._goals = {
            'random':{
                'name' : 'random',
                #'pos' : None # potential resource location
                'next_goal' : 'find_resource'
            },
            'find_resource':{
                'name' : 'find_resource',
                #'pos' : None, # potential resource location
                'next_goal' : 'find_drop_point'
            },
            # 'pick_resource':{
            #     'name' : 'pick_resource',
            #     'next_goal' : 'find_drop_point'
            # },
            'find_drop_point':{
                'name' : 'find_drop_point',
                #'pos' : None # potential drop point location
                'next_goal' : 'find_resource'
            },
            'find_recharge_point':{
                'name' : 'find_recharge_point',
                'next_goal' : 'recharge'
            },
            'recharge':{
                'name' : 'recharge',
                'next_goal' : 'find_resource'
            }

        }

        self._domain = {
            'location':{
                'room':{
                    'relation' : 'has',
                    'cadinality' : 'one_to_many'
                },
                'drop_point':{
                    'relation' : 'has',
                    'cadinality' : 'one_to_many'
                },
                'recharge_point':{
                    'relation' : 'has',
                    'cadinality' : 'one_to_many'
                },
                'resource':{
                    'relation' : 'has',
                    'cadinality' : 'one_to_many'
                },
                'corridor':{
                    'relation' : 'has',
                    'cadinality' : 'one_to_many'
                }
            },
            'room':{
                'drop_point':{
                    'relation' : 'has',
                    'cadinality' : 'one_to_one'
                },
                'recharge_point':{
                    'relation' : 'has',
                    'cadinality' : 'one_to_one'
                },
                'resource':{
                    'relation' : 'has',
                    'cadinality' : 'one_to_many'
                },
                'corridor':{
                    'relation' : 'link',
                    'cadinality' : 'one_to_many'
                }
            },
            'corridor':{
                'drop_point':{
                    'relation' : 'has',
                    'cadinality' : 'one_to_none'
                },
                'recharge_point':{
                    'relation' : 'has',
                    'cadinality' : 'one_to_none'
                }
            }
        }
        
        self._resource_positions = []

        self._drop_point_positions = []

        self._recharge_point_positions = [(55,5)] #for testing purpose
        
    @property
    def goals(self):
        return self._goals

    @property
    def domain(self):
        return self._domain

    @property
    def resource_positions(self):
        return self._resource_positions

    @property
    def drop_point_positions(self):
        return self._drop_point_positions
    
    @property
    def recharge_point_positions(self):
        return self._recharge_point_positions

        
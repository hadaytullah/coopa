import random
        
class KnowledgeBase:

    def __init__(self):
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
        
    @property
    def goals(self, agent):
        return self._goals

    @property
    def domain(self, agent):
        return self._domain

        
class KnowledgeBase:

    def __init__(self):
        self._goals = {
            'random':{
                'name' : 'random',
                #'pos' : None # potential resource location
                'next_goal' : 'find_trash'
            },
            'find_trash':{
                'name' : 'find_trash',
                #'pos' : None, # potential resource location
                'next_goal' : 'find_trashcan'
            },
            # 'pick_resource':{
            #     'name' : 'pick_resource',
            #     'next_goal' : 'find_drop_point'
            # },
            'find_trashcan':{
                'name' : 'find_trashcan',
                #'pos' : None # potential drop point location
                'next_goal' : 'find_trash'
            },
            'find_recharge_point':{
                'name' : 'find_recharge_point',
                'next_goal' : 'recharge'
            },
            'recharge':{
                'name' : 'recharge',
                'next_goal' : 'find_trash'
            }

        }

        self._domain = {
            'location': {
                'room': {
                    'relation': 'has',
                    'cadinality': 'one_to_many'
                },
                'trashcan': {
                    'relation': 'has',
                    'cadinality': 'one_to_many'
                },
                'recharge_point': {
                    'relation': 'has',
                    'cadinality': 'one_to_many'
                },
                'trash': {
                    'relation': 'has',
                    'cadinality': 'one_to_many'
                },
                'corridor': {
                    'relation': 'has',
                    'cadinality': 'one_to_many'
                }
            },
            'room':{
                'trashcan': {
                    'relation' : 'has',
                    'cadinality' : 'one_to_one'
                },
                'recharge_point':{
                    'relation' : 'has',
                    'cadinality' : 'one_to_one'
                },
                'trash':{
                    'relation' : 'has',
                    'cadinality' : 'one_to_many'
                },
                'corridor':{
                    'relation' : 'link',
                    'cadinality' : 'one_to_many'
                }
            },
            'corridor':{
                'trashcan':{
                    'relation' : 'has',
                    'cadinality' : 'one_to_none'
                },
                'recharge_point':{
                    'relation' : 'has',
                    'cadinality' : 'one_to_none'
                }
            }
        }
        
        self._trash_positions = []

        self._trashcan_positions = [(5, 5)]

        self._recharge_point_positions = [(55, 5)] #for testing purpose
        
    @property
    def goals(self):
        return self._goals

    @property
    def domain(self):
        return self._domain

    @property
    def trash_positions(self):
        return self._trash_positions

    @property
    def trashcan_positions(self):
        return self._trashcan_positions
    
    @property
    def recharge_point_positions(self):
        return self._recharge_point_positions

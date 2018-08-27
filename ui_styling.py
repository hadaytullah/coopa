from agents.basic import BasicAgent
from agents.coopa import CoopaAgent
from agents.potential_field import PotentialFieldAgent
from agents.recharge_point import RechargePoint
from agents.trash import Trash
from agents.trashcan import Trashcan
from agents.wall import Wall

PORTRAYALS = {
    CoopaAgent: {
        "Color": "blue",
        "Layer": 0,
        "r": 0.8
    },
    BasicAgent: {
        "Color": "blue",
        "Layer": 0,
        "r": 0.8
    },
    PotentialFieldAgent: {
        "Color": "purple",
        "Layer": 0,
        "r": 0.8
    },
    Trash: {
        "Color": "red",
        "Layer": 0
    },
    Trashcan: {
        "Color": "green",
        "Layer": 0,
        "r":  0.8
    },
    Wall: {
        "Color": "grey",
        "Layer": 0,
        "w": 1,
        "h": 1,
        "Shape": "rect"
    },
    RechargePoint: {
        "Color": "black",
        "Layer": 0,
        "r":  0.8
    }
}

AGENT_TYPES = {
    'pf': PotentialFieldAgent,
    'coopa': CoopaAgent,
    'basic': BasicAgent
}


def agent_portrayal(agent):
    # portrayal = {"Shape": "circle",
    #             "Filled": "true",
    #             "Layer": 0,
    #             "Color": "red",
    #             "r": 0.5}
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "r": 0.5}

    for key, value in PORTRAYALS[type(agent)].items():
        portrayal[key] = value

    if type(agent) in (CoopaAgent, PotentialFieldAgent):
        if agent.battery.charge == 0:
            portrayal["Color"] = "grey"
            portrayal['r'] = 0.7

    return portrayal

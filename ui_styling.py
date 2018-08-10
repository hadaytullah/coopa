from agent_coopa import AgentCoopa
from agent_basic import AgentBasic
from agent_potential_field import AgentPotentialField
from trash import Trash
from drop_point import DropPoint
from wall import Wall
from recharge_point import RechargePoint


PORTRAYALS = {
    AgentCoopa: {
        "Color": "blue",
        "Layer": 0,
        "r": 0.8
    },
    AgentBasic: {
        "Color": "blue",
        "Layer": 0,
        "r": 0.8
    },
    AgentPotentialField: {
        "Color": "purple",
        "Layer": 0,
        "r": 0.8
    },
    Trash: {
        "Color": "red",
        "Layer": 0
    },
    DropPoint: {
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
    'pf': AgentPotentialField,
    'coopa': AgentCoopa,
    'basic': AgentBasic
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

    if type(agent) in (AgentCoopa, AgentPotentialField):
        if agent.battery_power == 0:
            portrayal["Color"] = "grey"
            portrayal['r'] = 0.7

    return portrayal

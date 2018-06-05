from agent_coopa import AgentCoopa
from agent_basic import AgentBasic
from resource import Resource
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
    Resource: {
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
    'coopa': AgentCoopa,
    'basic': AgentBasic
}

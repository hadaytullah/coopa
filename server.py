# server.py
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from coopa_model import CoopaModel
from agent_coopa import AgentCoopa
from agent_basic import AgentBasic
from resource import Resource
from drop_point import DropPoint
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule

n_slider = UserSettableParameter('slider', "Number of Agents", 3, 2, 200, 1)

def agent_portrayal(agent):
    #portrayal = {"Shape": "circle",
    #             "Filled": "true",
    #             "Layer": 0,
    #             "Color": "red",
    #             "r": 0.5}
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "r": 0.5}

    if type(agent) is AgentCoopa:
        portrayal["Color"] = "red"
        portrayal["Layer"] = 0
        portrayal["r"] = 0.8
    elif type(agent) is Resource:
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 0
    elif type(agent) is DropPoint:
        portrayal["Color"] = "blue"
        portrayal["Layer"] = 0
        portrayal["r"] = 0.8
#    else:
#        portrayal["Color"] = "grey"
#        portrayal["Layer"] = 1
#        portrayal["r"] = 0.2

    return portrayal

grid = CanvasGrid(agent_portrayal, 40, 40, 600, 600)
chart = ChartModule([{"Label": "Gini",
                      "Color": "Black"}],
                    data_collector_name='datacollector')

server = ModularServer(CoopaModel,
                       [grid, chart],
                       "Coopa Model",
                       {"N": n_slider, "width": 40, "height": 40})
#server = ModularServer(CoopaModel,
#                       [grid],
#                       "Coopa Model",
#                       {"N": 100, "width": 10, "height": 10})

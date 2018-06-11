# server.py
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from coopa_model import CoopaModel
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule
from ui_styling import agent_portrayal, PORTRAYALS, AGENT_TYPES

n_slider = UserSettableParameter('slider', "Number of Agents", 3, 2, 200, 1)
agent_type = UserSettableParameter('choice', 'Agent type', value=sorted(AGENT_TYPES.keys())[0],
                                   choices=sorted(AGENT_TYPES.keys()))


grid = CanvasGrid(agent_portrayal, 60, 60, 600, 600)
chart = ChartModule([{"Label": "Gini",
                      "Color": "Black"}],
                    data_collector_name='datacollector')

server = ModularServer(CoopaModel,
                       [grid, chart],
                       "Coopa Model",
                       {"N": n_slider, "width": 60, "height": 60, "agent_type": agent_type})
#server = ModularServer(CoopaModel,
#                       [grid],
#                       "Coopa Model",
#                       {"N": 100, "width": 10, "height": 10})

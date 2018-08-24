# server.py
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule
from mesa.visualization.modules import TextElement


from coopa_model import CoopaModel
from random_trash_model import RandomTrashModel
from TextVisualization import TextModule
from ui_styling import agent_portrayal, AGENT_TYPES

n_slider = UserSettableParameter('slider', "Number of Agents", 1, 1, 200, 1)
# Reverse to sorted keys to get coopa as the default agent as we are currently building it.
agent_type = UserSettableParameter('choice', 'Agent type', value=sorted(AGENT_TYPES.keys(), reverse=True)[0],
                                   choices=sorted(AGENT_TYPES.keys()))


grid = CanvasGrid(agent_portrayal, 60, 60, 600, 600)
chart = ChartModule([{"Label": "Trash collected",
                      "Color": "Black"}],
                    data_collector_name='datacollector')

chart2 = ChartModule([{"Label": "Average battery power",
                      "Color": "Black"},
                      {"Label": "Max battery power",
                      "Color": "Green"},
                      {"Label": "Min battery power",
                      "Color": "Red"},
                      ],
                    data_collector_name='datacollector')

time_text = TextModule('time', 'Time')
trash_collected_text = TextModule('trash_collected', 'Trash collected')

#server = ModularServer(CoopaModel,
#                       [grid, chart, chart2],
#                       "Coopa Model",
#                       {"N": n_slider, "width": 60, "height": 60, "agent_type": agent_type, "log_path": None})

#server = ModularServer(CoopaModel,
#                       [grid],
#                       "Coopa Model",
#                       {"N": n_slider, "width": 60, "height": 60, "agent_type": agent_type, "log_path": None})


server = ModularServer(RandomTrashModel,
                       [grid, time_text, trash_collected_text],
                       "Random Trash Model",
                       {"N": n_slider, "width": 60, "height": 60, "agent_type": agent_type, "log_path": None})


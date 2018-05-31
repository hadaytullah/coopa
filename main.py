from agent_coopa import AgentCoopa
from coopa_model import CoopaModel
import matplotlib.pyplot as plt
import numpy as np
from server import server


def start_visualization_server():
    server.port = 8521 # The default
    server.launch()

def test2():
    print('Running Test2...')
    model = CoopaModel(50, 10, 10)
    for i in range(20):
        model.step()
    
    plot_cells(model)
    plot_wealth(model)


start_visualization_server()
#test2()


#def test1():
#    print('Running Test1...')
#    model = CoopaModel(10)
#
#    all_wealth = []
#
#    for j in range(100):
#        for i in range(10):
#            model.step()
#
#        for agent in model.schedule.agents:
#            all_wealth.append(agent.wealth)
#
#    #agent_wealth = [a.wealth for a in model.schedule.agents]
#
#    plt.hist(all_wealth, bins=range(max(all_wealth)+1))
#    #print('agents wealth:%s' %agent_wealth)
#    plt.show()

#def plot_wealth(model):
#    all_wealth = []
#    for agent in model.schedule.agents:
#            all_wealth.append(agent.wealth)
#
#    #agent_wealth = [a.wealth for a in model.schedule.agents]
#
#    plt.hist(all_wealth, bins=range(max(all_wealth)+1))
#    #print('agents wealth:%s' %agent_wealth)
#    plt.show()
#    plt.savefig('wealth.png')
#
#
#def plot_cells(model):
#    agent_counts = np.zeros((model.grid.width, model.grid.height))
#    for cell in model.grid.coord_iter():
#        cell_content, x, y = cell
#        agent_counts[x][y] = len(cell_content)
#
#    plt.imshow(agent_counts, interpolation='nearest')
#    plt.colorbar()
#    plt.show()
#    plt.savefig('grid.png')
    



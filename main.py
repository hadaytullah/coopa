from agent_coopa import AgentCoopa
from coopa_model import CoopaModel
import matplotlib.pyplot as plt
import numpy as np
from server import server


def start_visualization_server():
    server.port = 8521  # The default
    server.launch()


if __name__ == "__main__":
    start_visualization_server()


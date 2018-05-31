from mesa.visualization.ModularVisualization import ModularServer

from .model import BoidModel
from .SimpleContinuousModule import SimpleCanvas


def boid_draw(agent):
    return {"Shape": "circle", "r": 2, "Filled": "true", "Color": "Red"}


boid_canvas = SimpleCanvas(boid_draw, 500, 500)
model_params = {
    "population": 50,
    "width": 100,
    "height": 100,
    "speed": 1,
    "vision": 10,
    "separation": 5,
    "cohere": 0.5,
    "separate": 4.0,
    "match": 4.0
}

server = ModularServer(BoidModel, [boid_canvas], "Boids", model_params)

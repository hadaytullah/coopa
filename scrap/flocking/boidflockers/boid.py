import numpy as np

from mesa import Agent


class Boid(Agent):
    '''
    A Boid-style flocker agent.

    The agent follows three behaviors to flock:
        - Cohesion: steering towards neighboring agents.
        - Separation: avoiding getting too close to any other agent.
        - Alignment: try to fly in the same direction as the neighbors.

    Boids have a vision that defines the radius in which they look for their
    neighbors to flock with. Their speed (a scalar) and velocity (a vector)
    define their movement. Separation is their desired minimum distance from
    any other Boid.
    '''
    def __init__(self, unique_id, model, pos, speed, velocity, vision, separation,
                 cohere=0.025, separate=0.25, match=0.04, max_force=0.05):
        '''
        Create a new Boid flocker agent.

        Args:
            unique_id: Unique agent identifyer.
            pos: Starting position
            speed: Distance to move per step.
            heading: numpy vector for the Boid's direction of movement.
            vision: Radius to look around for nearby Boids.
            separation: Minimum distance to maintain from other Boids.
            cohere: the relative importance of matching neighbors' positions
            separate: the relative importance of avoiding close neighbors
            match: the relative importance of matching neighbors' headings
            max_force: the maximum steering force for coherence, separation and alignment (match).

        '''
        super().__init__(unique_id, model)
        self.pos = np.array(pos)
        self.new_pos = np.array(self.pos)
        self.speed = speed
        self.velocity = velocity
        self.new_velocity = velocity
        self.vision = vision
        self.separation = separation
        self.cohere_factor = cohere
        self.separate_factor = separate
        self.match_factor = match
        self.max_force = max_force

    def cohere(self, neighbors):
        '''
        Return the vector toward the center of mass of the local neighbors.
        '''
        cohere = np.zeros(2)
        if neighbors:
            for neighbor in neighbors:
                #cohere += neighbor.pos
                cohere += self.model.space.get_heading(self.pos, neighbor.pos)
            cohere /= len(neighbors)
        #cohere = self.model.space.get_heading(self.pos, cohere)
        if np.linalg.norm(cohere) > 0.0:
            cohere /= np.linalg.norm(cohere)
        cohere *= self.max_force
        return cohere

    def separate(self, neighbors):
        '''
        Return a vector away from any neighbors closer than separation dist.
        '''
        me = self.pos
        them = (n.pos for n in neighbors)
        separation_vector = np.zeros(2)
        for other in them:
            if self.model.space.get_distance(me, other) < self.separation:
                separation_vector -= self.model.space.get_heading(me, other)
        if np.linalg.norm(separation_vector) > 0.0:
            separation_vector /= np.linalg.norm(separation_vector)
        separation_vector *= self.max_force
        return separation_vector

    def match_heading(self, neighbors):
        '''
        Return a vector of the neighbors' average heading.
        '''
        match_vector = np.zeros(2)
        if neighbors:
            for neighbor in neighbors:
                match_vector += neighbor.velocity
            match_vector /= len(neighbors)
        if np.linalg.norm(match_vector) > 0.0:
            match_vector /= np.linalg.norm(match_vector)
        match_vector *= self.max_force
        return match_vector

    def step(self):
        '''
        Get the Boid's neighbors, compute the new vector, and move accordingly.
        '''

        neighbors = self.model.space.get_neighbors(self.pos, self.vision, False)
        self.new_velocity = self.velocity +\
            (self.cohere(neighbors) * self.cohere_factor +
             self.separate(neighbors) * self.separate_factor +
             self.match_heading(neighbors) * self.match_factor)
        self.new_velocity /= np.linalg.norm(self.new_velocity)
        self.new_pos = self.pos + self.new_velocity * self.speed

    def advance(self):
        self.velocity = self.new_velocity
        self.model.space.move_agent(self, self.new_pos)

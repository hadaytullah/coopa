"""Breadth-first search.
"""
from collections import deque

import numpy as np

# "Maximum distance" used for f.
MAX_DIST = 100000

# "Maximum" dimensions for the maps, used to derive fast lookups from dictionaries using object hashes.
MAX_DIM = 100000

# Clock wise index differences from a center point, starting from the upper left corner.
clock_wise = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]
clock_wise4 = [(-1, 0), (0, 1), (1, 0), (0, -1)]


class SearchNode:

    def __init__(self, pos, prev, f=MAX_DIST):
        self.x = pos[0]
        self.y = pos[1]
        self.pos = tuple(pos)
        self.prev = prev
        self.f = f

    def __eq__(self, other):
        if self.pos == other.pos:
            return True
        return False

    def __hash__(self):
        return self.x * MAX_DIM + self.y


def get_neighbors(map, pos, moore=True):
    n_deltas = clock_wise if moore else clock_wise4
    neighbors = []
    for delta in n_deltas:
        new_pos = (pos[0] + delta[0], pos[1] + delta[1])
        if 0 <= new_pos[0] < map.shape[0] and 0 <= new_pos[1] < map.shape[1]:
            # Passable cells are marked as zeros
            if map[new_pos] == 0:
                neighbors.append((pos[0] + delta[0], pos[1] + delta[1]))
    # We could probably shuffle the neighbors to get rid of some deterministic behavior.
    return neighbors


def bfs(map, goal, moore=True):
    """Compute the minimum distance to the goal from all cells in a given binary map.
    """
    distances = np.zeros(map.shape)
    distances -= 1
    open = deque([SearchNode(goal, None, f=0)])
    closed = {}

    while len(open) > 0:
        current = open.pop()

        for n_pos in get_neighbors(map, current.pos, moore=moore):
            new_node = SearchNode(n_pos, current, f=current.f + 1)
            if n_pos in closed:
                closed_node = closed[n_pos]
                if new_node.f < closed_node.f:
                    del closed[n_pos]
                    open.appendleft(new_node)
                    distances[new_node.pos] = new_node.f
            else:
                open.appendleft(new_node)

        closed[current.pos] = current
        if distances[current.pos] == -1:
            distances[current.pos] = current.f
        elif distances[current.pos] > current.f:
            distances[current.pos] = current.f

    return distances


if __name__ == "__main__":
    import time
    map = np.zeros((10, 10))
    map[3, 3:9] = 1
    map[1:9, 3] = 1
    map[3:5, 8] = 1
    print(map)
    goal = (9, 9)
    t = time.monotonic()
    map2 = bfs(map, goal, moore=True)
    print(time.monotonic() - t)
    print(map2)

    goal = (9, 0)
    t = time.monotonic()
    map3 = bfs(map, goal, moore=True)
    print(time.monotonic() - t)
    print(map3)
    map4 = np.minimum(map2, map3)
    print(map4)




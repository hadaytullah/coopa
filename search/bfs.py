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


def get_neighbors(map, distances, appended, pos, moore=True):
    n_deltas = clock_wise if moore else clock_wise4
    neighbors = []
    for delta in n_deltas:
        new_pos = (pos[0] + delta[0], pos[1] + delta[1])
        if 0 <= new_pos[0] < map.shape[0] and 0 <= new_pos[1] < map.shape[1] and new_pos not in appended:
            # Passable cells are marked as zeros
            if map[new_pos] == 0:
                neighbors.append(new_pos)
            # Mark impassable cells that are neighbors to passable cells as -1.
            elif map[new_pos] == -1:
                distances[new_pos] = -1
    # We could probably shuffle the neighbors to get rid of some deterministic behavior.
    return neighbors


def bfs(map, goal, moore=True):
    """Compute the minimum distance to the goal from all cells in a given binary map.

    :returns: Distance to every cell from the goal. If cell is next to reachable, but marked as impassable (-1), i.e.
    a wall, the returned distance map shows -1. If the cell is not next to reachable and marked as impassable, the
    returned distance map shows -2.
    """
    # Initialize distances so that all cells are though to be "inside wall", i.e. impassable and not next to any
    # passable cell.
    distances = np.zeros(map.shape) - 2
    open = deque([(goal, 0)])
    appended = set([goal])
    nodes_appended = 1

    while len(open) > 0:
        current = open.pop()

        for n_pos in get_neighbors(map, distances, appended, current[0], moore=moore):
            new_node = (n_pos, current[1] + 1)
            if n_pos not in appended:
                open.appendleft(new_node)
                appended.add(n_pos)
                nodes_appended += 1

        if distances[current[0]] == -2:
            distances[current[0]] = current[1]
        elif distances[current[0]] > current[1]:
            distances[current[0]] = current[1]
    # print(nodes_appended)
    return distances


if __name__ == "__main__":
    import time

    np.set_printoptions(threshold=np.nan, linewidth=200)
    map = np.zeros((10, 10))
    map[3, 3:10] = -1
    map[0:9, 3] = -1
    map[3:5, 8] = -1
    print(map)
    goal = (9, 9)
    t = time.monotonic()
    map2 = bfs(map, goal, moore=True)
    print(time.monotonic() - t)
    #print(map2)

    goal = (9, 0)
    t = time.monotonic()
    map3 = bfs(map, goal, moore=True)
    print(time.monotonic() - t)
    print(map3)
    map4 = np.minimum(map2, map3)
    #print(map4)




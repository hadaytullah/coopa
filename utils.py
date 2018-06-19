import numpy as np

def _line_special_cases(x1, y1, x2, y2, dx, dy):
    # Check zero length
    if (x1, y1) == (x2, y2):
        return [(x1, y1)]

    # Check horizontal
    if y1 == y2:
        direction = int(np.sign(x2 - x1))
        return [(x, y1) for x in range(x1, x2 + direction, direction)]

    # Check vertical
    if x1 == x2:
        direction = int(np.sign(y2 - y1))
        return [(x1, y) for y in range(y1, y2 + direction, direction)]

    # Check diagonal
    if abs(dx) == abs(dy):
        diagonal_points = [(x1 + i * np.sign(dx),
                            y1 + i * np.sign(dy))
                           for i in range(abs(dx) + 1)]
        return diagonal_points

    return None

def get_line(start, end):
    # Setup initial conditions
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1

    # Check special cases
    cells = _line_special_cases(x1, y1, x2, y2, dx, dy)
    if cells is not None:
        return cells

    # Determine how steep the line is
    is_steep = abs(dy) > abs(dx)

    # Rotate line
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # Swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True

    # Recalculate differentials
    dx = x2 - x1
    dy = y2 - y1

    # Setup needed variables for the line algorithm
    # Calculate numerator and denominator to avoid floating point issues
    y_numerator = -2 * dy * (2 * x1 + 1) + 2 * dx * (1 + 2 * y1)
    y_denominator = 4 * dx
    not_done = True
    cells = []
    y_direction = int(np.sign(dy / dx))
    prev_cell = (x1, y1)

    # Calculate the cells in the line
    while not_done:
        cells.append(prev_cell)
        next_y = prev_cell[1]
        if y_direction > 0:
            next_y += 1
        next_x = (y_denominator * next_y - y_numerator) * dx / (y_denominator * dy)
        corner_case = next_x.is_integer()
        next_x = int(np.floor(next_x))
        end_addition = 1
        if corner_case:
            end_addition = 0
        for x in range(prev_cell[0] + 1, next_x + end_addition):
            cells.append((x, prev_cell[1]))
            if x == x2:
                not_done = False
                break
        if y_direction < 0:
            next_y -= 1
        prev_cell = (next_x, next_y)

    # Reverse the list if the coordinates were swapped
    if swapped:
        cells.reverse()
    if is_steep:
        for i in range(len(cells)):
            cells[i] = tuple(reversed(cells[i]))
    return cells


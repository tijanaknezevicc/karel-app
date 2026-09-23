from collections import deque

from karel.robot import Direction, direction_delta


def get_neighbors(world, position):
    x, y, direction = position
    neighbors = []

    # forward
    delta_x, delta_y = direction_delta(direction)
    new_x, new_y = x + delta_x, y + delta_y
    if not world.is_blocked(x, y, new_x, new_y):
        neighbors.append((new_x, new_y, direction))

    # left
    left_direction = Direction((direction.value + 3) % 4)
    neighbors.append((x, y, left_direction))

    # right
    right_direction = Direction((direction.value + 1) % 4)
    neighbors.append((x, y, right_direction))

    return neighbors

def is_solvable(world, start, goal_position):
    
    queue = deque([start])
    visited = {start}

    while queue:
        current = queue.popleft()

        current_x, current_y, current_dir = current        
        if (current_x, current_y) == goal_position:
            return True

        for neighbor in get_neighbors(world, current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return False
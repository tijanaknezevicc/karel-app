import random


def _grid_neighbors(x, y, width, height):
    neighbors = []
    if x > 0:
        neighbors.append((x - 1, y))
    if x < width - 1:
        neighbors.append((x + 1, y))
    if y > 0:
        neighbors.append((x, y - 1))
    if y < height - 1:
        neighbors.append((x, y + 1))
    return neighbors

def generate_perfect_maze(world):
    # adding all walls
    for i in range(world.width):
        for j in range(world.height):
            if i < world.width - 1:
                world.add_wall(i, j, i + 1, j) # right field
            if j < world.height - 1:
                world.add_wall(i, j, i, j + 1) # upper field

    start = random.randint(0, world.width - 1), random.randint(0, world.height - 1)
    visited = {start}
    stack = [start]

    while stack:
        current = stack[-1]
        x, y = current

        # find unvisited neighbors
        neighbors = []
        for nx, ny in _grid_neighbors(x, y, world.width, world.height):
            if (nx, ny) not in visited:
                neighbors.append((nx, ny))

        if neighbors:
            next_field = random.choice(neighbors)
            nx, ny = next_field

            world.remove_wall(x, y, nx, ny) # remove wall between current and random neighbor

            visited.add(next_field)
            stack.append(next_field)
        else:
            stack.pop()
import random

from karel.robot import Direction, direction_delta
from karel.world import World


def _add_all_walls(world):
    for i in range(world.width):
        for j in range(world.height):
            if i < world.width - 1:
                world.add_wall(i, j, i + 1, j)  # right square
            if j < world.height - 1:
                world.add_wall(i, j, i, j + 1)  # upper square

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
    _add_all_walls(world)

    start = random.randint(0, world.width - 1), random.randint(0, world.height - 1)
    visited = {start}
    stack = [start]
    edges = []

    while stack:
        current = stack[-1]
        x, y = current

        # find unvisited neighbors
        neighbors = []
        for nx, ny in _grid_neighbors(x, y, world.width, world.height):
            if (nx, ny) not in visited:
                neighbors.append((nx, ny))

        if neighbors:
            next_square = random.choice(neighbors)
            nx, ny = next_square

            edges.append(((x, y), (nx, ny)))
            world.remove_wall(x, y, nx, ny) # remove wall between current and random neighbor

            visited.add(next_square)
            stack.append(next_square)
        else:
            stack.pop()
    return edges

def generate_branching_corridor_structure(orientation, length, branch_probability, main_line_index=None):
    if main_line_index is None:
        main_line_index = random.choice([0, 1])
    branch_index = 1 - main_line_index

    if orientation == "horizontal":
        world = World(width=length, height=2)
        main_line = [(x, main_line_index) for x in range(length)]
    else:
        world = World(width=2, height=length)
        main_line = [(main_line_index, y) for y in range(length)]

    _add_all_walls(world)
    for i in range(len(main_line) - 1):
        world.remove_wall(*main_line[i], *main_line[i + 1])

    branch_positions = []
    for field_index in range(1, len(main_line) - 1):
        if random.random() >= branch_probability:
            continue
        main_pos = main_line[field_index]
        branch_pos = (main_pos[0], branch_index) if orientation == "horizontal" else (branch_index, main_pos[1])
        world.remove_wall(*main_pos, *branch_pos)
        branch_positions.append(branch_pos)

    if not branch_positions:
        field_index = random.randint(1, len(main_line) - 2)
        main_pos = main_line[field_index]
        branch_pos = (main_pos[0], branch_index) if orientation == "horizontal" else (branch_index, main_pos[1])
        world.remove_wall(*main_pos, *branch_pos)
        branch_positions.append(branch_pos)

    return world, main_line, branch_positions

def _build_corridor_from_directions(directions, side_length):
    path = [(0, 0)]
    for direction in directions:
        dx, dy = direction_delta(direction)
        for _ in range(side_length):
            last = path[-1]
            path.append((last[0] + dx, last[1] + dy))

    xs = [p[0] for p in path]
    ys = [p[1] for p in path]
    min_x, min_y = min(xs), min(ys)
    path = [(x - min_x, y - min_y) for x, y in path]
    width = max(xs) - min_x + 1
    height = max(ys) - min_y + 1

    world = World(width=width, height=height)
    _add_all_walls(world)
    for k in range(len(path) - 1):
        world.remove_wall(*path[k], *path[k + 1])

    return world, path

def generate_polyline_corridor_structure(num_segments, side_length, initial_direction=None, turn=None):
    if num_segments not in (2, 3, 4):
        raise ValueError("num_segments must be 2, 3 or 4")

    if initial_direction is None:
        initial_direction = random.choice(list(Direction))
    if turn is None:
        turn = random.choice(["left", "right"])

    if turn == "left":
        turn_func = lambda d: Direction((d.value + 3) % 4)
    else:
        turn_func = lambda d: Direction((d.value + 1) % 4)

    directions = [initial_direction]
    for _ in range(num_segments - 1):
        directions.append(turn_func(directions[-1]))

    return _build_corridor_from_directions(directions, side_length)

_DIAGONAL_PAIRS = {
    "NE": (Direction.NORTH, Direction.EAST),
    "NW": (Direction.NORTH, Direction.WEST),
    "SE": (Direction.SOUTH, Direction.EAST),
    "SW": (Direction.SOUTH, Direction.WEST),
}

STAIRCASE_DIAGONALS = list(_DIAGONAL_PAIRS.keys())

def random_staircase_orientation():
    diagonal = random.choice(STAIRCASE_DIAGONALS)
    dir_a, dir_b = _DIAGONAL_PAIRS[diagonal]
    first_direction = random.choice([dir_a, dir_b])
    return diagonal, first_direction

def generate_staircase_corridor_structure(num_segments, side_length, diagonal=None, first_direction=None):
    if diagonal is None:
        diagonal = random.choice(STAIRCASE_DIAGONALS)
    dir_a, dir_b = _DIAGONAL_PAIRS[diagonal]
    if first_direction is None:
        first_direction = random.choice([dir_a, dir_b])
    second_direction = dir_b if first_direction == dir_a else dir_a

    directions = [first_direction if i % 2 == 0 else second_direction for i in range(num_segments)]
    return _build_corridor_from_directions(directions, side_length)
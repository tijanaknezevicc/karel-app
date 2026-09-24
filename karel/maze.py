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

def _build_adjacency(edges):
    adjacency = {}
    for (x, y), (nx, ny) in edges:
        if (x, y) not in adjacency:
            adjacency[(x, y)] = []
        if (nx, ny) not in adjacency:
            adjacency[(nx, ny)] = []
        adjacency[(x, y)].append((nx, ny))
        adjacency[(nx, ny)].append((x, y))
    return adjacency

def _assign_stretched_positions(edges, root, min_segment, max_segment):
    adjacency = _build_adjacency(edges)
    new_positions = {root: (0, 0)}
    visited = {root}
    stack = [root]

    while stack:
        current = stack.pop()
        for neighbor in adjacency[current]:
            if neighbor not in visited:
                direction = (neighbor[0] - current[0], neighbor[1] - current[1])
                length = random.randint(min_segment, max_segment)
                new_positions[neighbor] = (new_positions[current][0] + direction[0] * length,
                                           new_positions[current][1] + direction[1] * length)
                visited.add(neighbor)
                stack.append(neighbor)

    return new_positions

def _shift_to_positive(new_positions):
    xs = [pos[0] for pos in new_positions.values()]
    ys = [pos[1] for pos in new_positions.values()]
    min_x, min_y = min(xs), min(ys)

    shifted = {}
    for cell, (x, y) in new_positions.items():
        shifted[cell] = (x - min_x, y - min_y)

    return shifted, (max(xs) - min_x + 1, max(ys) - min_y + 1)  # (width, height)

def _segment_squares(pos_a, pos_b):
    x1, y1 = pos_a
    x2, y2 = pos_b
    dx = x2 - x1
    dy = y2 - y1
    length = abs(dx) + abs(dy)  # one of dx or dy should be 0 for a straight segment
    step_x = dx // length if dx != 0 else 0
    step_y = dy // length if dy != 0 else 0

    squares = []
    for i in range(length + 1):
        squares.append((x1 + step_x * i, y1 + step_y * i))
    return squares


def generate_stretched_maze(edges, root, min_segment=2, max_segment=4, max_attempts=50):
    for attempt in range(max_attempts):
        new_positions = _assign_stretched_positions(edges, root, min_segment, max_segment)
        shifted, (width, height) = _shift_to_positive(new_positions)

        occupied = set(shifted.values())
        if len(occupied) != len(shifted): # 
            continue
        segments = []
        overlap_found = False

        for (a, b) in edges:
            squares = _segment_squares(shifted[a], shifted[b])
            interior = squares[1:-1]

            for square in interior:
                if square in occupied:
                    overlap_found = True
                    break
                occupied.add(square)
            
            segments.append(squares)

        if overlap_found:
            continue  # try again with a new random assignment of positions

        world = World(width, height)

        _add_all_walls(world)

        for squares in segments:
            for k in range(len(squares) - 1):
                world.remove_wall(*squares[k], *squares[k + 1])

        return world, shifted

    raise RuntimeError("Could not stretch maze without overlaps after multiple attempts.")

def generate_branching_corridor_structure(orientation, length, branch_probability):
    if orientation == "horizontal":
        world = World(width=length, height=3)
        main_line = [(x, 1) for x in range(length)]
    else:
        world = World(width=3, height=length)
        main_line = [(1, y) for y in range(length)]

    _add_all_walls(world)

    for i in range(len(main_line) - 1):
        world.remove_wall(*main_line[i], *main_line[i + 1])

    branch_positions = []
    for square_index in range(1, len(main_line) - 1):
        if random.random() >= branch_probability:
            continue

        main_pos = main_line[square_index]
        side = random.choice([0, 2])

        if orientation == "horizontal":
            branch_pos = (main_pos[0], side)
        else:
            branch_pos = (side, main_pos[1])

        world.remove_wall(*main_pos, *branch_pos)
        branch_positions.append(branch_pos)

    if not branch_positions: # in case no branches were added, force at least one branch
        square_index = random.randint(1, len(main_line) - 2)
        main_pos = main_line[square_index]
        side = random.choice([0, 2])
        branch_pos = (main_pos[0], side) if orientation == "horizontal" else (side, main_pos[1])
        world.remove_wall(*main_pos, *branch_pos)
        branch_positions.append(branch_pos)

    return world, main_line, branch_positions

def generate_polyline_corridor_structure(num_segments, side_length):
    if num_segments not in (2, 3, 4):
        raise ValueError("num_segments mora biti 2, 3 ili 4.")

    if num_segments == 4:
        initial_direction = Direction.EAST
        turn = "left"
    else:
        initial_direction = random.choice(list(Direction))
        turn = random.choice(["left", "right"])

    if turn == "left":
        turn_func = lambda d: Direction((d.value + 3) % 4)
    else:
        turn_func = lambda d: Direction((d.value + 1) % 4)

    directions = [initial_direction]
    for _ in range(num_segments - 1):
        directions.append(turn_func(directions[-1]))

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
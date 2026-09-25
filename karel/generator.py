import random

from karel.maze import generate_branching_corridor_structure, generate_perfect_maze, generate_polyline_corridor_structure, generate_staircase_corridor_structure
from karel.robot import Direction
from karel.solver import is_solvable
from karel.world import World


def random_square(width, height, exclude=None):
    if exclude is None:
        exclude = []
    while True:
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        if (x, y) not in exclude:
            return x, y

def generate_maze_task(width, height, task_type="pick_up", one_beeper=True): # always one source and one destination
    world = World(width=width, height=height)
    generate_perfect_maze(world)

    start = (0, 0, Direction.EAST)
    goal = random_square(width, height, exclude={(0, 0)})
    initial_beepers = 0
    item_position = None

    if task_type == "pick_up":
        if one_beeper:
            world.add_beeper(*goal)
        else:
            world.add_beeper(*goal, random.randint(1, 10))

    elif task_type == "put_down":
        if one_beeper:
            initial_beepers = 1
        else:
            initial_beepers = random.randint(1, 10)
        world.add_beeper(*goal, -initial_beepers)  # negative beepers to indicate where the robot needs to put them down

    elif task_type == "both":
        item_position = random_square(width, height, exclude={(0, 0), goal})
        if one_beeper:
            beepers_to_add = 1
            world.add_beeper(*item_position)
        else:
            beepers_to_add = random.randint(1, 10)
            world.add_beeper(*item_position, beepers_to_add)
        world.add_beeper(*goal, -beepers_to_add)  # negative beepers to indicate where the robot needs to put them down

    else:
        raise ValueError("Invalid task type. Must be 'pick_up', 'put_down' or 'both'.")

    if is_solvable(world, start, goal):
        return world, start, goal, initial_beepers, item_position
    else:
        raise RuntimeError("Generated maze is unsolvable!")

def generate_multi_item_maze_task(width, height, num_sources=2, num_destinations=2, min_per_destination=1, max_per_destination=5):
    world = World(width=width, height=height)
    generate_perfect_maze(world)

    start = (0, 0, Direction.EAST)
    excluded = [(0, 0)]

    destinations = {}
    for _ in range(num_destinations):
        pos = random_square(width, height, exclude=excluded)
        destinations[pos] = random.randint(min_per_destination, max_per_destination)
        excluded.append(pos)

    total_needed = sum(destinations.values())

    while total_needed < num_sources: # to enusre every source gets at least one beeper to pick up
        pos = random.choice(list(destinations.keys()))
        destinations[pos] += 1
        total_needed += 1

    for pos, count in destinations.items():
        world.add_beeper(*pos, -count)

    source_positions = []
    for _ in range(num_sources):
        pos = random_square(width, height, exclude=excluded)
        source_positions.append(pos)
        excluded.append(pos)

    remaining = total_needed
    source_amounts = {}

    for i, pos in enumerate(source_positions):
        sources_left = num_sources - i

        if sources_left == 1:
            amount = remaining
        else:
            max_for_this = remaining - (sources_left - 1)  # 1 beeper reserved for each remaining source
            amount = random.randint(1, max_for_this)

        source_amounts[pos] = amount
        remaining -= amount
        if amount > 0:
            world.add_beeper(*pos, amount)

    return world, start, source_positions, destinations

def _corridor_position(square, orientation):
    if orientation == "horizontal":
        return (square, 0)
    else:
        return (0, square)
  

def generate_beeper_corridor(min_length=5, max_length=8, spread=True, step=1, one_beeper=True, random_squares=False,
                              orientation=None, with_final_hole=False):

    if spread and with_final_hole:
        raise ValueError("with_final_hole makes sense only when spread is False")

    if orientation is None:
        orientation = random.choice(["horizontal", "vertical"])

    length = random.randint(min_length, max_length)

    if not spread and with_final_hole and length < 3: # beeper and a hole at the end
        raise ValueError("minimum length for with_final_hole is 3")

    if orientation == "horizontal":
        world = World(width=length, height=1)
    else:
        world = World(width=1, height=length)

    beepers_added = 0

    if spread:
        candidate_squares = list(range(1, length, step))  # robot starts on empty square

        for square in candidate_squares:
            is_edge_square = (square == candidate_squares[0] or square == candidate_squares[-1])
            if random_squares and random.random() < 0.4 and not is_edge_square:
                continue

            pos = _corridor_position(square, orientation)
            if one_beeper:
                world.add_beeper(*pos, 1)
                beepers_added += 1
            else:
                beepers_to_add = random.randint(1, 10)
                world.add_beeper(*pos, beepers_to_add)
                beepers_added += beepers_to_add

    else:
        amount = 1 if one_beeper else random.randint(1, 10)
        beeper_square = length - 2 if with_final_hole else length - 1
        pos = _corridor_position(beeper_square, orientation)
        world.add_beeper(*pos, amount)
        beepers_added = amount

        if with_final_hole:
            hole_pos = _corridor_position(length - 1, orientation)
            world.add_beeper(*hole_pos, -amount)

    start = (0, 0, Direction.EAST)
    goal = _corridor_position(length - 1, orientation)

    if is_solvable(world, start, goal):
        return world, start, beepers_added    
    else:
        raise RuntimeError("generated maze is unsolvable!")

def generate_beeper_hole_corridor(min_pairs=2, max_pairs=4, one_beeper=True, orientation=None):
    if orientation is None:
        orientation = random.choice(["horizontal", "vertical"])

    num_pairs = random.randint(min_pairs, max_pairs)
    length = 2 * num_pairs + 1

    world, start, total_beepers = generate_beeper_corridor(
        min_length=length, max_length=length, step=2, spread=True,
        random_squares=False, one_beeper=one_beeper, orientation=orientation,
    )

    beeper_positions = list(world.beepers.keys())  # before holes
    for pos in beeper_positions:
        square = pos[0] if orientation == "horizontal" else pos[1]
        amount = world.beeper_count(*pos)
        hole_pos = _corridor_position(square + 1, orientation)
        world.add_beeper(*hole_pos, -amount)

    return world, start, total_beepers

def generate_branching_corridor(min_length=4, max_length=8, branch_probability=0.3, one_beeper=True, orientation=None, main_line_index=None):
    if orientation is None:
        orientation = random.choice(["horizontal", "vertical"])
    length = random.randint(min_length, max_length)

    world, main_line, branch_positions = generate_branching_corridor_structure(
        orientation, length, branch_probability, main_line_index=main_line_index
    )

    total_beepers = 0
    for pos in branch_positions:
        amount = 1 if one_beeper else random.randint(1, 10)
        world.add_beeper(*pos, amount)
        total_beepers += amount

    start = (*main_line[0], Direction.EAST)
    goal = main_line[-1]

    if is_solvable(world, start, goal):
        return world, start, total_beepers
    else:
        raise RuntimeError("generated maze is unsolvable!")

def _place_corridor_beepers(world, positions, step=1, offset=0, one_beeper=True, random_squares=False):
    candidate_squares = positions[offset::step]
    beepers_added = 0

    for i, pos in enumerate(candidate_squares):
        is_edge_square = (i == 0 or i == len(candidate_squares) - 1)
        if random_squares and random.random() < 0.4 and not is_edge_square:
            continue

        if one_beeper:
            world.add_beeper(*pos, 1)
            beepers_added += 1
        else:
            amount = random.randint(1, 10)
            world.add_beeper(*pos, amount)
            beepers_added += amount

    return beepers_added

def generate_polyline_corridor(min_side=2, max_side=5, num_segments=3, one_beeper=True, initial_direction=None, turn=None, random_squares=False):
    side_length = random.randint(min_side, max_side)
    world, path = generate_polyline_corridor_structure(num_segments, side_length, initial_direction=initial_direction, turn=turn)

    if num_segments == 4:
        candidate_squares = path[1:-1]  # exclude start and end, they are the same square
        goal = None
    else:
        candidate_squares = path[1:]  # exclude start
        goal = path[-1]

    total_beepers = _place_corridor_beepers(world, candidate_squares, step=1, one_beeper=one_beeper, random_squares=random_squares)

    start = (*path[0], Direction.EAST)

    if goal is not None and not is_solvable(world, start, goal):
        raise RuntimeError("generated maze is unsolvable!")

    return world, start, total_beepers

def generate_staircase_corridor(min_segments=2, max_segments=4, min_side=1, max_side=1, step=None, offset=None,
                                  one_beeper=True, diagonal=None, first_direction=None, random_squares=False):
    num_segments = random.randint(min_segments, max_segments)
    side_length = random.randint(min_side, max_side)

    world, path = generate_staircase_corridor_structure(
        num_segments, side_length,
        diagonal=diagonal, first_direction=first_direction
    )
    candidate_squares = path[1:]

    if step is None:
        step = side_length
    if offset is None:
        offset = side_length - 1

    total_beepers = _place_corridor_beepers(
        world, candidate_squares, step=step, offset=offset,
        one_beeper=one_beeper, random_squares=random_squares
    )
    
    start = (*path[0], Direction.EAST)
    goal = path[-1]

    if is_solvable(world, start, goal):
        return world, start, total_beepers
    else:
        raise RuntimeError("generated maze is unsolvable!")
import random

from karel.maze import generate_perfect_maze, generate_stretched_maze
from karel.robot import Direction, Robot
from karel.executor import execute_program, validate_syntax
from karel.exceptions import KarelRuntimeError, InvalidCommandError
from karel.generator import random_square, generate_beeper_corridor, generate_beeper_hole_corridor, generate_branching_corridor, generate_maze_task, generate_multi_item_maze_task, generate_polyline_corridor
from karel.world import World


def _as_maker(task_factory):
    def maker():
        return task_factory
    return maker

def maze_pick_up_task():
    width = random.randint(4, 8)
    height = random.randint(4, 8)
    world, start, goal, initial_beepers, item_position = generate_maze_task(width, height, "pick_up")

    expected_beepers = world.beeper_count(*goal)

    def success(robot, world):
        return robot.get_position() == goal and robot.beeper_count_in_bag() == expected_beepers

    return world, start, initial_beepers, success

def maze_put_down_task():
    width = random.randint(4, 8)
    height = random.randint(4, 8)
    world, start, goal, initial_beepers, item_position = generate_maze_task(width, height, "put_down")

    def success(robot, world):
        return world.beeper_count(*goal) == initial_beepers and robot.beeper_count_in_bag() == 0

    return world, start, initial_beepers, success

def maze_both_task():
    width = random.randint(4, 8)
    height = random.randint(4, 8)
    world, start, goal, initial_beepers, item_position = generate_maze_task(width, height, "both")

    expected_beepers = world.beeper_count(*item_position)

    def success(robot, world):
        picked_up = world.beeper_count(*item_position) == 0
        delivered = world.beeper_count(*goal) == expected_beepers
        return picked_up and delivered

    return world, start, initial_beepers, success

def maze_multi_item_task():
    width = random.randint(5, 8)
    height = random.randint(5, 8)
    world, start, source_positions, destinations = generate_multi_item_maze_task(width, height)

    def success(robot, world):
        sources_empty = all(world.beeper_count(*pos) == 0 for pos in source_positions)
        destinations_filled = all(world.beeper_count(*pos) == 0 for pos in destinations)
        bag_empty = robot.beeper_count_in_bag() == 0
        return sources_empty and destinations_filled and bag_empty

    return world, start, 0, success

def beeper_corridor_task():
    world, start, total = generate_beeper_corridor()

    def success(robot, world):
        return (world.beepers) == 0  # all beepers picked up

    return world, start, 0, success

def beeper_corridor_counting_task():
    world, start, total = generate_beeper_corridor(
        min_length=5, max_length=10, step=1, one_beeper=True, random_squares=False
    )
    def success(robot, world):
        return len(world.beepers) == 0
    return world, start, 0, success

def make_beeper_corridor_conditional_task():
    orientation = random.choice(["horizontal", "vertical"])

    def task_factory():
        world, start, total = generate_beeper_corridor(
            min_length=5, max_length=10, step=1,
            one_beeper=False, random_squares=False,
            orientation=orientation,
        )
        def success(robot, world):
            return len(world.beepers) == 0
        return world, start, 0, success

    return task_factory

def grade(code, level, task_factory, num_variations=5):
    try:
        validate_syntax(code, level)
    except InvalidCommandError:
        return False # invalid syntax

    for _ in range(num_variations):
        world, start, initial_beepers, success_check = task_factory()
        x, y, direction = start

        robot = Robot(x=x, y=y, direction=direction)
        robot.beepers = initial_beepers
        robot.place_in_world(world)

        try:
            execute_program(code, robot, level)
        except KarelRuntimeError:
            return False  # error

        if not success_check(robot, world):
            return False  # no errors, but incorrect result

    return True

def make_classic_maze_task(min_size=4, max_size=6, one_beeper=True):
    width = random.randint(min_size, max_size)
    height = random.randint(min_size, max_size)
    base_world = World(width, height)
    edges = generate_perfect_maze(base_world)
    root = (0, 0)
    original_goal = random_square(width, height, exclude=[root])

    def task_factory():
        stretched_world, shifted = generate_stretched_maze(edges, root=root, min_segment=2, max_segment=4)
        start = (*shifted[root], Direction.EAST)
        goal = shifted[original_goal]

        amount = 1 if one_beeper else random.randint(1, 10)
        stretched_world.add_beeper(*goal, amount)

        def success(robot, world):
            return robot.get_position() == goal and robot.beeper_count_in_bag() == amount

        return stretched_world, start, 0, success

    return task_factory

def make_beeper_corridor_random_squares_task(min_length=6, max_length=12):
    orientation = random.choice(["horizontal", "vertical"])

    def task_factory():
        world, start, total = generate_beeper_corridor(
            min_length=min_length, max_length=max_length, spread=True,
            random_squares=True, one_beeper=False, orientation=orientation,
        )
        def success(robot, world):
            return len(world.beepers) == 0
        return world, start, 0, success

    return task_factory

def make_polyline_task(min_side=2, max_side=5, num_segments=None, random_squares=False):
    if num_segments is None:
        num_segments = random.choice([2, 3])
    initial_direction = random.choice(list(Direction))
    turn = random.choice(["left", "right"])

    def task_factory():
        world, start, total = generate_polyline_corridor(
            min_side=min_side, max_side=max_side, num_segments=num_segments,
            one_beeper=(not random_squares), initial_direction=initial_direction,
            turn=turn, random_squares=random_squares,
        )
        def success(robot, world):
            return len(world.beepers) == 0
        return world, start, 0, success

    return task_factory

def make_branching_corridor_task(min_length=6, max_length=12, branch_probability=0.3):
    orientation = random.choice(["horizontal", "vertical"])

    def task_factory():
        world, start, total = generate_branching_corridor(
            min_length=min_length, max_length=max_length, 
            branch_probability=branch_probability, one_beeper=False, orientation=orientation,
        )
        def success(robot, world):
            return len(world.beepers) == 0
        return world, start, 0, success

    return task_factory

def beeper_corridor_two_square_task():
    world, start, total = generate_beeper_corridor(
        min_length=2, max_length=2, step=1,
        one_beeper=False, random_squares=False,
    )
    def success(robot, world):
        return len(world.beepers) == 0
    return world, start, 0, success

def beeper_corridor_end_task():
    world, start, total = generate_beeper_corridor(
        min_length=5, max_length=10, step=1,
        one_beeper=False, random_squares=False, 
        spread=False, with_final_hole=False
    )
    def success(robot, world):
        return len(world.beepers) == 0
    return world, start, 0, success

def beeper_corridor_end_hole_task():
    world, start, total = generate_beeper_corridor(
        min_length=5, max_length=10, step=1,
        one_beeper=False, random_squares=False, 
        spread=False, with_final_hole=True
    )
    def success(robot, world):
        return len(world.beepers) == 0
    return world, start, 0, success

def beeper_hole_corridor_task():
    world, start, total = generate_beeper_hole_corridor(
        min_pairs=2, max_pairs=5, 
        one_beeper=True, orientation=None
    )
    def success(robot, world):
        return len(world.beepers) == 0
    return world, start, 0, success
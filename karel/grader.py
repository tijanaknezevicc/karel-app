import ast
import random
import copy

from karel.levels import LEVELS
from karel.maze import generate_perfect_maze, random_staircase_orientation
from karel.robot import Direction, Robot
from karel.executor import execute_program, validate_syntax
from karel.exceptions import KarelRuntimeError, InvalidCommandError
from karel.generator import generate_staircase_corridor, random_square, generate_beeper_corridor, generate_beeper_hole_corridor, generate_branching_corridor, generate_maze_task, generate_multi_item_maze_task, generate_polyline_corridor
from karel.world import World


_NODE_TYPE_LABELS = {
    ast.For: "for petlja",
    ast.While: "while petlja",
    ast.If: "if grananje",
}

def grade(code, level, task_factory, num_variations=5):
    try:
        validate_syntax(code, level)
    except InvalidCommandError:
        return False # invalid syntax

    required = LEVELS[level].get("required_node_types", set())
    if required:
        tree = ast.parse(code)
        present_types = {type(node) for node in ast.walk(tree)}
        if not required.issubset(present_types):
            return False

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

def _as_maker(task_factory):
    def maker():
        return task_factory
    return maker

def missing_required_constructs(code, level):
    required = LEVELS[level].get("required_node_types", set())
    if not required:
        return []
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    present_types = {type(node) for node in ast.walk(tree)}
    missing_types = required - present_types
    return [_NODE_TYPE_LABELS.get(t, t.__name__) for t in missing_types]

def maze_pick_up_task():
    width = random.randint(3, 6)
    height = random.randint(3, 6)
    world, start, goal, initial_beepers, item_position = generate_maze_task(width, height, "pick_up")

    expected_beepers = world.beeper_count(*goal)

    def success(robot, world):
        return robot.get_position() == goal and robot.beeper_count_in_bag() == expected_beepers

    success.description = "Pokupi lopticu."
    return world, start, initial_beepers, success

def maze_put_down_task():
    width = random.randint(3, 6)
    height = random.randint(3, 6)
    world, start, goal, initial_beepers, item_position = generate_maze_task(width, height, "put_down")

    def success(robot, world):
        return world.beeper_count(*goal) == 0 and robot.beeper_count_in_bag() == 0

    success.description = "Ostavi lopticu u rupi."
    return world, start, initial_beepers, success

def maze_both_task():
    width = random.randint(3, 6)
    height = random.randint(3, 6)
    world, start, goal, initial_beepers, item_position = generate_maze_task(width, height, "both")

    expected_beepers = world.beeper_count(*item_position)

    def success(robot, world):
        picked_up = world.beeper_count(*item_position) == 0
        delivered = world.beeper_count(*goal) == 0
        return picked_up and delivered

    success.description = "Pokupi lopticu i ostavi je u rupi."
    return world, start, initial_beepers, success

def make_maze_beeper_count_task(min_size=4, max_size=6, task_type="pick_up"):
    width = random.randint(min_size, max_size)
    height = random.randint(min_size, max_size)

    base_world = World(width, height)
    generate_perfect_maze(base_world)
    start = (0, 0, Direction.EAST)
    goal = random_square(width, height, exclude=[(0, 0)])
    item_position = None
    if task_type == "both":
        item_position = random_square(width, height, exclude=[(0, 0), goal])

    def task_factory():
        world = copy.deepcopy(base_world)
        initial_beepers = 0

        if task_type == "pick_up":
            amount = random.randint(1, 10)
            world.add_beeper(*goal, amount)
            def success(robot, world):
                return robot.get_position() == goal and robot.beeper_count_in_bag() == amount
            description = "Pokupi sve loptice.\nObrati pažnju: ne znaš unapred koliko ih ima!"

        elif task_type == "put_down":
            amount = random.randint(1, 10)
            initial_beepers = amount
            world.add_beeper(*goal, -amount)
            def success(robot, world):
                return world.beeper_count(*goal) == 0 and robot.beeper_count_in_bag() == 0
            description = "Ostavi sve loptice u rupu.\nObrati pažnju: ne znaš unapred koliko ih imaš!"

        elif task_type == "both":
            amount = random.randint(1, 10)
            world.add_beeper(*item_position, amount)
            world.add_beeper(*goal, -amount)
            def success(robot, world):
                picked_up = world.beeper_count(*item_position) == 0
                delivered = world.beeper_count(*goal) == 0
                return picked_up and delivered
            description = "Pokupi sve loptice i ostavi ih u rupe.\nObrati pažnju: ne znaš unapred koliko ih ima!"

        else:
            raise ValueError("task_type mora biti 'pick_up', 'put_down' ili 'both'.")

        success.description = description
        return world, start, initial_beepers, success

    return task_factory

def maze_multi_item_task():
    width = random.randint(3, 6)
    height = random.randint(3, 6)
    world, start, source_positions, destinations = generate_multi_item_maze_task(width, height)

    def success(robot, world):
        sources_empty = all(world.beeper_count(*pos) == 0 for pos in source_positions)
        destinations_filled = all(world.beeper_count(*pos) == 0 for pos in destinations)
        bag_empty = robot.beeper_count_in_bag() == 0
        return sources_empty and destinations_filled and bag_empty

    success.description = "Pokupi sve loptice i ostavi ih u rupe."
    return world, start, 0, success

def beeper_corridor_counting_task():
    world, start, total = generate_beeper_corridor(
        min_length=5, max_length=10, step=1, one_beeper=True, random_squares=False
    )
    def success(robot, world):
        return len(world.beepers) == 0
    success.description = "Pokupi sve loptice u hodniku."
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
        success.description = "Pokupi sve loptice.\nObrati pažnju: ne znaš unapred koliko ih ima na svakom polju!"
        return world, start, 0, success

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
        success.description = "Pokupi sve loptice.\nObrati pažnju: ne znaš unapred na kojim poljima se nalaze!"
        return world, start, 0, success

    return task_factory

def make_polyline_task(min_side=2, max_side=5, num_segments=None, random_squares=False):
    if num_segments is None:
        num_segments = random.choice([2, 3])
    initial_direction = random.choice(list(Direction))
    turn = random.choice(["left", "right"])
    one_beeper = random.choice([True, False])

    def task_factory():
        world, start, total = generate_polyline_corridor(
            min_side=min_side, max_side=max_side, num_segments=num_segments,
            one_beeper=one_beeper, initial_direction=initial_direction,
            turn=turn, random_squares=random_squares,
        )
        def success(robot, world):
            return len(world.beepers) == 0
        success.description = "Pokupi sve loptice."
        return world, start, 0, success

    return task_factory

def make_branching_corridor_task(min_length=6, max_length=12, branch_probability=0.3):
    orientation = random.choice(["horizontal", "vertical"])
    main_line_index = random.choice([0, 1])

    def task_factory():
        world, start, total = generate_branching_corridor(
            min_length=min_length, max_length=max_length,
            branch_probability=branch_probability, one_beeper=False,
            orientation=orientation, main_line_index=main_line_index,
        )
        def success(robot, world):
            return len(world.beepers) == 0
        success.description = "Pokupi sve loptice u bočnim prolazima."
        return world, start, 0, success

    return task_factory

def beeper_corridor_two_square_task():
    world, start, total = generate_beeper_corridor(
        min_length=2, max_length=2, step=1,
        one_beeper=False, random_squares=False,
    )
    def success(robot, world):
        return len(world.beepers) == 0
    success.description = "Pokupi lopticu."
    return world, start, 0, success

def beeper_corridor_end_task():
    world, start, total = generate_beeper_corridor(
        min_length=5, max_length=10, step=1,
        one_beeper=False, random_squares=False, 
        spread=False, with_final_hole=False
    )
    def success(robot, world):
        return len(world.beepers) == 0
    success.description = "Pokupi loptice na kraju hodnika."
    return world, start, 0, success

def beeper_corridor_end_hole_task():
    world, start, total = generate_beeper_corridor(
        min_length=5, max_length=10, step=1,
        one_beeper=False, random_squares=False, 
        spread=False, with_final_hole=True
    )
    def success(robot, world):
        return len(world.beepers) == 0
    success.description = "Pokupi loptice i ostavi ih u rupu."
    return world, start, 0, success

def beeper_hole_corridor_task():
    world, start, total = generate_beeper_hole_corridor(
        min_pairs=2, max_pairs=5, 
        one_beeper=True, orientation=None
    )
    def success(robot, world):
        return len(world.beepers) == 0
    success.description = "Pokupi svaku grupu loptica i ostavi je u rupu pored."
    return world, start, 0, success

def make_staircase_task(min_side=1, max_side=1, min_segments=4, max_segments=8, random_squares=False):
    diagonal, first_direction = random_staircase_orientation()
    one_beeper = random.choice([True, False])

    def task_factory():
        world, start, total = generate_staircase_corridor(
            min_side=min_side, max_side=max_side, min_segments=min_segments, max_segments=max_segments,
            one_beeper=one_beeper, diagonal=diagonal, first_direction=first_direction,
            random_squares=random_squares,
        )
        def success(robot, world):
            return len(world.beepers) == 0
        success.description = "Pokupi sve loptice."
        return world, start, 0, success

    return task_factory

def staircase_counting_task():
    world, start, total = generate_staircase_corridor(
        min_segments=2, max_segments=4, min_side=1, max_side=3,
        one_beeper=True, random_squares=False
    )
    def success(robot, world):
        return len(world.beepers) == 0
    success.description = "Pokupi sve loptice."
    return world, start, 0, success
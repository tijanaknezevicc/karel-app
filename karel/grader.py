import random

from karel.robot import Robot
from karel.executor import execute_program, validate_syntax
from karel.exceptions import KarelRuntimeError, InvalidCommandError
from karel.generator import generate_beeper_corridor, generate_maze_task, generate_multi_item_maze_task


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
        return len(world.beepers) == 0  # all beepers picked up

    return world, start, 0, success

def beeper_corridor_counting_task():
    world, start, total = generate_beeper_corridor(
        min_length=5, max_length=10, step=1, one_beeper=True, random_fields=False
    )
    def success(robot, world):
        return len(world.beepers) == 0
    return world, start, 0, success

def make_beeper_corridor_conditional_task():
    orientation = random.choice(["horizontal", "vertical"])

    def task_factory():
        world, start, total = generate_beeper_corridor(
            min_length=5, max_length=10, step=1,
            one_beeper=False, random_fields=False,
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
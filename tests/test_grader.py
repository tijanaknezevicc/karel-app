import pytest

from karel.world import World
from karel.robot import Direction
from karel.grader import grade


def _simple_corridor_task():
    world = World(width=4, height=1)
    start = (0, 0, Direction.EAST)

    def success(robot, world):
        return robot.get_position() == (3, 0)

    return world, start, 0, success


def test_correct_solution_passes():
    code = "napred()\nnapred()\nnapred()"
    assert grade(code, "linijski", _simple_corridor_task) is True


def test_incorrect_solution_fails():
    code = "napred()"  # ne stiže do cilja
    assert grade(code, "linijski", _simple_corridor_task) is False


def test_invalid_syntax_for_level_fails_immediately():
    code = "while moze_napred():\n    napred()"  # while nije dozvoljen na "linijski"
    assert grade(code, "linijski", _simple_corridor_task) is False


def test_runtime_crash_counts_as_failure():
    code = "napred()\nnapred()\nnapred()\nnapred()\nnapred()"  # udara u zid posle cilja
    assert grade(code, "linijski", _simple_corridor_task) is False


def test_general_while_solution_passes_on_varying_lengths():

    import random

    def varying_length_task():
        length = random.randint(3, 8)
        world = World(width=length, height=1)
        start = (0, 0, Direction.EAST)

        def success(robot, world):
            return robot.get_position() == (length - 1, 0)

        return world, start, 0, success

    code = "while moze_napred():\n    napred()"
    assert grade(code, "uslovna_petlja", varying_length_task) is True


def test_hardcoded_solution_fails_on_varying_lengths():
    import random

    def varying_length_task():
        length = random.randint(3, 8)
        world = World(width=length, height=1)
        start = (0, 0, Direction.EAST)

        def success(robot, world):
            return robot.get_position() == (length - 1, 0)

        return world, start, 0, success

    code = "napred()\nnapred()\nnapred()"  # radi samo za duzinu 4
    assert grade(code, "uslovna_petlja", varying_length_task) is False
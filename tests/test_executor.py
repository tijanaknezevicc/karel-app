import pytest

from karel.world import World
from karel.robot import Robot, Direction
from karel.executor import validate_syntax
from karel.executor import execute_program
from karel.exceptions import InvalidCommandError, InfiniteLoopError


def _robot_in_open_world(width=10, height=10, x=0, y=0, direction=Direction.EAST):
    world = World(width=width, height=height)
    robot = Robot(x=x, y=y, direction=direction)
    robot.place_in_world(world)
    return robot


def test_execute_simple_program_moves_robot():
    robot = _robot_in_open_world()
    execute_program("napred()\nnapred()", robot, "linijski")
    assert robot.get_position() == (2, 0)


def test_disallowed_construct_stops_before_any_execution():
    robot = _robot_in_open_world()
    code = "while moze_napred():\n    napred()"
    with pytest.raises(InvalidCommandError):
        execute_program(code, robot, "linijski")
    assert robot.get_position() == (0, 0)  # ništa nije izvršeno


def test_infinite_loop_is_detected():
    robot = _robot_in_open_world(x=5, y=5, direction=Direction.NORTH)
    code = "while moze_napred():\n    levo()"  # robot se samo okreće u krug
    with pytest.raises(InfiniteLoopError):
        execute_program(code, robot, "uslovna_petlja")


def test_camel_case_alias_executes_correctly():
    robot = _robot_in_open_world()
    code = "if mozeNapred():\n    napred()"
    execute_program(code, robot, "grananje")
    assert robot.get_position() == (1, 0)


def test_for_loop_with_range_moves_correct_number_of_times():
    robot = _robot_in_open_world()
    execute_program("for i in range(3):\n    napred()", robot, "brojacka_petlja")
    assert robot.get_position() == (3, 0)


def test_valid_linear_code_passes():
    code = "napred()\nlevo()\nuzmi()"
    validate_syntax(code, "linijski")  # ne sme da baci grešku


def test_for_loop_rejected_at_linear_level():
    code = "for i in range(3):\n    napred()"
    with pytest.raises(InvalidCommandError):
        validate_syntax(code, "linijski")


def test_valid_for_loop_passes_at_counting_level():
    code = "for i in range(3):\n    napred()"
    validate_syntax(code, "brojacka_petlja")


def test_sensor_command_rejected_before_conditional_level():
    code = "moze_napred()"
    with pytest.raises(InvalidCommandError):
        validate_syntax(code, "brojacka_petlja")


def test_valid_while_with_sensor_passes_at_conditional_level():
    code = "while moze_napred():\n    napred()"
    validate_syntax(code, "uslovna_petlja")


def test_if_rejected_before_branching_level():
    code = "if moze_napred():\n    napred()"
    with pytest.raises(InvalidCommandError):
        validate_syntax(code, "uslovna_petlja")


def test_valid_if_passes_at_branching_level():
    code = "if moze_napred():\n    napred()\nelse:\n    levo()"
    validate_syntax(code, "grananje")


def test_assignment_always_rejected():
    code = "x = 5"
    with pytest.raises(InvalidCommandError):
        validate_syntax(code, "napredni")
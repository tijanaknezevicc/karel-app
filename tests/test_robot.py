import pytest

from karel.robot import Robot, Direction
from karel.world import World
from karel.exceptions import WallCollisionError, OutOfBoundsError, NoBeeperError, NoBeepersToPutError

@pytest.fixture
def robot_in_test_world():
    world = World(width=5, height=5, walls={(2, 2)})
    world.add_beeper(0, 0)
    robot = Robot(x=0, y=0, direction=Direction.NORTH)
    robot.place_in_world(world)
    return robot, world

def test_move_forward_updates_position(robot_in_test_world):
    robot, world = robot_in_test_world
    robot.move_forward()
    assert robot.get_position() == (0, 1)

def test_move_forward_into_wall_raises_error(robot_in_test_world):
    robot, world = robot_in_test_world
    robot.x, robot.y = 1, 2
    robot.direction = Direction.EAST
    with pytest.raises(WallCollisionError):
        robot.move_forward()

def test_move_forward_out_of_bounds_raises_error(robot_in_test_world):
    robot, world = robot_in_test_world
    robot.direction = Direction.SOUTH
    with pytest.raises(OutOfBoundsError):
        robot.move_forward()

def test_turn_left_and_turn_right_are_inverse(robot_in_test_world):
    robot, world = robot_in_test_world
    original_direction = robot.get_direction()
    robot.turn_left()
    robot.turn_right()
    assert robot.get_direction() == original_direction

def test_pick_beeper_moves_beeper_to_bag(robot_in_test_world):
    robot, world = robot_in_test_world
    robot.pick_beeper()
    assert robot.beeper_count_in_bag() == 1
    assert world.has_beeper(0, 0) is False

def test_pick_beeper_without_beeper_raises_error(robot_in_test_world):
    robot, world = robot_in_test_world
    robot.x, robot.y = 1, 1
    with pytest.raises(NoBeeperError):
        robot.pick_beeper()

def test_put_beeper_without_beeper_in_bag_raises_error(robot_in_test_world):
    robot, world = robot_in_test_world
    with pytest.raises(NoBeepersToPutError):
        robot.put_beeper()

def test_can_move_forward_reflects_world_state(robot_in_test_world):
    robot, world = robot_in_test_world
    assert robot.can_move_forward() is True  # (0,1) je slobodno

    robot.x, robot.y = 1, 2
    robot.direction = Direction.EAST
    assert robot.can_move_forward() is False  # zid je na (2,2)
import pytest

from karel.world import World
from karel.robot import Direction
from karel.solver import is_solvable


@pytest.fixture
def empty_world():
    return World(width=5, height=5)


def test_solvable_maze_returns_true(empty_world):
    start = (0, 0, Direction.NORTH)
    goal = (2, 2)
    assert is_solvable(empty_world, start, goal) is True


def test_unreachable_goal_returns_false():
    # cilj (2, 2) je opkoljen zidovima sa sve četiri strane
    walls = {(1, 2), (3, 2), (2, 1), (2, 3)}
    world = World(width=5, height=5, walls=walls)

    start = (0, 0, Direction.NORTH)
    goal = (2, 2)
    assert is_solvable(world, start, goal) is False


def test_goal_equals_start_returns_true_immediately(empty_world):
    start = (1, 1, Direction.SOUTH)
    goal = (1, 1)
    assert is_solvable(empty_world, start, goal) is True
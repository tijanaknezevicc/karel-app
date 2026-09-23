import pytest

from karel.world import World
from karel.robot import Direction
from karel.maze import generate_perfect_maze
from karel.solver import is_solvable


def test_maze_is_fully_connected():
    width, height = 4, 4
    world = World(width=width, height=height)
    generate_perfect_maze(world)

    for x in range(width):
        for y in range(height):
            start = (0, 0, Direction.NORTH)
            goal = (x, y)
            assert is_solvable(world, start, goal) is True


def test_maze_has_spanning_tree_wall_count():
    width, height = 5, 5
    world = World(width=width, height=height)

    total_possible_walls = 0
    for i in range(width):
        for j in range(height):
            if i < width - 1:
                total_possible_walls += 1
            if j < height - 1:
                total_possible_walls += 1

    generate_perfect_maze(world)

    removed_walls = total_possible_walls - len(world.walls)
    assert removed_walls == width * height - 1
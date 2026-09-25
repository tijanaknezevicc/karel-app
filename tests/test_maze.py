import pytest

from karel.world import World
from karel.robot import Direction
from karel.maze import generate_perfect_maze, generate_branching_corridor_structure, generate_polyline_corridor_structure
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


def test_branching_structure_main_line_is_fully_connected():
    world, main_line, branch_positions = generate_branching_corridor_structure(
        orientation="horizontal", length=8, branch_probability=0.3
    )
    start = (*main_line[0], Direction.NORTH)
    for pos in main_line:
        assert is_solvable(world, start, pos) is True


def test_branching_structure_branches_are_reachable():
    world, main_line, branch_positions = generate_branching_corridor_structure(
        orientation="horizontal", length=8, branch_probability=1.0
    )
    start = (*main_line[0], Direction.NORTH)
    for pos in branch_positions:
        assert is_solvable(world, start, pos) is True


def test_polyline_structure_l_shape_has_correct_cell_count():
    world, path = generate_polyline_corridor_structure(num_segments=2, side_length=4)
    assert len(path) == 2 * 4 + 1


def test_polyline_structure_square_closes_and_has_correct_cell_count():
    world, path = generate_polyline_corridor_structure(num_segments=4, side_length=3)
    assert len(path) == 4 * 3 + 1
    assert path[0] == path[-1]
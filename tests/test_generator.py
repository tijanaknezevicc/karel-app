import pytest

from karel.robot import Direction
from karel.generator import generate_beeper_corridor
from karel.generator import generate_maze_task


def test_pick_up_places_beeper_on_goal():
    for _ in range(20):
        world, start, goal, initial_beepers, item_position = generate_maze_task(
            width=5, height=5, task_type="pick_up"
        )
        assert world.beeper_count(*goal) == 1
        assert initial_beepers == 0
        assert item_position is None


def test_pick_up_with_random_beeper_count():
    world, start, goal, initial_beepers, item_position = generate_maze_task(
        width=5, height=5, task_type="pick_up", one_beeper=False
    )
    assert 1 <= world.beeper_count(*goal) <= 30


def test_put_down_gives_robot_initial_beeper():
    world, start, goal, initial_beepers, item_position = generate_maze_task(
        width=5, height=5, task_type="put_down"
    )
    assert initial_beepers == 1
    assert world.beepers == {}  # svet počinje potpuno bez loptica


def test_both_places_item_away_from_start_and_goal():
    for _ in range(20):
        world, start, goal, initial_beepers, item_position = generate_maze_task(
            width=5, height=5, task_type="both"
        )
        assert item_position not in ((0, 0), goal)
        assert world.beeper_count(*item_position) == 1
        assert initial_beepers == 0


def test_goal_is_never_start_position():
    for _ in range(30):
        world, start, goal, initial_beepers, item_position = generate_maze_task(
            width=4, height=4, task_type="pick_up"
        )
        assert goal != (0, 0)


def test_invalid_task_type_raises_error():
    with pytest.raises(ValueError):
        generate_maze_task(width=5, height=5, task_type="flying")


def test_length_within_requested_range():
    for _ in range(30):
        world, start, total = generate_beeper_corridor(min_length=5, max_length=10)
        assert 5 <= world.width <= 10


def test_start_position_and_direction():
    world, start, total = generate_beeper_corridor(min_length=5, max_length=5)
    assert start == (0, 0, Direction.EAST)


def test_one_beeper_places_exactly_one_per_candidate_field():
    world, start, total = generate_beeper_corridor(
        min_length=6, max_length=6, step=1, one_beeper=True, random_fields=False
    )
    for field in range(1, world.width):
        assert world.beeper_count(field, 0) == 1
    assert world.beeper_count(0, 0) == 0  # robot kreće na praznom polju
    assert total == world.width - 1


def test_random_fields_always_keep_edge_beepers():
    for _ in range(30):
        world, start, total = generate_beeper_corridor(
            min_length=8, max_length=8, step=1, one_beeper=True, random_fields=True
        )
        assert world.beeper_count(1, 0) > 0          # prvo kandidat-polje
        assert world.beeper_count(world.width - 1, 0) > 0  # poslednje kandidat-polje


def test_total_beepers_matches_world_state():
    world, start, total = generate_beeper_corridor(min_length=7, max_length=7)
    assert total == sum(world.beepers.values())
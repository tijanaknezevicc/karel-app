import pytest

from karel.robot import Direction
from karel.generator import generate_beeper_corridor


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
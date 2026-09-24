import pytest

from karel.robot import Direction
from karel.generator import (
    generate_beeper_corridor, generate_beeper_hole_corridor, generate_branching_corridor,
    generate_polyline_corridor,
)
from karel.generator import generate_maze_task, generate_multi_item_maze_task
from karel.maze import generate_polyline_corridor_structure
from karel.solver import is_solvable


def test_every_destination_has_negative_initial_count():
    world, start, source_positions, destinations = generate_multi_item_maze_task(
        width=8, height=8, num_sources=2, num_destinations=2
    )
    for pos, required in destinations.items():
        assert world.beeper_count(*pos) == -required
        assert world.has_beeper(*pos) is False


def test_source_and_destination_totals_match():
    world, start, source_positions, destinations = generate_multi_item_maze_task(
        width=8, height=8, num_sources=3, num_destinations=2
    )
    total_on_sources = sum(world.beeper_count(*pos) for pos in source_positions)
    total_needed = sum(destinations.values())
    assert total_on_sources == total_needed


def test_every_source_has_at_least_one_beeper():
    for _ in range(20):
        world, start, source_positions, destinations = generate_multi_item_maze_task(
            width=8, height=8, num_sources=3, num_destinations=2
        )
        for pos in source_positions:
            assert world.beeper_count(*pos) >= 1


def test_no_overlap_between_sources_destinations_and_start():
    world, start, source_positions, destinations = generate_multi_item_maze_task(
        width=8, height=8, num_sources=2, num_destinations=2
    )
    all_positions = source_positions + list(destinations.keys())
    assert (0, 0) not in all_positions
    assert len(all_positions) == len(set(all_positions))  # nema duplikata

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
    assert world.beepers == {}  # svet počinje bez loptica


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
        world, start, total = generate_beeper_corridor(min_length=5, max_length=10, orientation="horizontal")
        assert 5 <= world.width <= 10


def test_start_position_and_direction():
    world, start, total = generate_beeper_corridor(min_length=5, max_length=5)
    assert start == (0, 0, Direction.EAST)


def test_one_beeper_places_exactly_one_per_candidate_square():
    world, start, total = generate_beeper_corridor(
        min_length=6, max_length=6, step=1, one_beeper=True, random_squares=False, orientation="horizontal"
    )
    for square in range(1, world.width):
        assert world.beeper_count(square, 0) == 1
    assert world.beeper_count(0, 0) == 0  # robot kreće na praznom polju
    assert total == world.width - 1


def test_random_squares_always_keep_edge_beepers():
    for _ in range(30):
        world, start, total = generate_beeper_corridor(
            min_length=8, max_length=8, step=1, one_beeper=True, random_squares=True, orientation="horizontal"
        )
        assert world.beeper_count(1, 0) > 0          # prvo kandidat-polje
        assert world.beeper_count(world.width - 1, 0) > 0  # poslednje kandidat-polje


def test_vertical_orientation_places_beepers_along_y_axis():
    world, start, total = generate_beeper_corridor(
        min_length=6, max_length=6, step=1, one_beeper=True, random_squares=False, orientation="vertical"
    )
    assert world.width == 1
    assert world.height == 6
    for square in range(1, world.height):
        assert world.beeper_count(0, square) == 1


def test_total_beepers_matches_world_state():
    world, start, total = generate_beeper_corridor(min_length=7, max_length=7)
    assert total == sum(world.beepers.values())


def test_end_without_hole_puts_beepers_on_last_square():
    world, start, total = generate_beeper_corridor(
        min_length=5, max_length=5, spread=False, with_final_hole=False,
        one_beeper=True, orientation="horizontal"
    )
    assert world.beeper_count(4, 0) == 1
    assert total == 1
    for square in range(4):
        assert world.beeper_count(square, 0) == 0


def test_end_with_hole_splits_beepers_and_hole():
    world, start, total = generate_beeper_corridor(
        min_length=5, max_length=5, spread=False, with_final_hole=True,
        one_beeper=False, orientation="horizontal"
    )
    beepers_on_second_to_last = world.beeper_count(3, 0)
    assert beepers_on_second_to_last == total
    assert world.beeper_count(4, 0) == -total  # rupa očekuje tačno taj broj


def test_spread_with_final_hole_raises_error():
    with pytest.raises(ValueError):
        generate_beeper_corridor(spread=True, with_final_hole=True)


def test_end_with_hole_and_too_short_corridor_raises_error():
    with pytest.raises(ValueError):
        generate_beeper_corridor(min_length=2, max_length=2, spread=False, with_final_hole=True)

def test_hole_corridor_pairs_match_exactly():
    world, start, total = generate_beeper_hole_corridor(
        min_pairs=3, max_pairs=3, one_beeper=False, orientation="horizontal"
    )
    num_pairs = 3
    running_total = 0
    for k in range(num_pairs):
        beeper_square = 1 + 2 * k
        hole_square = beeper_square + 1
        amount = world.beeper_count(beeper_square, 0)
        assert amount > 0
        assert world.beeper_count(hole_square, 0) == -amount
        running_total += amount
    assert running_total == total


def test_hole_corridor_one_beeper_gives_exactly_one_per_pair():
    world, start, total = generate_beeper_hole_corridor(
        min_pairs=4, max_pairs=4, one_beeper=True, orientation="horizontal"
    )
    for k in range(4):
        beeper_square = 1 + 2 * k
        assert world.beeper_count(beeper_square, 0) == 1
    assert total == 4


def test_hole_corridor_vertical_orientation():
    world, start, total = generate_beeper_hole_corridor(
        min_pairs=2, max_pairs=2, one_beeper=True, orientation="vertical"
    )
    assert world.width == 1
    assert world.height == 5  # 2*2 + 1
    assert world.beeper_count(0, 1) == 1
    assert world.beeper_count(0, 2) == -1
    assert world.beeper_count(0, 3) == 1
    assert world.beeper_count(0, 4) == -1


def test_hole_corridor_length_matches_pair_count():
    world, start, total = generate_beeper_hole_corridor(
        min_pairs=5, max_pairs=5, orientation="horizontal"
    )
    assert world.width == 11  # 2*5 + 1

def test_branching_corridor_always_has_at_least_one_beeper():
    for _ in range(30):
        world, start, total = generate_branching_corridor(
            min_length=6, max_length=8, branch_probability=0.1  # namerno nizak, da isprovociramo fallback
        )
        assert total > 0


def test_branching_corridor_total_matches_world_state():
    world, start, total = generate_branching_corridor(min_length=8, max_length=8)
    assert sum(world.beepers.values()) == total


def test_branching_corridor_start_faces_east():
    world, start, total = generate_branching_corridor(min_length=6, max_length=6, orientation="horizontal")
    assert start == (0, 1, Direction.EAST)


def test_branching_corridor_vertical_start_position():
    world, start, total = generate_branching_corridor(min_length=6, max_length=6, orientation="vertical")
    assert start == (1, 0, Direction.EAST)


def test_branching_corridor_no_branch_on_first_or_last_square():
    world, start, total = generate_branching_corridor(
        min_length=6, max_length=6, branch_probability=1.0, orientation="horizontal"  # svako polje granа
    )
    # ni prvo (x=0) ni poslednje (x=5) polje glavne linije ne sme imati lopticu na bočnoj strani
    assert world.beeper_count(0, 0) == 0
    assert world.beeper_count(0, 2) == 0
    assert world.beeper_count(5, 0) == 0
    assert world.beeper_count(5, 2) == 0


def test_invalid_num_segments_raises_error():
    with pytest.raises(ValueError):
        generate_polyline_corridor_structure(num_segments=5, side_length=3)


def test_l_shape_produces_beepers():
    for _ in range(20):
        world, start, total = generate_polyline_corridor(min_side=2, max_side=5, num_segments=2)
        assert total > 0


def test_u_shape_total_beepers_matches_world_state():
    world, start, total = generate_polyline_corridor(min_side=3, max_side=3, num_segments=3)
    assert total == sum(world.beepers.values())


def test_square_produces_beepers_without_crashing():
    for _ in range(20):
        world, start, total = generate_polyline_corridor(min_side=2, max_side=5, num_segments=4)
        assert total > 0


def test_start_square_never_gets_a_beeper():
    for _ in range(20):
        world, start, total = generate_polyline_corridor(min_side=2, max_side=5, num_segments=3)
        x, y, direction = start
        assert world.beeper_count(x, y) == 0


def test_square_closing_square_never_gets_a_beeper():
    for _ in range(20):
        world, start, total = generate_polyline_corridor(min_side=2, max_side=4, num_segments=4)
        x, y, direction = start
        assert world.beeper_count(x, y) == 0


def test_l_and_u_goal_is_reachable_from_start():
    for num_segments in (2, 3):
        for _ in range(20):
            world, path = generate_polyline_corridor_structure(num_segments, side_length=3)
            start = (*path[0], Direction.NORTH)
            goal = path[-1]
            assert is_solvable(world, start, goal) is True


def test_square_path_closes_back_to_start():
    world, path = generate_polyline_corridor_structure(num_segments=4, side_length=3)
    assert path[0] == path[-1]


def test_l_and_u_path_does_not_close():
    for num_segments in (2, 3):
        world, path = generate_polyline_corridor_structure(num_segments, side_length=3)
        assert path[0] != path[-1]

def test_polyline_fixed_shape_stays_same_across_calls():
    # isti initial_direction/turn, razlicita duzina — oblik (niz pravaca) mora biti isti
    world1, path1 = generate_polyline_corridor_structure(
        num_segments=2, side_length=3, initial_direction=Direction.NORTH, turn="right"
    )
    world2, path2 = generate_polyline_corridor_structure(
        num_segments=2, side_length=5, initial_direction=Direction.NORTH, turn="right"
    )
    # oba kreću u istom pravcu iz (0,0) — prva dva koraka moraju biti identична
    assert path1[1] == path2[1]


def test_polyline_random_squares_still_keeps_edge_beepers():
    for _ in range(30):
        world, start, total = generate_polyline_corridor(
            min_side=6, max_side=6, num_segments=2, one_beeper=True, random_squares=True
        )
        assert total > 0  # bar ivice su uvek pokrivene, isto svojstvo kao kod obicnog hodnika
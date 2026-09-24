import random

from karel.grader import (
    _as_maker,
    maze_pick_up_task, maze_put_down_task, maze_both_task, maze_multi_item_task,
    beeper_corridor_counting_task, beeper_corridor_two_square_task,
    beeper_corridor_end_task, beeper_corridor_end_hole_task, beeper_hole_corridor_task,
    make_beeper_corridor_conditional_task, make_polyline_task,
    make_classic_maze_task, make_beeper_corridor_random_squares_task,
    make_branching_corridor_task, grade,
)


def _uslovna_polyline_maker():
    return make_polyline_task(random_squares=False)

def _grananje_polyline_maker():
    return make_polyline_task(random_squares=True)


LINIJSKI = [
    (_as_maker(maze_pick_up_task), 1),
    (_as_maker(maze_put_down_task), 1),
    (_as_maker(maze_both_task), 1),
    (_as_maker(maze_multi_item_task), 1),
]

BROJACKA_PETLJA = [
    (_as_maker(beeper_corridor_counting_task), 1),
    (_as_maker(beeper_corridor_two_square_task), 1),
    (_as_maker(beeper_corridor_end_task), 1),
    (_as_maker(beeper_corridor_end_hole_task), 1),
    (_as_maker(beeper_hole_corridor_task), 1),
]

USLOVNA_PETLJA = [
    (make_beeper_corridor_conditional_task, 5),
    (_uslovna_polyline_maker, 5),
]

GRANANJE = [
    (make_beeper_corridor_random_squares_task, 5),
    (_grananje_polyline_maker, 5),
    (make_classic_maze_task, 5),
    (make_branching_corridor_task, 5),
]

NAPREDNI = BROJACKA_PETLJA + USLOVNA_PETLJA + GRANANJE

LEVEL_TASKS = {
    "linijski": LINIJSKI,
    "brojacka_petlja": BROJACKA_PETLJA,
    "uslovna_petlja": USLOVNA_PETLJA,
    "grananje": GRANANJE,
    "napredni": NAPREDNI,
}


def grade_with_random_task(code, level):
    maker, num_variations = random.choice(LEVEL_TASKS[level])
    task_factory = maker()
    return grade(code, level, task_factory, num_variations)
from karel.grader import (
    maze_pick_up_task,
    maze_put_down_task,
    maze_both_task,
    maze_multi_item_task,
    beeper_corridor_counting_task,
    beeper_corridor_conditional_task,
)

LEVEL_TASKS = {
    "linijski": {
        "factories": [maze_pick_up_task, maze_put_down_task, maze_both_task, maze_multi_item_task],
        "num_variations": 1,
    },
    "brojacka_petlja": {
        "factories": [beeper_corridor_counting_task],
        "num_variations": 1,
    },
    "uslovna_petlja": {
        "factories": [beeper_corridor_conditional_task],
        "num_variations": 5,
    },
    "grananje": {
        "factories": [],  # generator jos ne postoji
        "num_variations": 5,
    },
    "napredni": {
        "factories": [],  # generator jos ne postoji
        "num_variations": 5,
    },
}
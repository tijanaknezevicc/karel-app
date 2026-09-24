import pytest

from karel.task_registry import LEVEL_TASKS, grade_with_random_task


ALL_LEVELS = ["linijski", "brojacka_petlja", "uslovna_petlja", "grananje", "napredni"]


def test_all_levels_are_present_and_non_empty():
    for level in ALL_LEVELS:
        assert level in LEVEL_TASKS
        assert len(LEVEL_TASKS[level]) > 0


def test_every_maker_produces_a_valid_task_factory():
    for level in ALL_LEVELS:
        for maker, num_variations in LEVEL_TASKS[level]:
            assert callable(maker)
            assert isinstance(num_variations, int)
            assert num_variations >= 1

            task_factory = maker()
            assert callable(task_factory)

            world, start, initial_beepers, success = task_factory()
            assert len(start) == 3  # (x, y, Direction)
            assert isinstance(initial_beepers, int)
            assert callable(success)


def test_grade_with_random_task_never_crashes():
    trivial_codes = ["napred()", "napred()\nlevo()\nnapred()", "uzmi()", ""]

    for level in ALL_LEVELS:
        for code in trivial_codes:
            for _ in range(5):  # svaki level ima vise moguci zadataka, probaj vise puta
                result = grade_with_random_task(code, level)
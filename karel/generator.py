import random

from karel.maze import generate_perfect_maze
from karel.robot import Direction
from karel.solver import is_solvable
from karel.world import World


def _random_field(width, height, exclude=None):
    if exclude is None:
        exclude = []
    while True:
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        if (x, y) not in exclude:
            return x, y

def generate_maze_task(width, height, task_type="pick_up", one_beeper=True):
    world = World(width=width, height=height)
    generate_perfect_maze(world)

    start = (0, 0, Direction.EAST)
    goal = _random_field(width, height, exclude={(0, 0)})
    initial_beepers = 0
    item_position = None

    if task_type == "pick_up":
        if one_beeper:
            world.add_beeper(*goal)
        else:
            world.add_beeper(*goal, random.randint(1, 30))

    elif task_type == "put_down":
        if one_beeper:
            initial_beepers = 1
        else:
            initial_beepers = random.randint(1, 30)

    elif task_type == "both":
        item_position = _random_field(width, height, exclude={(0, 0), goal})
        if one_beeper:
            world.add_beeper(*item_position)
        else:
            beepers_to_add = random.randint(1, 30)
            world.add_beeper(*item_position, beepers_to_add)
    else:
        raise ValueError("Invalid task type. Must be 'pick_up', 'put_down' or 'both'.")

    if is_solvable(world, start, goal):
        return world, start, goal, initial_beepers, item_position
    else:
        raise RuntimeError("Generated maze is unsolvable!")

def generate_beeper_corridor(min_length=5, max_length=10, step=1, one_beeper=True, random_fields=False):

    length = random.randint(min_length, max_length)
    world = World(width=length, height=1)  
    beepers_added = 0

    candidate_fields = list(range(1, length, step)) # robot starts on empty field
    
    for field in candidate_fields:
        is_edge_field = (field == candidate_fields[0] or field == candidate_fields[-1]) # to prevent generating a corridor with no beepers        
        if random_fields and random.random() < 0.4 and not is_edge_field:
            continue  # skip this field

        if one_beeper:
            world.add_beeper(field, 0, 1)
            beepers_added += 1
        else:
            beepers_to_add = random.randint(1, 30)
            world.add_beeper(field, 0, beepers_to_add)
            beepers_added += beepers_to_add

    start = (0, 0, Direction.EAST)
    if is_solvable(world, start, (length - 1, 0)):
        return world, start, beepers_added    
    else:
        raise RuntimeError("generisani lavirint je nerešiv!")
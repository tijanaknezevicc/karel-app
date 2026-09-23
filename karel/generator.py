import random

from karel.robot import Direction
from karel.solver import is_solvable
from karel.world import World




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
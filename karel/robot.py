from enum import Enum

from karel.exceptions import KarelRuntimeError, NoBeeperError, NoBeepersToPutError, OutOfBoundsError, WallCollisionError


class Direction(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

def direction_delta(direction):
    if direction == Direction.NORTH:
        return (0, 1)
    elif direction == Direction.EAST:
        return (1, 0)
    elif direction == Direction.SOUTH:
        return (0, -1)
    elif direction == Direction.WEST:
        return (-1, 0)
    else:
        raise ValueError("Invalid direction")

class Robot:
    def __init__(self, x=0, y=0, direction=Direction.NORTH):
        self.x = x
        self.y = y
        self.direction = direction
        self.beepers = 0
        self.world = None
        self.on_step = None  # callback for each step, can be set externally

    def _notify_step(self):
        if self.on_step is not None:
            self.on_step()
    
    def place_in_world(self, world):
        self.world = world

    def _ensure_in_world(self):
        if self.world is None:
            raise KarelRuntimeError("Robot Karel nije postavljen u lavirint!")

    def _next_position(self):
        delta_x, delta_y = direction_delta(self.direction)
        return (self.x + delta_x, self.y + delta_y)

    def can_move_forward(self): # moze_napred()
        self._ensure_in_world()
        _x, _y = self._next_position()
        return not self.world.is_blocked(self.x, self.y ,_x, _y)

    def move_forward(self): # napred()
        self._ensure_in_world()
        _x, _y = self._next_position()

        if self.world.out_of_bounds(_x, _y):
            raise OutOfBoundsError("Robot Karel je izašao izvan granica lavirinta!")
        elif self.world.has_wall(self.x, self.y, _x, _y):
            raise WallCollisionError("Robot Karel je udario u zid!")
        else:
            self.x = _x
            self.y = _y
        self._notify_step()

    def turn_right(self): # desno()
        self.direction = Direction((self.direction.value + 1) % 4)
        self._notify_step()

    def turn_left(self): # levo()
        self.direction = Direction((self.direction.value + 3) % 4)
        self._notify_step()

    def beeper_present_on_field(self): # ima_loptica_na_polju()
        self._ensure_in_world()
        return self.world.has_beeper(self.x, self.y)

    def beeper_count_on_field(self): # broj_loptica_na_polju()
        self._ensure_in_world()
        return self.world.beeper_count(self.x, self.y)

    def beepers_present_in_bag(self): # ima_loptica_kod_sebe()
        return self.beepers > 0

    def beeper_count_in_bag(self): # broj_loptica_kod_sebe()
        return self.beepers    

    def put_beeper(self): # ostavi()
        self._ensure_in_world()

        if self.beepers <= 0:
            raise NoBeepersToPutError("Robot Karel nema loptica za postavljanje!")
        self.beepers -= 1
        self.world.add_beeper(self.x, self.y)
        self._notify_step()

    def pick_beeper(self): # uzmi()
        self._ensure_in_world()

        if not self.world.has_beeper(self.x, self.y):
            raise NoBeeperError("Na ovom polju ne postoji loptica!")
        self.world.remove_beeper(self.x, self.y)
        self.beepers += 1
        self._notify_step()

    def get_position(self):
        return (self.x, self.y)

    def get_direction(self):
        return self.direction


class World:
    def __init__(self, width, height, walls=None, beepers=None):
        self.width = width
        self.height = height
        self.walls = walls if walls is not None else set()
        self.beepers = beepers if beepers is not None else dict()

    def is_wall(self, x, y):
        return (x, y) in self.walls

    def out_of_bounds(self, x, y):
        return x < 0 or x >= self.width or y < 0 or y >= self.height

    def is_blocked(self, x, y):
        return self.is_wall(x, y) or self.out_of_bounds(x, y)

    def has_beeper(self, x, y):
        return (x, y) in self.beepers

    def add_beeper(self, x, y):
        self.beepers[(x, y)] = self.beepers.get((x, y), 0) + 1

    def remove_beeper(self, x, y):
        if (x, y) in self.beepers:
            self.beepers[(x, y)] -= 1
            if self.beepers[(x, y)] == 0:
                del self.beepers[(x, y)]

    def beeper_count(self, x, y):
        return self.beepers.get((x, y), 0)


class World:
    def __init__(self, width, height, walls=None, beepers=None):
        self.width = width
        self.height = height
        self.walls = walls if walls is not None else set()
        self.beepers = beepers if beepers is not None else dict()

    def has_wall(self, x1, y1, x2, y2):
        return frozenset({(x1, y1), (x2, y2)}) in self.walls

    def add_wall(self, x1, y1, x2, y2): # for maze generator
        self.walls.add(frozenset({(x1, y1), (x2, y2)}))

    def remove_wall(self, x1, y1, x2, y2): # for maze generator
        self.walls.discard(frozenset({(x1, y1), (x2, y2)})) # ignores if wall doesn't exist

    def out_of_bounds(self, x, y):
        return x < 0 or x >= self.width or y < 0 or y >= self.height

    def is_blocked(self, x1, y1, x2, y2):
        return self.has_wall(x1, y1, x2, y2) or self.out_of_bounds(x2, y2)

    def has_beeper(self, x, y):
        return (x, y) in self.beepers

    def add_beeper(self, x, y, count=1):
        self.beepers[(x, y)] = self.beepers.get((x, y), 0) + count

    def remove_beeper(self, x, y):
        if (x, y) in self.beepers:
            self.beepers[(x, y)] -= 1
            if self.beepers[(x, y)] == 0:
                del self.beepers[(x, y)]

    def beeper_count(self, x, y):
        return self.beepers.get((x, y), 0)
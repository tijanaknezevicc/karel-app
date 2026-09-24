class KarelRuntimeError(Exception):
    # Karel runtime errors
    pass

class WallCollisionError(KarelRuntimeError):
    # Karel collides with a wall
    pass

class OutOfBoundsError(KarelRuntimeError):
    # Karel tries to move outside the world boundaries
    pass

class NoBeeperError(KarelRuntimeError):
    # Karel tries to pick up a beeper but there are none
    pass

class NoBeepersToPutError(KarelRuntimeError):
    # Karel tries to put a beeper but has none
    pass

class InvalidCommandError(Exception):
    # Invalid command given to Karel
    pass

class InfiniteLoopError(KarelRuntimeError):
    # Karel is stuck in an infinite loop
    pass
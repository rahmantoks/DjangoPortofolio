from enum import Enum

class Collisions(Enum):
    NO_COLLISION = 0
    SELF_COLLISION = 1
    OTHER_COLLISION = 2
    BOUNDARY_COLLISION = 3

class Directions(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    
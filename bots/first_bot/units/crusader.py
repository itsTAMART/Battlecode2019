#
from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import random


def crusade(self):

    # The directions: North, NorthEast, East, SouthEast, South, SouthWest, West, NorthWest
    choices = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
    choice = random.choice(choices)
    self.log('try to move ' + str(choice))
    return self.move(*choice)

#

#
from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import random
from ..utils import *


def first_turn_crusader(self):
    # TODO do tings like choosing which castle you represent with the map
    self.nav = Navigation()
    self.combat = CombatManager(self)
    return



def crusade(self):
    self.combat.turn(self)

    # The directions: North, NorthEast, East, SouthEast, South, SouthWest, West, NorthWest
    choices = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
    choice = random.choice(choices)
    self.log('try to move ' + str(choice))
    return self.move(*choice)

#

from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import random

from bots.first_bot.utils import *


def castle(self):
    if can_build('PILGRIM'):
        self.log("Building a pilgrim at " + str(self.me['x'] + 1) + ", " + str(self.me['y'] + 1))
        return self.build_unit(SPECS['PILGRIM'], 1, 1)

    else:
        self.log("Castle health: " + self.me['health'])

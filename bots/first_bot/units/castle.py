from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import random


def castle(self):
    if self.step < 10:
        self.log("Building a crusader at " + str(self.me['x'] + 1) + ", " + str(self.me['y'] + 1))
        return self.build_unit(SPECS['CRUSADER'], 1, 1)

    else:
        self.log("Castle health: " + self.me['health'])

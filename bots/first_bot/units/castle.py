
from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import random

from bots.first_bot.utils import *



def castle(self):
    order = naive_build(self, 'PILGRIM')
    if order is not None:
        return order
    else:
        self.log("Castle health: " + self.me['health'])

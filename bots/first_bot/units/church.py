#
from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import random

from bots.first_bot.utils import *
from ..tactics import *


def first_turn_church(self):
    self.build_order = BuildOrderManager(BUILD_ORDER)

    self.map_process.filter_mines_for_church(self)
    self.comms.hello_church(self)

    # Debug
    self.map_process.log_lists(self)



def church(self):
    self.log("church health: " + self.me['health'])
    # Select what to build
    order = self.build_order.turn_build(self)
    if order is not None:
        # self.log('built correctly')
        return order
    else:
        # self.log("Not building this time")
        pass


#

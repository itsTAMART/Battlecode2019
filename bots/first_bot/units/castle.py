#
from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import random

from bots.first_bot.utils import *
from ..tactics import *


def first_turn_castle(self):
    # TODO do tings like choosing which castle you represent with the map
    self.build_order = BuildOrderManager(BUILD_ORDER)
    return


def castle(self):
    # Select what to build
    order = naive_build(self, self.build_order.current_order())
    if order is not None:
        self.build_order.built_correctly()
        return order
    else:
        self.log("Not building this time")

#

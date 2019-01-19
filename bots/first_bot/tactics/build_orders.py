#
from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
from bots.first_bot.utils import *

FIRST_BUILD_ORDER = ["PILGRIM", "CRUSADER", "CRUSADER",
                     "PILGRIM", "CRUSADER", "CRUSADER",
                     "PILGRIM", "PILGRIM", "CRUSADER"]

ECON_BUILD_ORDER = ["PILGRIM", "PILGRIM", "PILGRIM",
                    "PILGRIM", "PILGRIM", "CRUSADER",
                    "PILGRIM", "CRUSADER", "PILGRIM"]

BUILD_ORDER = ECON_BUILD_ORDER


def naive_build(bc, unit_name):
    """
    tries to build around
    :param bc: battlecode object
    :param unit_name: name of the unit to build e.g. PILGRIM
    :return: True if you have materials to build unit
    """
    my_x = bc.me.x
    my_y = bc.me.y
    choices = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
    for dx, dy in choices:
        if can_build(bc, unit_name, my_x + dx, my_y + dy):
            bc.log("Building a {} at [{}, {}]".format(unit_name, bc.me['x'] + dx, bc.me['y'] + dy))
            return bc.build_unit(SPECS[unit_name], dx, dy)
    return None



# TODO test
class BuildOrderManager(object):
    # TODO something left to synchronize castles

    # Reserve materials
    reserve_karb = 0
    reserve_fuel = 0

    # Unit counters
    total_units = 0
    pilgrims_built = 0
    total_crusaders = 0
    crusaders_built = 0
    total_prophets = 0
    prophets_built = 0
    total_preacher = 0
    preacher_built = 0




    def __init__(self, build_order):
        self.build_order = build_order
        self.build_step = 0

    def current_order(self):
        build_step = min(self.build_step, len(self.build_order) - 1)  # Hacky -1 to keep it in bounds
        return self.build_order[build_step]

    def next_order(self):
        build_step = min(self.build_step, len(self.build_order) - 2)  # Hacky -2 to keep it in bounds
        return self.build_order[build_step + 1]

    def built_correctly(self, bc):
        build_step = min(self.build_step, len(self.build_order) - 2)  # Hacky -2 to keep it in bounds
        if self.build_order[build_step + 1] == 'PILGRIM':
            bc.log('sending the pilgrim the next mine location')
            next_mine = bc.map_process.next_mine(bc)
            bc.comms.send_loc(bc, next_mine, 2, code=T2C['YOUR_MINE_IS'])  # SEND THE PILGRIM THE LOCATION TO ITS MINE
        self.build_step += 1
        self.build_step = min(self.build_step, len(self.build_order) - 1)  # Hacky -2 to keep it in bounds

#

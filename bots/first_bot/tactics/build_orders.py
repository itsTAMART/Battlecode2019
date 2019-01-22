#
from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
from bots.first_bot.utils import *

FIRST_BUILD_ORDER = ["PILGRIM", "CRUSADER", "CRUSADER",
                     "PILGRIM", "CRUSADER", "CRUSADER",
                     "PILGRIM", "PILGRIM", "CRUSADER"]

ECON_BUILD_ORDER = ["PILGRIM", "PILGRIM", "PILGRIM",
                    "PILGRIM", "PILGRIM",
                    "PILGRIM", "PILGRIM"]

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


def dir_build(bc, unit_name, target):
    """
    tries to build around
    :param bc: battlecode object
    :param unit_name: name of the unit to build e.g. PILGRIM
    :return: True if you have materials to build unit
    """
    my_x, my_y = locate(bc.me)
    dx, dy = bc.nav.goto(bc, target)
    if can_build(bc, unit_name, my_x + dx, my_y + dy):
        bc.log("Building a {} at [{}, {}]".format(unit_name, bc.me['x'] + dx, bc.me['y'] + dy))
        return bc.build_unit(SPECS[unit_name], dx, dy)
    return None


# TODO implement building logic
"""
TODO: here I will include what to build for each strat. with flags

for ECON: build pilgrim with destiny to middle mine and save_for_church = True
          check if other castles are going for eco and mark it too.

for RUSH: create phrophet, phrophet, crusader (maybe?) and give them the rush target
          check if other castles in rush so that chuch comes later
          
for FAKE_RUSH: creathe phrophet, pilgrim and save for church
                check if other castles are going for FAKE_RUSH and mark it too.

GENERALLY create pilgrims for each of the mines you have assigned

Create pilgrims for karbonite first except if RUSH then go for fuel

if BEING_ATTACKED create counter phrophet: crusader, crusader: preacher, preacher: phrophets

if no pilgrims left to mine start creating a PHROPHETS for ARCHER LATTICE

"""

# TODO test
class BuildOrderManager(object):


    # Reserve materials
    reserve_karb = 0
    reserve_fuel = 0

    # Tasks
    pilgrim_tasks = {}

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

    def check_pilgrims_alive(self):
        # We assign each pilgrim to a task, and we have to check if they are doing it
        # TODO implement check_pilgrims_alive
        pass


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

    def build_pilgrim(self, bc, target=None):
        # If target is none, then pilgrim is a scout
        if target is None:
            bc.log('trying to build a scout pilgrim')
            castle = bc.nav.closest_enemy_castle(bc)
            if castle is None:
                return naive_build(bc, 'PILGRIM')
            else:
                return dir_build(bc, 'PILGRIM', castle)
        else:
            return dir_build(bc, 'PILGRIM', target)





#

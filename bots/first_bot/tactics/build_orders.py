#
from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
from bots.first_bot.utils import *

FIRST_BUILD_ORDER = ["PILGRIM", "CRUSADER", "CRUSADER",
                     "PILGRIM", "CRUSADER", "CRUSADER",
                     "PILGRIM", "PILGRIM", "CRUSADER"]

ECON_BUILD_ORDER = ["PILGRIM", "PILGRIM", "PILGRIM",
                    "PILGRIM", "PILGRIM"]
ECON_TARGET_ORDER = ["m", "m", "m", "m", "m"]

RUSH_BUILD_ORDER = ["PILGRIM", "PROPHET", "PROPHET",
                    "PILGRIM", "PREACHER"]

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


#

"""
BuilOrderManager: here I will include what to build for each strat. with flags

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
    """building logic object"""


    # Reserve materials
    reserve_karb = 0
    reserve_fuel = 0
    issued_churches = 0

    # Tasks
    pilgrim_tasks = {}

    # build steps
    build_step = 0
    build_order = []
    target_order = []

    # Unit counters
    total_units = 0
    pilgrims_built = 0
    total_crusaders = 0
    crusaders_built = 0
    total_prophets = 0
    prophets_built = 0
    total_preacher = 0
    preacher_built = 0

    def __init__(self, build_order=ECON_BUILD_ORDER):
        self.build_order = build_order
        self.build_step = 0

    # TODO test
    def turn_build(self, bc):
        """
        Chooses what to build, returns an order or None
        :param bc:
        :return: order or None to return from robot
        """
        """
        PRIORITY CASES
            Type of Game Build order
            Def from rush
            Def pilgrim
            Pilgrims for my mines
            Defensive lattice

        """
        if bc.karbonite < self.reserve_karb and bc.fuel < self.reserve_fuel:
            return None

        order = None
        # Type of Game Build order
        if self.build_step < 6 and bc.me.unit == SPECS["CASTLE"]:
            bc.log('First turns build orders')
            self.build_order_from_gametype(bc)
            unit = self.current_order()
            bc.log('    build order {}'.format(self.build_order))
            bc.log('    trying to build {}'.format(unit))
            if self.enough_for_unit(bc, unit):
                # bc.log('enough pela')
                target = self.current_target(bc)
                bc.log('    target: {}'.format(target))
                order = dir_build(bc, unit, target)
                if order is not None:
                    bc.comms.send_loc(bc, target, 2,
                                      code=T2C['YOUR_MINE_IS'])  # SEND THE unit THE LOCATION TO ITS target
                    self.built_correctly(bc)
                    return order
                else:
                    bc.log('    all directions occupied')

        # Def from rush
        # Def pilgrim
        if bc.tactics.under_attack(bc):
            bc.log('We are under attack')
            unit = bc.tactics.counter_unit(bc)
            target = locate(bc.combat.lowest_health_enemy())
            order = dir_build(bc, unit, target)
            bc.log('    unit: {}, target: {}'.format(unit, target))
            if order is not None:
                bc.comms.send_loc(bc, target, 2,
                                  code=T2C['YOUR_MINE_IS'])  # SEND THE unit THE LOCATION TO ITS target
                self.built_correctly(bc)
                return order
            else:
                bc.log('    could not build deffensive units')

        # TODO if missing pilgrims:
        # Pilgrims for my mines
        unit = "PILGRIM"
        if self.enough_for_unit(bc, unit):
            target = bc.map_process.next_mine(bc)
            if target is not None:
                order = dir_build(bc, unit, target)
                bc.log('unit: {}, target: {}'.format(unit, target))
                if order is not None:
                    bc.comms.send_loc(bc, target, 2,
                                      code=T2C['YOUR_MINE_IS'])  # SEND THE unit THE LOCATION TO ITS target
                    self.built_correctly(bc)
                    return order
                else:
                    bc.log('    no more pilgrims left to build')

        # # Defensive lattice
        # # Offensive lattice?
        # unit = bc.tactics.lategame_unit(bc)
        # target = bc.tactics.lategame_target(bc)
        # if self.enough_for_unit(bc, unit):
        #     if target is not None:
        #         order = dir_build(bc, unit, target)
        #         bc.log('unit: {}, target: {}'.format(unit, target))
        #         if order is not None:
        #             bc.comms.send_loc(bc, target, 2,
        #                               code=T2C['YOUR_MINE_IS'])  # SEND THE unit THE LOCATION TO ITS target
        #             self.built_correctly(bc)
        #             return order
        #         else:
        #             bc.log('could not build')

        # Finally return whatever you chose, probably None
        bc.log('not building this time')
        return order
        #

    def build_order_from_gametype(self, bc):
        if bc.tactics.RUSH:
            self.build_order = RUSH_BUILD_ORDER
            self.target_order = bc.tactics.get_rush_targets(bc)
            return
        if bc.tactics.ECON:
            self.build_order = ECON_BUILD_ORDER
            self.target_order = ECON_TARGET_ORDER
            return
        if bc.tactics.FAKE_RUSH:
            self.build_order = ECON_BUILD_ORDER
            self.target_order = ECON_TARGET_ORDER
            return

        # ECON by default
        self.build_order = ECON_BUILD_ORDER
        self.target_order = ECON_TARGET_ORDER
        return

    def check_pilgrims_alive(self):
        # We assign each pilgrim to a task, and we have to check if they are doing it
        # TODO implement check_pilgrims_alive
        pass

    # TODO test
    def current_order(self):
        if self.build_step < len(self.build_order):
            return self.build_order[self.build_step]
        else:
            return None

    def current_target(self, bc):
        bc.log('build step: {}'.format(self.build_step))
        # bc.log('target order: {}'.format(self.target_order))
        if self.build_step < len(self.target_order):
            target = self.target_order[self.build_step]
            # bc.log('    target {}'.format(target))
            if target == 'm':
                target = bc.map_process.next_mine(bc)
                # bc.log('        target {}'.format(target))
            return target
        else:
            return None

    def built_correctly(self, bc):
        """ build confirmation, increase the build step index"""
        # bc.log('built correctly')
        self.build_step += 1

    # TODO test
    def save_for_church(self, bc):
        bc.log('saving for church')
        self.issued_churches += 1
        if self.issued_churches % 2 == 1:  # Only increase the savings for each odd(impar) church
            self.reserve_karb += 50
            self.reserve_fuel += 200

    # TODO test
    def church_built(self, bc):
        bc.log('church built')
        if self.issued_churches % 2 == 1:  # Only decrease the savings for each odd(impar) church
            self.reserve_karb -= 50
            self.reserve_fuel -= 200
        self.issued_churches -= 1
        self.reserve_karb = max(self.reserve_karb, 0)
        self.reserve_fuel = max(self.reserve_fuel, 0)

    def enough_for_unit(self, bc, unit):
        """ returns True if you have enough materials """
        if unit is None:
            return False
        unit_k_cost = SPECS['UNITS'][SPECS[unit]]['CONSTRUCTION_KARBONITE']
        unit_f_cost = SPECS['UNITS'][SPECS[unit]]['CONSTRUCTION_FUEL']

        return bc.karbonite >= self.reserve_karb + unit_k_cost \
               and bc.fuel >= self.reserve_fuel + unit_f_cost


#

#
from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import random

from bots.first_bot.utils import *
from ..tactics import *


def first_turn_castle(self):
    # TODO Tactics somewhere
    self.build_order = BuildOrderManager()

    # Debug
    self.map_process.log_lists(self)


def second_third_turns_castles(self):
    self.comms.send_initial_castle_location(self)
    self.comms.receive_initial_castle_location(self)
    # self.log('second_third_turns_castles:')




def castle(self):
    # Shenanigans to get castle locations
    if self.step < 3:
        # self.log('{} turn'.format(self.step))
        second_third_turns_castles(self)
    # Part 2 of map processing
    if self.step == 3:
        self.map_process.get_initial_game_info_2(self)
        # Debug
        self.map_process.log_lists(self)

    # Select what to build
    order = self.build_order.turn_build(self)
    if order is not None:
        self.log('built correctly')
        return order
    else:
        self.log("Not building this time")

    target = self.combat.lowest_health_enemy()
    self.log('attack target: {}'.format(target))
    if target is not None:
        if can_attack(self, *locate(target)):
            self.log('attack:')
            self.log(locate(target))  # TODO test
            return self.attack(*difference_to(locate(self.me), locate(target)))

#

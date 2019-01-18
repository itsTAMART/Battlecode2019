#
from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import random

from bots.first_bot.utils import *
from ..tactics import *


def first_turn_castle(self):
    # TODO do tings like choosing which castle you represent with the map
    self.build_order = BuildOrderManager(BUILD_ORDER)
    # self.map_process = MapPreprocess()
    # self.comms = Communications(self)
    # self.map_process.get_initial_game_info(self)
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

    # #Debug
    # self.log('castle coords')
    # self.log(self.comms.castle_coords)
    # # self.log(self.vision_list)

    # Select what to build
    order = naive_build(self, self.build_order.current_order())
    if order is not None:
        self.build_order.built_correctly()
        return order
    else:
        self.log("Not building this time")

#

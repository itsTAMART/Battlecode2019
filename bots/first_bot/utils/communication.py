#
from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
from bots.first_bot.utils import *


class Communications(object):
    """
    manages communications between robots

    """
    sent_first_part = False
    received_first_part = False

    def __init__(self, bc):
        self.my_team = team(bc.me)

    def turn(self, bc):
        pass  # TODO

    def send_loc(self, bc):
        pass  # TODO

    def receive_loc(self, bc):
        pass  # TODO

    def send_castle_talk(self, bc, message):
        pass  # TODO

    def receive_castle_talk(self, bc):
        pass  # TODO

    def send_initial_castle_location(self, bc):
        """ sends initial castle location in 2 steps"""
        # If im a castle
        if bc.me.unit != SPECS['CASTLE']:
            return
        # In the first 3 turns
        if bc.turn > 4:
            return
        # Has it sended a first time? No:
        if not self.sent_first_part:
            # If map is horizontally reflected:
            if bc.map_process.horizontal_reflection:
                # send first x
                self.send_castle_talk(bc, bc.me.x)
            #  If map is vertically reflected :
            else:
                # send first y
                self.send_castle_talk(bc, bc.me.y)
            #   save a flag for first sent
            self.sent_first_part = True

        # Yes:when called again
        else:
            # If map is horizontally reflected:
            if bc.map_process.horizontal_reflection:
                # send first y
                self.send_castle_talk(bc, bc.me.y)
            #  If map is vertically reflected :
            else:
                # send first x
                self.send_castle_talk(bc, bc.me.x)
        return

    def receive_initial_castle_location(self, bc):
        # If im a castle
        # In the first 3 turns
        # Has it received a first time?
        # No:
        #   If map is horizontally reflected:receive first x
        #   If map is vertically reflected :receive first y
        #   save a flag for first received
        # Yes:when called again
        #   If map is horizontally reflected:receive y
        #   If map is vertically reflected :receive x
        #

        # TODO do it
        x, y = -1, -1

        if bc.me.unit != SPECS['CASTLE']:
            return
        # In the first 3 turns
        if bc.turn > 4:
            return
        # Has it sended a first time? No:
        if not self.received_first_part:
            # If map is horizontally reflected:
            if bc.map_process.horizontal_reflection:
                # send first x
                x = self.receive_castle_talk(bc)
            #  If map is vertically reflected :
            else:
                # send first y
                y = self.receive_castle_talk(bc)
            #   save a flag for first sent
            self.received_first_part = True

        # Yes:when called again
        else:
            # If map is horizontally reflected:
            if bc.map_process.horizontal_reflection:
                # send first y
                y = self.receive_castle_talk(bc)
            #  If map is vertically reflected :
            else:
                x = self.receive_castle_talk(bc)
        return

    def _reset_lists(self):
        """ resets all lists for each turn """
        pass  # TODO

    def log_lists(self, bc):
        # bc.log('my_castles: {}'.format(len(self.my_castles)))
        # bc.log('my_military: {}'.format(len(self.my_military)))
        pass  # TODO

#

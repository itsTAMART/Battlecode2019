#
from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
from bots.first_bot.utils import *


class Communications(object):
    """
    manages communications between robots


        Locations sent in signals as CODE[4bits]+X[6bits]+Y[6bits]


    """
    # First turn Flags
    sent_first_part = False
    received_first_part = False
    first_turn_coords = {}
    castle_coords = []

    def __init__(self, bc):
        self.my_team = team(bc.me)

    def turn(self, bc):
        signaling = []
        for r in bc.vision_list:
            if bc.is_signaling(r):
                signaling.append(r)
        return signaling





        pass  # TODO

    def send_loc(self, bc, loc, radius):
        pass  # TODO

    def receive_loc(self, bc, robot=None, message=None):
        if robot is not None:
            pass
        if message is not None:
            pass  # TODO

    def send_castle_talk(self, bc, message):
        bc.castle_talk(int(message) % 256)

    def receive_castle_talk(self, robot):
        """
        recieve the castle talk and the id
        :param robot: robot object recieved from the vision list
        :return: the castle talk AND  the robot id
        """
        return robot.castle_talk, robot.id

    def send_initial_castle_location(self, bc):
        """ sends initial castle location in 2 steps"""

        # If im a castle
        # In the first 3 turns
        # Has it sended a first time? No:
        # If map is horizontally reflected:
        # send first x
        #  If map is vertically reflected :
        # send first y
        #   save a flag for first sent
        # Yes:when called again
        # If map is horizontally reflected:
        # send first y
        #  If map is vertically reflected :
        # send first x
        if bc.me.unit != SPECS['CASTLE']:
            return
        if bc.step > 3:
            return
        if not self.sent_first_part:
            bc.log('sending first part')
            if bc.map_process.horizontal_reflection:
                self.send_castle_talk(bc, bc.me.x)
            else:
                self.send_castle_talk(bc, bc.me.y)
            self.sent_first_part = True

        else:
            bc.log('sending second part')
            if bc.map_process.horizontal_reflection:
                self.send_castle_talk(bc, bc.me.y)
            else:
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

        signaling = [robot for robot in bc.get_visible_robots() if (not bc.is_visible(robot))]

        if bc.me.unit != SPECS['CASTLE']:
            # bc.log('not a castle')
            return
        # In the first 3 turns
        if bc.step > 4:
            # bc.log('not first turns')
            return

        for robot in signaling:
            # if robot.unit is not None:
            #     bc.log('not the castle we lookin for')
            #     bc.log(robot)
            #     continue

            # bc.log('for this robot:')
            # bc.log(robot)
            #
            # bc.log('first turn coords: {}'.format(self.first_turn_coords))

            coord, id = self.receive_castle_talk(robot)
            if coord == 0:
                # bc.log('not valid coord_1')
                continue

            if id not in self.first_turn_coords:
                bc.log('receiving first part')
                bc.log('coord_1: {}'.format(coord))
                self.first_turn_coords[id] = coord

            # Yes:when called again
            else:
                bc.log('receiving second part')
                # If map is horizontally reflected:
                if bc.map_process.horizontal_reflection:
                    bc.log('horizontal map')
                    castle_cord = (self.first_turn_coords[id], coord)
                    if not loc_in_list(castle_cord, self.castle_coords):
                        self.castle_coords.append(castle_cord)
                #  If map is vertically reflected :
                else:
                    bc.log('vertical map')
                    castle_cord = (coord, self.first_turn_coords[id])
                    if not loc_in_list(castle_cord, self.castle_coords):
                        self.castle_coords.append(castle_cord)

                # bc.log('first turn coords: {}'.format(self.first_turn_coords))
                bc.log('recieved coords: {}'.format(castle_cord))

            return


    def _reset_lists(self):
        """ resets all lists for each turn """
        pass  # TODO

    def log_lists(self, bc):
        # bc.log('my_castles: {}'.format(len(self.my_castles)))
        # bc.log('my_military: {}'.format(len(self.my_military)))
        pass  # TODO

#

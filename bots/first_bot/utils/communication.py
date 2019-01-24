#
from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
from bots.first_bot.utils import *


class Communications(object):
    """
    manages communications between robots


        Locations sent in signals as CODE[4bits]+X[6bits]+Y[6bits]


    """
    # Variables to store signaling robots
    signaling = []

    # First turn Flags
    sent_first_part = False
    received_first_part = False
    first_turn_coords = {}
    castle_coords = []

    def __init__(self, bc):
        self.my_team = team(bc.me)

    def turn(self, bc):
        """ retrieves robots signaling that turn """
        self._reset_lists()
        for r in bc.vision_list:
            if bc.is_radioing(r):
                self.signaling.append(r)

    def send_loc(self, bc, loc, sq_radius, code=0):
        """
        sets the emitting signal to the message
        :param bc: battlecode object
        :param loc: tuple (x, y)
        :param sq_radius: squared radius of the emission
        :param code: int only can use 4 bits
        :return:
        """
        x, y = loc
        full_loc = (x * 64) + y
        message = (code * 4096) + full_loc
        # Debug
        bc.log('sending [{}] at {} radius'.format(message, sq_radius))
        bc.signal(message, sq_radius)


    def receive_loc(self, bc, robot=None, message=None):
        """
         Locations sent in signals as CODE[4bits]+X[6bits]+Y[6bits]

         returns code, location
         """
        # bc.log('robot {}, message {}'.format(robot, message))
        if robot is not None:
            message = robot.signal
        if message is None:
            bc.log('error in receive_loc: no message or null robot')
            return None, None
        # extract location
        full_loc = message % 4096  # the last 12 bits
        # extract code
        code = (message - full_loc) / 4096  # The first 4 bits
        # separate location
        # y the last 6 bits
        y = full_loc % 64
        # x the first 6 bits
        x = (full_loc - y) / 64
        location = (x, y)

        # Debug
        bc.log('received code for: {} at [{}] '.format(C2T[code], location))
        return code, location


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

    def issue_church(self, bc, church_loc):
        """ notify the castles you will build a church in church_loc """
        # TODO implement it
        pass

    def churches_being_built(self, bc):
        """ check if there is going to be any church built soon """
        # TODO implement it
        # Check if any pilgrim is going to build a church
        # Plan for it with the build order
        # Recalculate mines of this castle taking into account the church
        pass

    def _reset_lists(self):
        """ resets all lists for each turn """
        self.signaling = []


    def log_lists(self, bc):
        bc.log('signaling: \n {}'.format(self.signaling))
        # bc.log('my_castles: {}'.format(len(self.my_castles)))
        # bc.log('my_military: {}'.format(len(self.my_military)))
        pass

#

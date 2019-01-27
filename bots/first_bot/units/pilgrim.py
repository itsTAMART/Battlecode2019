#
from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import random

from ..utils import *


def first_turn_pilgrim(self):
    # # Debug
    # self.log(self.comms.signaling)

    location = (self.me.x, self.me.y)
    # Find your closest mine
    my_mine = None
    my_mine = receive_mine(self)
    self.log('My mine in: {}'.format(my_mine))

    #  set the objective to the mine

    self.nav.set_destination(my_mine)
    self.destination = my_mine
    if not is_a_mine(self, self.destination):
        self.scouting = True
    self.spawn_loc = location
    return


def pilgrim(self):
    """ PILGRIM: scouts, mines and goes to church on sundays"""

    """

    CHURCH BUILDING

    """
    # TODO test

    # Second part of sending church_loc
    if self.comms.sent_first_church:
        self.log('sending second part of the church_loc')
        self.comms.issue_church(self, self.church_spot)

    if pending_church(self) and self.step > 3:  # Lets not interfere with castles talking
        self.log('thinking about erecting a church')
        # Not nearby castle's
        if man_distance(self.spawn_loc, self.destination) > 6:
            self.log('  location far enough')
            if is_a_mine(self, self.destination):
                self.log('  getting good churchsport')
                self.church_spot = self.map_process.get_church_spot(self, self.destination)
                self.log('  Good Church Spot in {}'.format(self.church_spot))
                # self.comms.issue_church(self, self.church_spot)
            else:
                # My destination is not a church
                self.log('  My destination is not a church')
                self.church_spot = (-1, -1)
        else:
            # My destination is close to a castle
            self.log('  My destination is too close to a castle')
            self.church_spot = (-1, -1)

    """

    FULL OF KARB: deposit code

    """
    # TODO implement
    # If not enough material to build.
    #   Start mining other resource
    #   If already full
    #       give to a military unit

    # FULL OF KARBONITE
    if full_of_karb(self) or full_of_fuel(self):
        # self.destination = self.spawn_loc # Destination represents your mine

        # if im_at(self, self.spawn_loc):
        #     # AT SPAWN
        for castle in self.combat.get_deposit(self):
            self.log('  - castle')
            if can_give(self, castle):
                # GIVE the material
                self.log('Direction to give {}'.format(direction_to(locate(self.me), castle)))
                self.log('Karb and fuel given {}, {}'.format(self.me.karbonite, self.me.fuel))
                self.nav.set_destination(self.destination)  # GO BACK TO THE MINE
                return self.give(*direction_to(locate(self.me), castle),
                                 self.me.karbonite, self.me.fuel)

        deposits = self.combat.get_deposit(self)
        self.log('deposits: {}'.format(deposits))
        my_depo = closest(self, locate(self.me), deposits)
        self.log('my depo: {}'.format(my_depo))

        self.nav.set_destination(my_depo)


    """
    PART 2 of CHURCH BUILDING
    
    """

    if want_to_build_church(self):
        self.log('I want to build a church')
        if ready_to_church(self):
            self.log('  almost ready to build a church')
            # Ask for the church
            self.log('  notifying it')
            self.comms.issue_church(self, self.church_spot)
            # When in place
            if is_adjacent(locate(self.me), self.church_spot):
                self.log('  in place to build a church')
                # TODO if no churches nearby else darla como construilda
                if not self.combat.are_there_closeby_churches(self):
                    #   Build Church
                    if can_build(self, "CHURCH", *self.church_spot):
                        self.log('  building a church')
                        spot = self.church_spot
                        self.church_spot = (-1, -1)  # You are done building churches
                        self.nav.set_destination(self.destination)  # GO BACK TO THE MINE
                        return self.build_unit(SPECS["CHURCH"], *direction_to(locate(self.me), spot))
                else:  # Church nearby
                    self.log('church nearby')
                    self.church_spot = (-1, -1)  # You are done building churches
                    self.nav.set_destination(self.destination)  # GO BACK TO THE MINE
                    self.comms.hello_church(self)

            else:  # Not adjacent
                self.log('  going there')
                # Go towards the church site
                self.log('  church spot: {}'.format(self.church_spot))
                adj = closest_passable(self, locate(self.me), adjacent_tiles(self, *self.church_spot))
                self.nav.set_destination(adj)
                # self.log('  destination: {}'.format(self.nav.destination))
                # closest_passable(self, locate(self.me), adjacent_tiles(self, *self.church_spot)))




    """

    SCOUTING and combat

    """
    # TODO test
    # If close to my mine
    if distance(locate(self.me), self.destination) < 5:
        self.log('  at destination ')

        # If it is occuppied
        if is_a_mine(self, self.destination):
            if is_occupied(self, *self.destination):
                self.log('  my mine is occupied')
                self.stuck += 1
                if self.stuck > 3:  # for more than 3 turns
                    self.stuck = 0
                    # FIND AND GO FOR NEXT MINE
                    self.log('Rushing next mine')
                    self.destination = self.map_process.find_next_mine_to_attack(self, self.destination)
                    self.nav.set_destination(self.destination)

        # # Too much, leave this
        # if self.combat.heavily_outgunned(self):
        #     # FIND AND GO FOR NEXT MINE
        #     self.log('Rushing next mine')
        #     self.destination = self.map_process.find_next_mine_to_attack(self, self.destination)
        #     self.nav.set_destination(self.destination)
        #     self.on_ring = False
        #

        if (not self.combat.are_enemies_near(self)) and self.scouting:
            # if no enemies here
            self.log('  no-one here, NOTIFYING')
            # Notify to castle
            self.comms.notify_target_done(self, self.destination)

            if (self.church_spot[0] == self.church_spot[1] == -1):
                # BUILDING A CHURCH FOR VICTORY
                self.log('  getting good churchsport')
                self.church_spot = self.map_process.get_church_spot(self, self.destination)
                self.log('  Good Church Spot in {}'.format(self.church_spot))
                self.comms.issue_church(self, self.church_spot)

            # FIND AND GO FOR NEXT MINE
            self.log('Rushing next mine')
            self.destination = self.map_process.find_next_mine_to_attack(self, self.destination)
            # self.nav.set_destination(self.destination)
            self.on_ring = False


    # if Im not on attack range
    #   Keep doing ma thing, check next on trajectory not in range
    # if im on attack range
    #   move away
    if len(self.combat.i_am_attackable) > 0:
        self.log('Combat Movement')
        combat_tile = self.combat.best_spot_to_move(self)
        moving_dir = difference_to(locate(self.me), combat_tile)
        self.log('moving dir: {}'.format(moving_dir))
        if can_move(self, *combat_tile):
            return self.move(*moving_dir)


    # TODO do it
    # If you see enemy unit
    # Report to castletalk
    # check if my military to help me
    #   signal it to them

    """

    MOVING code and MINING

    """
    # TODO test if it mines with the new navigation
    moving_dir = self.nav.next_tile(self)
    self.log('moving dir: {}'.format(moving_dir))  # Move to closest non-occupied mine
    if moving_dir[0] == moving_dir[1] == 0:  # moving_dir == (0,0)
        if can_mine(self, self.me.x, self.me.y):  # MINING
            # self.destination = None
            self.log('mining')  # Mine if you can
            return self.mine()
        else:
            self.log('couldnt move, couldnt mine')
    else:
        # self.log('  destination: {}'.format(self.nav.destination))
        # self.log('  trajectory: {}'.format(self.nav.trajectory))
        return self.move(*moving_dir)










def receive_mine(bc):
    # find the castle siganl and receive it
    for robot in bc.comms.signaling:
        if robot.unit == SPECS['CASTLE'] or robot.unit == SPECS['CHURCH']:
            # bc.log('robot {}, message {}'.format(robot, robot.signal))
            code, mine = bc.comms.receive_loc(bc, robot, robot.signal)
            bc.log('mine: {}, code: {}'.format(mine, code))
            if code == T2C['YOUR_MINE_IS']:
                # Debug
                bc.log('mine received correctly')
                if not is_a_mine(bc, mine):
                    bc.log('SCOUT pilgrim')
                    bc.church_spot = (-1, -1)  # Hacky way to avoid checking for church if you are scouting
                return mine
            else:
                bc.log('not appropriate code')
    else:
        bc.log('no castle found')
    bc.log('couldnt find mine')


# TODO test
def pending_church(bc):
    """ True if you still have to build a church """
    return bc.church_spot is None


# TODO test
def want_to_build_church(bc):
    """ True if you want to build a church """
    if bc.step < 4 or bc.church_spot is None:
        return False
    return not (bc.church_spot[0] == bc.church_spot[1] == -1)


def ready_to_church(bc):
    return bc.karbonite > 40 and bc.fuel > 180  # Hardcoded 90% of the cost of a church


def is_a_mine(bc, loc):
    return loc_in_list(loc, bc.map_process.karb_mines) or loc_in_list(loc, bc.map_process.fuel_mines)


#

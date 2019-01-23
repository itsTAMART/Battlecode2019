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
    self.spawn_loc = location
    return


def pilgrim(self):
    """ PILGRIM: scouts, mines and goes to church on sundays"""

    """

    CHURCH BUILDING

    """
    # Not nearby castle's
    if self.church_spot is None:
        self.log('getting good churchsport')
        self.church_spot = self.map_process.get_church_spot(self, self.destination)
        self.log('Good Church Spot in {}'.format(self.church_spot))

    # TODO do it
    # When in place
    # If not enough material to build.
    #   Start mining other resource
    #   If already full
    #       give to a military unit
    # else:
    #   Build Church

    """
    
    FULL OF KARB: deposit code
    
    """


    # FULL OF KARBONITE
    if full_of_karb(self) or full_of_fuel(self):
        # self.destination = self.spawn_loc # Destination represents your mine
        self.nav.set_destination(self.spawn_loc)

        # if im_at(self, self.spawn_loc):
        #     # AT SPAWN
        for castle in self.combat.get_deposit():
            if can_give(self, castle):
                # GIVE the material
                self.log('Direction to give {}'.format(direction_to(locate(self.me), locate(castle))))
                self.log('Karb and fuel given {}, {}'.format(self.me.karbonite, self.me.fuel))
                self.nav.set_destination(self.destination)  # GO BACK TO THE MINE
                return self.give(*direction_to(locate(self.me), locate(castle)),
                                 self.me.karbonite, self.me.fuel)

    """

    SCOUTING and combat

    """
    # TODO do it
    # If you see enemy unit
    # Report to castletalk
    # if Im not on attack range
    #   Keep doing ma thing, check next on trajectory not in range
    # if im on attack range
    #   move away
    # check if my military to help me
    #   signal it to them

    """

    MOVING code and MINING

    """

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
                return mine
            else:
                bc.log('not appropriate code')
    else:
        bc.log('no castle found')
    bc.log('couldnt find mine')



#

#
from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import random

from ..utils import *


def first_turn_pilgrim(self):
    # TODO do tings like choosing which castle you represent with the map
    # Find your closest mine
    excluded_mines = []
    location = (self.me.x, self.me.y)
    my_mine = find_nearest(self, self.karbonite_map, location, excluded_mines)
    self.log('My mine in: {}'.format(my_mine))

    # Initialize Navigation and set the objective to the mine
    self.nav = Navigation(self, my_mine)
    self.destination = my_mine
    self.spawn_loc = location
    return


def pilgrim(self):
    unit_specs = SPECS['UNITS'][bc.me.unit]

    # FULL OF KARBONITE
    if self.me.karbonite == unit_specs['KARBONITE_CAPACITY']:
        # self.destination = self.spawn_loc # Destination represents your mine
        self.nav.set_destination(self.spawn_loc)

        if self.me.x == self.spawn.loc[0] and self.me.y == self.spawn.loc[1]:
            # AT SPAWN
            pass  # # TODO left here RECORRER VISIBLES Y GIVE SI ES UN CASTLE
        # if can_give(self):



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


    # # Mine till full, (temporarily) come back

    """
    
    EXAMPLEFUNKY CODE
    
    elif self.me['unit'] == SPECS['PILGRIM']:
    if self.destination is None:
        # find nearest karbonite
        self.destination = self.find_nearest(self.karbonite_map, (self.me['x'], self.me['y']))
        # self.log('I have a destination! ' + str(self.destination))
    if self.karbonite_map[self.me['y']][self.me['x']]:
        # on karbonite!
        if self.me.karbonite == SPECS['UNITS'][SPECS["PILGRIM"]]['KARBONITE_CAPACITY']:
            self.destination = self.spawnloc
        else:
            # self.log('MINING!')
            return self.mine()

    my_coord = (self.me['x'], self.me['y'])
    return self.move(*nav.goto(my_coord, self.destination, self.map, visible_robot_map, self.already_been))
    
    """




#

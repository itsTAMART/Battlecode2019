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
    self.nav = Navigation(my_mine)
    self.combat = CombatManager(self)
    self.destination = my_mine
    self.spawn_loc = location
    return


def pilgrim(self):
    """ Basic PILGRIM: mine then, come back to deposit"""
    # Run combat/give code
    # Run nav code
    # Run mining code

    self.combat.turn(self)

    # FULL OF KARBONITE
    if full_of_karb(self):
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







#

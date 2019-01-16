#
from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import random

from ..utils import *


def first_turn_prophet(self):
    # TODO do tings like choosing which castle you represent with the map
    self.nav = Navigation()
    self.combat = CombatManager(self)
    self.spawn_loc = locate(self.me)

    # TODO MASSIVE WORKAROUND, REMOVE AFTER SPRINT
    # TODO temporal add a random offset to spawnloc and use it as destination to move them around
    choices = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
    choice = random.choice(choices)
    self.destination = (self.spawn_loc[0] + choice[0], self.spawn_loc[1] + choice[1])

    # # TODO find first castle
    # self.destination = None
    return


def prophet(self):
    self.combat.turn(self)

    # ATTACK IF THERE IS A TARGET
    target = self.combat.lowest_health_enemy()
    self.log('target: {}'.format(target))
    if target is not None:
        if can_attack(self, *locate(target)):
            self.log('attack:')
            self.log(locate(self.me))
            self.log(locate(target))  # TODO testing

            return self.attack(*diference_to(locate(self.me), locate(target)))

    # AGGRESSIVE BEHAVIOUR
    aggression_target = self.combat.closest_visible_enemy(self)
    self.log('aggression target: {}'.format(aggression_target))
    if aggression_target is not None:  # Go for closest target
        self.nav.set_destination(locate(aggression_target))
        # TODO something to move aggresively inside navigation
    else:
        # Back again at pushing for the castle
        self.nav.set_destination(self.destination)

    # IF LOADED OF KARB GO TO SPAWN TO UNLOAD
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

    # MUVEMENTO
    moving_dir = self.nav.next_tile(self)
    self.log('moving dir: {}'.format(moving_dir))  # Move to closest non-occupied mine
    if moving_dir[0] == moving_dir[1] == 0:  # moving_dir == (0,0)
        if im_at(self, self.destination):  # Am I at my destination?
            self.log('no castle here, so next castle')
            # TODO go for next castle
            # TODO destination = next castle
            # TODO signal there is no longer a castle here

        else:
            self.log('stuck')
    else:
        return self.move(*moving_dir)

#

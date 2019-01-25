#
from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import random

from ..utils import *


def first_turn_preacher(self):
    # Find your closest target
    attack_loc = None
    attack_loc = self.comms.receive_target(self)
    self.log('My attack_loc in: {}'.format(attack_loc))

    #  set the objective to the mine

    self.nav.set_destination(attack_loc)
    self.destination = attack_loc

    self.spawn_loc = locate(self.me)


def preacher(self):
    """
     Ezekiel 25:17. "The path of the righteous man is beset on all sides by the
     inequities of the selfish and the tyranny of evil men. Blessed is he who, in
     the name of charity and good will, shepherds the weak through the valley of the
     darkness. For he is truly his brother's keeper and the finder of lost children.
     And I will strike down upon thee with great vengeance and furious anger those
     who attempt to poison and destroy my brothers. And you will know I am the Lord
     when I lay my vengeance upon you.
     """

    """
    ATTACKING BUSSINESS

    """

    # ATTACK IF THERE IS A TARGET
    # TODO change targeting to attack crusaders if they are together
    # else focus prophets , attack preachers
    # TODO if RUSH try to hit pilgrims, if you are not going to die from being hit

    target = self.combat.lowest_health_enemy()
    self.log('target: {}'.format(target))
    if target is not None:
        if can_attack(self, *locate(target)):
            self.log('attack:')
            self.log(locate(self.me))
            self.log(locate(target))  # TODO testing

            return self.attack(*difference_to(locate(self.me), locate(target)))

    """
    COMBAT MOVEMENT

    """

    # AGGRESSIVE BEHAVIOUR
    # TODO when to aggressive move
    # TODO when you hear a signal, move to just outside attacking range
    # TODO do not move inside castle range if you dont outpower it
    aggression_target = self.combat.closest_visible_enemy(self)
    self.log('aggression target: {}'.format(aggression_target))
    if aggression_target is not None:  # Go for closest target
        self.nav.set_destination(locate(aggression_target))
        # TODO something to move aggresively inside navigation
    else:
        # Back again at pushing for the castle
        self.nav.set_destination(self.destination)

    # IF LOADED OF KARB GO TO SPAWN TO UNLOAD
    # TODO restrict this
    if full_of_karb(self):
        # self.destination = self.spawn_loc # Destination represents your mine
        self.nav.set_destination(self.spawn_loc)
        # if im_at(self, self.spawn_loc):
        #     # AT SPAWN
        for castle in self.combat.get_deposit(self):
            if can_give(self, castle):
                # GIVE the material
                self.log('Direction to give {}'.format(direction_to(locate(self.me), locate(castle))))
                self.log('Karb and fuel given {}, {}'.format(self.me.karbonite, self.me.fuel))
                self.nav.set_destination(self.destination)  # GO BACK TO THE MINE
                return self.give(*direction_to(locate(self.me), locate(castle)),
                                 self.me.karbonite, self.me.fuel)

    """
    OFF-COMBAT MOVEMENT

    """

    # MUVEMENTO
    # TODO move where you want to go
    # TODO if rush, aggressive pathfind
    # TODO
    moving_dir = self.nav.next_tile(self)
    self.log('moving dir: {}'.format(moving_dir))  # Move to closest non-occupied mine
    if moving_dir[0] == moving_dir[1] == 0:  # moving_dir == (0,0)
        if im_at(self, self.destination):  # Am I at my destination?
            self.log('no castle here, so next castle')
        else:
            self.log('stuck')
    else:
        return self.move(*moving_dir)

#

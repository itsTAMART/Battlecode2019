#
from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import random

from ..utils import *


def first_turn_prophet(self):

    # Find your closest mine
    attack_loc = None
    attack_loc = self.comms.receive_target(self)
    self.log('My attack_loc in: {}'.format(attack_loc))

    #  set the objective to the mine

    self.nav.set_destination(attack_loc)
    self.destination = attack_loc

    self.spawn_loc = locate(self.me)



def prophet(self):
    """ The BORING PROPHET from the Life of Bryan """

    # TODO check if its going to be a FAKE RUSH

    """
    COMUNICATIONS
    
    """
    # Second part of sending church_loc
    if self.comms.sent_first_target:
        self.log('  sending second part of the target_loc')
        self.comms.notify_target_done(self, self.destination)

    """
    COMBAT MOVEMENT

    """
    # TODO if defensive behaviour, ARCHER LATTICE

    # AGGRESSIVE BEHAVIOUR
    # TODO when to aggressive move
    # TODO when you hear a signal, move to just outside attacking range
    # TODO do not move inside castle range if you dont outpower it
    if self.on_ring:

        if len(self.combat.i_am_attackable) > 0:
            self.log('Combat Deffensive Movement')
            combat_tile = self.combat.best_spot_to_move(self)
            moving_dir = difference_to(locate(self.me), combat_tile)
            self.log('moving dir: {}'.format(moving_dir))

            if moving_dir[0] == moving_dir[1] == 0:

                target = self.combat.lowest_health_enemy()
                self.log('target: {}'.format(target))
                if target is not None:
                    if can_attack(self, *locate(target)):
                        self.log('attack:')
                        self.log(locate(self.me))
                        self.log(locate(target))  # TODO testing

                        return self.attack(*difference_to(locate(self.me), locate(target)))

            if can_move(self, *combat_tile):
                return self.move(*moving_dir)

    else:
        # Normally attack
        target = self.combat.lowest_health_enemy()
        self.log('target: {}'.format(target))
        if target is not None:
            if can_attack(self, *locate(target)):
                self.log('attack:')
                self.log(locate(self.me))
                self.log(locate(target))  # TODO testing

                return self.attack(*difference_to(locate(self.me), locate(target)))

        aggression_target = self.combat.closest_visible_enemy(self)
        self.log('aggression target: {}'.format(aggression_target))
        if aggression_target is not None:  # Go for closest target
            self.nav.set_destination(locate(aggression_target))
            # TODO something to move aggresively inside navigation
        else:
            # Back again at pushing for the castle
            self.nav.set_destination(self.destination)

    """
    ATTACKING BUSSINESS

    """
    # ATTACK IF THERE IS A TARGET
    # TODO change targeting to attack crusaders if only prophets in allies
    # else focus preachers , attack prophets
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
    IF IM AT TARGET and NO enemies here: notify
    
    """
    # if Distance to target < 5
    if distance(locate(self.me), self.destination) < 5:
        self.log('  at destination ')

        # Too much, leave this
        if self.combat.heavily_outgunned(self):
            # FIND AND GO FOR NEXT MINE
            self.log('Rushing next mine')
            self.destination = self.map_process.find_next_mine_to_attack(self, self.destination)
            self.nav.set_destination(self.destination)
            self.on_ring = False

        if not self.combat.are_enemies_near(self):
            # if no enemies here
            self.log('  no-one here, NOTIFYING')
            # Notify to castle
            self.comms.notify_target_done(self, self.destination)

            # FIND AND GO FOR NEXT MINE
            self.log('Rushing next mine')
            self.destination = self.map_process.find_next_mine_to_attack(self, self.destination)
            self.nav.set_destination(self.destination)
            self.on_ring = False





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

    if man_distance(locate(self.me), self.destination) < 13 and not self.on_ring:
        new_objective = closest_passable(self, locate(self.me), ring(10, 11))
        self.log('going to ring')
        self.nav.set_destination(new_objective)
        self.on_ring = True


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

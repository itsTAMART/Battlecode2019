#
from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
from bots.first_bot.utils import *


class CombatManager(object):
    """
    manages combat action, movement and GIVING of resources
    """
    my_team = -1

    my_castles = []
    my_military = []
    my_civil = []
    my_signaling_units = []

    enemy_castles = []
    enemy_military = []
    enemy_civil = []
    enemy_signaling_units = []

    attackable = []
    attackable_by_allies = []
    i_am_attackable = []
    seen = []

    def __init__(self, bc):
        self.my_team = team(bc.me)

    # TODO test
    def turn(self, bc):
        """
        The loop which checks visible units and bins them into lists
        :param bc: battlecode_object
        """
        self._reset_lists()

        im_military = bc.me.unit == SPECS['CRUSADER'] \
                      or bc.me.unit == SPECS['PROPHET'] \
                      or bc.me.unit == SPECS['PREACHER']

        for r in bc.vision_list:  # For each robot visible
            # Check if is signaling and not in vision range
            if not bc.is_visible(r):
                # TODO by now it only appends the signaling units, doesn't count them to units
                # this robot isn't actually in our vision range,
                # it just turned up because we heard its radio broadcast.
                if r.team == self.my_team:
                    self.my_signaling_units.append(r)
                else:
                    self.enemy_signaling_units.append(r)

                bc.log('Signaling unit: {}'.format(TYPES[r.unit]))
                bc.log(r)

                continue

            # Check if it is your team
            if r.team == self.my_team:  # MY TEAM
                # bc.log('Ally unit:')
                # bc.log(r)
                # Castle, Civil or Military ?
                if r.unit == SPECS['CASTLE'] or r.unit == SPECS['CHURCH']:
                    self.my_castles.append(r)
                    continue
                if r.unit == SPECS['PILGRIM']:
                    self.my_civil.append(r)
                    continue
                if r.unit == SPECS['CRUSADER'] \
                        or r.unit == SPECS['PROPHET'] \
                        or r.unit == SPECS['PREACHER']:
                    self.my_military.append(r)
                    continue

            # Check if is other team
            else:  # ENEMY TEAM
                # Castle, Civil or Military ?
                if r.unit == SPECS['CASTLE'] or r.unit == SPECS['CHURCH']:
                    self.enemy_castles.append(r)
                if r.unit == SPECS['PILGRIM']:
                    self.enemy_civil.append(r)
                if r.unit == SPECS['CRUSADER'] \
                        or r.unit == SPECS['PROPHET'] \
                        or r.unit == SPECS['PREACHER']:
                    self.enemy_military.append(r)

                    # Am I attackable by it?
                    if am_i_attackable(bc, r):
                        self.i_am_attackable.append(r)

                if im_military:
                    # Is attackable by me?
                    if is_attackable(bc, r):
                        self.attackable.append(r)

                bc.log('Enemy unit: {}'.format(TYPES[r.unit]))

        # END FOR

        # TODO test
        # Is attackable by allied military?
        if im_military:
            for enemy in self.attackable:
                for ally in self.my_military:
                    if is_attackable_unit(ally, enemy):
                        self.attackable_by_allies.append(enemy)
                        break

    # TODO list of methods
    # lowest health enemy
    # Give (target)

    def _reset_lists(self):
        """ resets all lists for each turn """
        self.my_castles = []
        self.my_military = []
        self.my_civil = []
        self.my_signaling_units = []
        self.enemy_castles = []
        self.enemy_military = []
        self.enemy_civil = []
        self.enemy_signaling_units = []
        self.attackable = []
        self.attackable_by_allies = []
        self.i_am_attackable = []

#

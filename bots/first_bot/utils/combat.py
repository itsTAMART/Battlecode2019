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


    def turn(self, bc):
        """
        The loop which checks visible units and bins them into lists
        :param bc: battlecode_object
        """
        self._reset_lists()

        im_military = bc.me.unit == SPECS['CRUSADER'] \
                      or bc.me.unit == SPECS['PROPHET'] \
                      or bc.me.unit == SPECS['PREACHER'] \
                      or bc.me.unit == SPECS['CASTLE']

        for r in bc.vision_list:  # For each robot visible
            # Check if is signaling and not in vision range
            if not bc.is_visible(r):
                # this robot isn't actually in our vision range,
                # it just turned up because we heard its radio broadcast.
                if r.team == self.my_team:
                    self.my_signaling_units.append(r)
                else:
                    self.enemy_signaling_units.append(r)
                    bc.log('Enemy signaling unit at: {}'.format((r.x, r.y)))
                # bc.log(r)
                continue

            # Check if it is your team
            if r.team == self.my_team:  # MY TEAM
                # bc.log('Ally unit:')
                # bc.log(r)
                # Castle, Civil or Military ?
                if r.unit == SPECS['CASTLE'] or r.unit == SPECS['CHURCH']:
                    if not loc_in_list(locate(r), bc.map_process.my_castles):
                        bc.map_process.my_castles.append(locate(r))
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
                    if not loc_in_list(locate(r), bc.map_process.enemy_castles):
                        bc.map_process.enemy_castles.append(locate(r))
                    self.enemy_castles.append(r)
                if r.unit == SPECS['PILGRIM']:
                    self.enemy_civil.append(r)
                if r.unit == SPECS['CRUSADER'] \
                        or r.unit == SPECS['PROPHET'] \
                        or r.unit == SPECS['PREACHER'] \
                        or r.unit == SPECS['CASTLE']:
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

        # Is attackable by allied military?
        if im_military:
            for enemy in self.attackable:
                for ally in self.my_military:
                    if is_attackable_unit(ally, enemy):
                        self.attackable_by_allies.append(enemy)
                        break

        # # Debug
        # self.log_lists(bc)

    # # Yay, coding for things that cannot be done
    # def lowest_health_enemy(self):
    #     min_health = 10000
    #     enemy = None
    #     for r in self.attackable:
    #         if r.health < min_health:
    #             min_health = r.health
    #             enemy = r
    #     return enemy

    def lowest_health_enemy(self):
        min_health = 10000
        enemy = None
        unit_specs = SPECS['UNITS']
        for r in self.attackable:
            hp = unit_specs[r.unit]['STARTING_HP']
            if hp < min_health:
                min_health = hp
                enemy = r
        return enemy

    def closest_visible_enemy(self, bc):
        enemies_lists = [self.enemy_castles, self.enemy_military, self.enemy_civil]
        min_dist = 10000
        enemy = None
        for lista in enemies_lists:
            for r in lista:
                # bc.log(r)
                dist = distance(locate(bc.me), locate(r))
                if dist < min_dist:
                    min_dist = dist
                    enemy = r
        return enemy

    # TODO test
    def best_spot_to_move(self, bc):
        bc.log('Choosing best tile for combat')
        if self.favorable_fight(bc):
            return (0, 0)

        candidates = {}
        max_points = -9999
        chosen_spot = None
        tiles = passable_movement_tiles(bc, *locate(bc.me))

        for spot in tiles:
            candidates[spot] = 0

        for robot in self.enemy_military:
            for spot in tiles:
                if can_be_attacked(spot, robot):
                    candidates[spot] -= 1

        bc.log('Good Movements {}'.format(candidates))
        # May break
        for spot in candidates.keys():
            points = candidates[spot]
            if points > max_points:
                max_points = points
                chosen_spot = spot

        return tuple([int(x) for x in chosen_spot.split(',')])  # FUCK JAVASCRIPT AND YOUR TRANSPILER, REALLY


    # TODO test
    # do we outgun castle?
    def can_we_outgun_castle(self, bc):

        return (len(self.my_military) - len(self.enemy_military) > 3)

    def favorable_fight(self, bc):

        return (len(self.my_military) - len(self.enemy_military) > 1)


    # TODO new targeting to oneshot castle if possible
    # TODO target civil units
    # TODO the 3 different targetings needed
    # TODO check if i have been attacked and if im going to lose the combat then retreat



    # TODO test
    def are_there_closeby_churches(self, bc):
        bc.log('        my_castles: {}'.format(bc.map_process.my_castles))
        for church in bc.map_process.my_castles:
            if man_distance(locate(bc.me), church) < 7:
                return True
        return False

    def get_deposit(self, bc):
        bc.log('        my_deposits: {}'.format(bc.map_process.my_castles))
        return bc.map_process.my_castles

    def are_enemies_near(self, bc):
        """ True if yes """
        return (len(self.enemy_castles) > 0) or (len(self.enemy_civil) > 0) or (len(self.enemy_military) > 0)

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

    def log_lists(self, bc):
        bc.log('my_castles: {}'.format(len(self.my_castles)))
        bc.log('my_military: {}'.format(len(self.my_military)))
        bc.log('my_civil: {}'.format(len(self.my_civil)))
        bc.log('my_signaling_units: {}'.format(len(self.my_signaling_units)))
        bc.log('enemy_castles: {}'.format(len(self.enemy_castles)))
        bc.log('enemy_military: {}'.format(len(self.enemy_military)))
        bc.log('enemy_civil: {}'.format(len(self.enemy_civil)))
        bc.log('enemy_signaling_units: {}'.format(len(self.enemy_signaling_units)))
        bc.log('attackable: {}'.format(len(self.attackable)))
        bc.log('attackable_by_allies: {}'.format(len(self.attackable_by_allies)))
        bc.log('i_am_attackable: {}'.format(len(self.i_am_attackable)))


#

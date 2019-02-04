from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import random
import math


#
# from battlecode import BCAbstractRobot, SPECS
# import battlecode as bc
# import random

# from bots.first_bot.utils import *


def find_nearest(self, mapa, location, excluding=[]):
    """
    Method used to find the next mine, for example
    :param self: battlecode object
    :param mapa: map the format bc uses it map[y][x]
    :param location: (tuple) the position in a tuple (x, y)
    :param excluding: list including all mines that are busy
    :return: (tuple) closest location (x, y)
    """
    visited = []
    q = []
    i_q = 0
    current = location
    while not mapa[current[1]][current[0]]:
        visited.append(current)
        for x, y in passable_adjacent_tiles(self, current[0], current[1]):
            newc = (x, y)
            if not loc_in_list(newc, visited):
                # Not visited
                if not loc_in_list(newc, excluding):
                    # not from the excluded ones
                    q.append(newc)
        current = q[i_q]  # Equivalent to pop
        i_q += 1
    return current


def takeFirst(elem):
    return 9000 + int(elem[0])  # Hack because transpiler is sorting it as a string


# def find_all(self, mapa, location):
#     """
#     Method used to find the all mines, for example
#     :param self: battlecode object
#     :param mapa: map the format bc uses it map[y][x]
#     :param location: (tuple) the position in a tuple (x, y)
#     :return: (tuple) closest location (x, y)
#     """
#     target = []
#     visited = []
#     q = []
#     i_q = 0
#     current = location
#     q.append(current)
#     while i_q < len(q):
#         visited.append(current)
#         if mapa[current[1]][current[0]]:
#             # Found one
#             target.append(current)
#         for x, y in passable_adjacent_tiles(self, current[0], current[1]):
#             newc = (x, y)
#             if not loc_in_list(newc, visited):
#                 # Not visited
#                 q.append(newc)
#
#         current = q[i_q]  # Equivalent to pop
#         i_q += 1
#     return target


class MapPreprocess(object):
    """
    extract the features of the type of game and aids with the targeting
    """
    # MAP FEATURES
    map_size = -1
    passable_tiles = 0
    passable_pct = -1
    horizontal_reflection = True
    n_castles = 1
    my_castle_ids = []
    my_castles = []
    my_churches = []
    enemy_castles = []
    karb_mines = []
    fuel_mines = []
    conectedness = []

    # Counters
    mine_index = 0
    index_karb_mine = 0
    index_fuel_mine = 0
    k_distances = []
    f_distances = []
    mine_distances = []

    def get_initial_game_info(self, bc):

        self.map_size = len(bc.passable_map[0])
        self.find_all_mines(bc)
        self.horizontal_reflection = self.is_horizontal_reflect()
        self.sorted_mines_by_distance(bc)
        self.get_n_castles(bc)

    def get_initial_game_info_2(self, bc):
        self.get_my_castles(bc)
        self.reflect_enemy_castles(bc)
        self.filter_mines_by_distance(bc)

    def find_all_mines(self, bc):
        passable_tiles = 0
        karbonite_mines = []
        fuel_mines = []

        for y in range(self.map_size):
            for x in range(self.map_size):
                if bc.passable_map[y][x]:
                    self.passable_tiles += 1
                if bc.karbonite_map[y][x]:
                    self.karb_mines.append((x, y))
                if bc.fuel_map[y][x]:
                    self.fuel_mines.append((x, y))
        self.passable_pct = self.passable_tiles / (self.map_size ** 2)

    def is_horizontal_reflect(self):
        """
        check if the map is horizontally reflected,
        call after the find mines
        True if Horizontal, False if vertical
        """
        if len(self.karb_mines) > 0:
            x, y = self.karb_mines[0]
            horiz_reflected_loc = (self.map_size - x, y)
            return loc_in_list(horiz_reflected_loc, self.karb_mines)
        elif len(self.fuel_mines) > 0:
            x, y = self.fuel_mines[0]
            horiz_reflected_loc = (self.map_size - x, y)
            return loc_in_list(horiz_reflected_loc, self.fuel_mines)
        else:
            return True

    def get_n_castles(self, bc):
        """ gets the number of castles, not the coords"""
        visible = bc.get_visible_robots()
        if bc.me.unit == SPECS['CASTLE']:
            self.n_castles = len(visible)
        for unit in visible:
            self.my_castle_ids.append(unit.id)

    def get_my_castles(self, bc):
        """ (ONLY CALLABLE BY A CASTLE)
            (ONLY CALLABLE FROM TURN 3 ON)
            get the locations of your own castles
        """
        self.my_castles = bc.comms.castle_coords
        self.my_castles.append(locate(bc.me))

    def reflect_enemy_castles(self, bc):
        """ call after horizontal reflection is known, and castles known"""
        for castle in self.my_castles:
            self.enemy_castles.append(reflect(bc, castle, self.horizontal_reflection))

    def sorted_mines_by_distance(self, bc):
        """ sort the minse list by distance"""
        my_loc = locate(bc.me)
        self.k_distances = [(man_distance(my_loc, mine), mine) for mine in self.karb_mines]
        self.k_distances = sort_tuples(self.k_distances, bc)
        self.karb_mines = [mine for _, mine in self.k_distances]

        self.f_distances = [(man_distance(my_loc, mine), mine) for mine in self.fuel_mines]
        self.f_distances = sort_tuples(self.f_distances, bc)
        self.fuel_mines = [mine for _, mine in self.f_distances]

    def filter_mines_by_distance(self, bc):
        """ assign each mine to a castle by distance """
        bc.log('filter mines by distance')
        bc.log('before')
        bc.log('karb_mines: {}'.format(len(self.karb_mines)))
        # bc.log('karb_mines: {}'.format(self.karb_mines))
        bc.log('fuel_mines: {}'.format(len(self.fuel_mines)))
        my_loc = locate(bc.me)
        # Remove my loc from castle locs
        my_castles = [castle for castle in self.my_castles if castle != my_loc]

        k_mines = []
        f_mines = []
        # filter distances if d other castles < my dist
        for castle in my_castles:
            for d, mine in self.k_distances:
                if man_distance(castle, mine) < int(d):
                    k_mines.append(mine)
            for d, mine in self.f_distances:
                if man_distance(castle, mine) < int(d):
                    f_mines.append(mine)

        self.karb_mines = [mine for mine in self.karb_mines if (mine not in k_mines)]
        self.fuel_mines = [mine for mine in self.fuel_mines if (mine not in f_mines)]
        # # Fix the lists
        # self.sorted_mines_by_distance(bc)

        bc.log('after')
        bc.log('karb_mines: {}'.format(len(self.karb_mines)))
        # bc.log('karb_mines: {}'.format(self.karb_mines))
        bc.log('fuel_mines: {}'.format(len(self.fuel_mines)))

    def filter_mines_by_church(self, bc, church_loc):
        """ remove the mines belonging to a church """
        bc.log('filter mines by church')
        bc.log('before')
        bc.log('karb_mines: {}'.format(len(self.karb_mines)))
        bc.log('fuel_mines: {}'.format(len(self.fuel_mines)))

        k_mines = []
        f_mines = []

        # filter distances if d to church is < 7
        for mine in self.karb_mines:
            if distance(church_loc, mine) > 36:
                k_mines.append(mine)
        for mine in self.fuel_mines:
            if distance(church_loc, mine) > 36:
                f_mines.append(mine)
        self.karb_mines = k_mines
        self.fuel_mines = f_mines
        # Fix the lists
        self.sorted_mines_by_distance(bc)
        bc.log('after')
        bc.log('karb_mines: {}'.format(len(self.karb_mines)))
        bc.log('fuel_mines: {}'.format(len(self.fuel_mines)))

    def filter_mines_for_church(self, bc):
        """ keep the mines belonging to a church """
        bc.log('filter_mines_for_church')
        bc.log('before')
        bc.log('karb_mines: {}'.format(len(self.karb_mines)))
        # bc.log('karb_mines: {}'.format(self.karb_mines))
        bc.log('fuel_mines: {}'.format(len(self.fuel_mines)))
        # filter distances if d to church is < 7
        k_mines = []
        f_mines = []
        for mine in self.karb_mines:
            if (int(distance(locate(bc.me), mine)) < 6 ** 2):
                k_mines.append(mine)
        for mine in self.fuel_mines:
            if (int(distance(locate(bc.me), mine)) < 6 ** 2):
                f_mines.append(mine)
        self.karb_mines = k_mines
        self.fuel_mines = f_mines
        # Fix the lists
        self.sorted_mines_by_distance(bc)
        bc.log('after')
        bc.log('karb_mines: {}'.format(len(self.karb_mines)))
        bc.log('karb_mines: {}'.format(self.karb_mines))
        bc.log('fuel_mines: {}'.format(len(self.fuel_mines)))

    def next_mine(self, bc):
        """ Chooses the next mine to send the pilgrim
        If RUSH choose first 2 fuel then karb
        If ECON go for first 2 karb then fuel
        """
        mine_type = ''
        mine = None
        # index = self.mine_index % ((len(self.karb_mines) + len(self.fuel_mines)))
        #
        # # # Only build for the mines of that church or castle
        # # if self.mine_index >= (len(self.karb_mines) + len(self.fuel_mines)):
        # #     return mine
        #
        # # CHOOSE
        # if self.mine_index % 2 == 0:  # Here we go for karb or fuel
        #     mine_type = 'k'
        # else:
        #     mine_type = 'f'
        #
        # # For the first 3 mines
        # if self.mine_index < 4:
        #     if bc.tactics.RUSH:
        #         bc.log('rush custom mine')
        #         rush_build = ['s', 'f', 'f']
        #         mine_type = rush_build[self.mine_index]
        #
        #     if bc.tactics.ECON:
        #         bc.log('econ custom mine')
        #         econ_build = ['k', 'k', 'f']
        #         mine_type = econ_build[self.mine_index]
        #
        # # BUILD
        # if mine_type == 'k':  # Here we go for karb
        #     mine = self.next_karb_mine(bc)
        #     if mine is None:
        #         mine = self.next_fuel_mine(bc)
        # elif mine_type == 'f':  # Here we go fuel
        #     mine = self.next_fuel_mine(bc)
        #     if mine is None:
        #         mine = self.next_karb_mine(bc)
        # else:
        #     mine = None
        #     self.mine_index -= 1
        #

        if self.mine_index >= (len(self.karb_mines) + len(self.fuel_mines)):
            return None

        self.sorted_mines_by_distance(bc)

        mines = self.k_distances

        for a in self.f_distances:
            mines.append(a)

            mines = sorted_tuples(mines)

        d, mine = mines[self.mine_index]

        self.mine_index += 1
        return mine

    def next_karb_mine(self, bc):
        if self.index_karb_mine >= len(self.karb_mines):
            bc.log(' no karb mines left for this castle ')
            mine = None
            return mine
        mine = self.karb_mines[self.index_karb_mine]
        bc.log('karb mine is {} with k_index {}'.format(mine, self.index_karb_mine))
        self.index_karb_mine = (self.index_karb_mine + 1)
        return mine

    def next_fuel_mine(self, bc):
        if self.index_fuel_mine >= len(self.fuel_mines):
            bc.log(' no fuel mines left for this castle ')
            mine = None
            return mine
        mine = self.fuel_mines[self.index_fuel_mine]
        bc.log('fuel mine is {} with f_index {}'.format(mine, self.index_fuel_mine))
        self.index_fuel_mine = (self.index_fuel_mine + 1)
        return mine

    def closest_enemy_castle(self, bc):
        """ only for castles """
        bc.log('closest enemy castle')
        min_dist = 99999
        closest_castle = None
        loc = locate(bc.me)

        for castle in self.enemy_castles:
            bc.log('castle: {}'.format(castle))
            dist = distance(loc, castle)
            bc.log('dist: {}'.format(dist))
            if int(dist) < int(min_dist):
                min_dist = dist
                closest_castle = castle
        return closest_castle

    # TODO test
    def closest_e_castle_for_units(self, bc):
        """ closest enemy castle for a unit """
        bc.log('closest enemy castle')
        min_dist = 99999
        closest_castle = None
        loc = locate(bc.me)

        castle_locs = [locate(r) for r in bc.combat.my_castles if r.unit == SPECS["CASTLE"]]

        # Seen enemy castles
        for castle in bc.combat.enemy_castles:
            bc.log('castle: {}'.format(locate(castle)))
            dist = distance(loc, locate(castle))
            bc.log('dist: {}'.format(dist))
            if int(dist) < int(min_dist):
                min_dist = dist
                closest_castle = locate(castle)

        # For previously known enemy castles
        for castle in self.enemy_castles:
            bc.log('castle: {}'.format(castle))
            dist = distance(loc, castle)
            bc.log('dist: {}'.format(dist))
            if int(dist) < int(min_dist):
                min_dist = dist
                closest_castle = castle

        # Reflection of my castles
        for m_castle in castle_locs:
            castle = reflect(bc, m_castle, self.is_horizontal_reflect())
            if not loc_in_list(castle, self.enemy_castles):
                self.enemy_castles.append(castle)
            bc.log('castle: {}'.format(castle))
            dist = distance(loc, castle)
            bc.log('dist: {}'.format(dist))
            if int(dist) < int(min_dist):
                min_dist = dist
                closest_castle = castle

        return closest_castle

    # TODO test
    def fuel_rush_mine(self, bc):
        """ only for castles """
        my_loc = locate(bc.me)
        enemy_castle = reflect(bc, my_loc, self.horizontal_reflection)
        rush_mines = []
        for mine in self.fuel_mines:
            if man_distance(mine, my_loc) < 6 or man_distance(mine, enemy_castle) < 6:
                continue
            else:
                rush_mines.append(mine)

        return closest(bc, enemy_castle, rush_mines)

    # TODO test
    def karb_rush_mine(self, bc):
        """ only for castles """
        my_loc = locate(bc.me)
        enemy_castle = reflect(bc, my_loc, self.horizontal_reflection)
        rush_mines = []
        for mine in self.karb_mines:
            if man_distance(mine, my_loc) < 6 or man_distance(mine, enemy_castle) < 6:
                continue
            else:
                rush_mines.append(mine)

        return closest(bc, enemy_castle, rush_mines)

    # TODO test
    def find_next_mine_to_attack(self, bc, loc):

        self.karb_mines = [mine for mine in self.karb_mines if man_distance(loc, mine) > 7]
        self.fuel_mines = [mine for mine in self.fuel_mines if man_distance(loc, mine) > 7]

        mines = self.fuel_mines
        for mine in self.karb_mines:
            mines.append(mine)

        return closest(bc, bc.destination, mines)

    def get_church_spot(self, bc, loc):
        """ This will get all mines close to the loc and get adjacents and rate them"""
        bc.log('Choosing Ground for the holy land (get church spot)')
        candidates = {}
        max_points = 0
        chosen_spot = None

        close_k_mines = [mine for mine in self.karb_mines if man_distance(loc, mine) < 7]
        close_f_mines = [mine for mine in self.fuel_mines if man_distance(loc, mine) < 7]

        mines = close_f_mines
        for mine in close_k_mines:
            mines.append(mine)

        # bc.log('Church mines')
        # bc.log('{}'.format(mines))

        for mine in mines:
            # spots = walkable_adjacent_tiles(bc, *mine)
            spots = passable_adjacent_tiles(bc, *mine)
            # bc.log('spots')
            # bc.log('{}'.format(spots))
            for spot in spots:
                if loc_in_list(spot, mines):
                    continue  # Better not build in a mine

                # May break
                if not candidates.__contains__(spot):
                    # bc.log('.')
                    candidates[spot] = 1
                else:
                    candidates[spot] += 1

        bc.log('Candidates {}'.format(candidates))
        # May break
        for spot in candidates.keys():
            points = candidates[spot]
            if points > max_points:
                max_points = points
                chosen_spot = spot

        return tuple([int(x) for x in chosen_spot.split(',')])  # FUCK JAVASCRIPT AND YOUR TRANSPILER, REALLY
        # return (0, 0)

    # Assign all mines to that church or only its own?????

    # # Restructure my mines when there is a church
    # def filter_mines_bc_church(self, bc, church):
    #     """
    #
    #     :param bc:
    #     :param church: church location
    #     :return: None
    #     """
    #     my_loc = locate(bc.me)
    #     # add the church
    #     all_deposits = self.my_castles
    #     all_deposits.append(church)
    #     # Remove my loc from castle locs
    #     my_castles = [castle for castle in all_deposits if castle != my_loc]
    #     # filter distances if d other castles < my dist
    #     for castle in my_castles:
    #         for d, mine in self.k_distances:
    #             if man_distance(castle, mine) < d:
    #                 self.karb_mines.remove(mine)
    #         for d, mine in self.f_distances:
    #             if man_distance(castle, mine) < d:
    #                 self.fuel_mines.remove(mine)
    #     self.sorted_mines_by_distance(bc)

    # TODO check with nav if close are conected

    def log_lists(self, bc):
        bc.log('map_size: {}'.format(self.map_size))
        bc.log('n_castles: {}'.format(self.n_castles))
        bc.log('passable_size: {}'.format(self.passable_tiles))
        bc.log('passable_pct: {}%'.format(int(self.passable_pct * 100)))
        bc.log('horizontal reflect: {}'.format(self.horizontal_reflection))
        bc.log('n_karb_mines: {}'.format(len(self.karb_mines)))
        # bc.log('karb_mines: {}'.format(self.karb_mines))
        # bc.log('fuel_mines: {}'.format(self.fuel_mines))
        bc.log('n_fuel_mines: {}'.format(len(self.fuel_mines)))
        bc.log('my castles: {}'.format(self.my_castles))
        bc.log('enemy_castles: {}'.format(self.enemy_castles))


#
#


def sort_tuples(arr, bc):
    """ selection sort from:
    https://medium.com/@george.seif94/a-tour-of-the-top-5-sorting-algorithms-with-python-code-43ea9aa02889
    """
    # bc.log('before sort')
    # bc.log(arr)

    for i in range(len(arr)):
        minimum = i

        for j in range(i + 1, len(arr)):
            # Select the smallest value

            a = int(arr[j][0])
            b = int(arr[minimum][0])

            if a < b:
                minimum = j

        # Place it at the front of the
        # sorted end of the array
        arr[minimum], arr[i] = arr[i], arr[minimum]

    # bc.log('after')
    # bc.log(arr)

    return arr


def sorted_tuples(arr):
    """ selection sort from:
    https://medium.com/@george.seif94/a-tour-of-the-top-5-sorting-algorithms-with-python-code-43ea9aa02889
    """
    # bc.log('before sort')
    # bc.log(arr)

    for i in range(len(arr)):
        minimum = i

        for j in range(i + 1, len(arr)):
            # Select the smallest value

            a = int(arr[j][0])
            b = int(arr[minimum][0])

            if a < b:
                minimum = j

        # Place it at the front of the
        # sorted end of the array
        arr[minimum], arr[i] = arr[i], arr[minimum]

    # bc.log('after')
    # bc.log(arr)

    return arr


#
#
# import math

"""
HARDCODED ALL THE RANGES AND RINGS 
to avoid having to deal with js-transpiled iterables

"""

RANGE_1 = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0)]
RANGE_4 = [(-2, 0), (-1, -1), (-1, 0), (-1, 1), (0, -2), (0, -1), (0, 0), (0, 1), (0, 2), (1, -1), (1, 0), (1, 1),
           (2, 0)]
RANGE_9 = [(-3, 0), (-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2), (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2),
           (0, -3), (0, -2), (0, -1), (0, 0), (0, 1), (0, 2), (0, 3), (1, -2), (1, -1), (1, 0), (1, 1), (1, 2), (2, -2),
           (2, -1), (2, 0), (2, 1), (2, 2), (3, 0)]
RANGE_16 = [(-4, 0), (-3, -2), (-3, -1), (-3, 0), (-3, 1), (-3, 2), (-2, -3), (-2, -2), (-2, -1), (-2, 0), (-2, 1),
            (-2, 2), (-2, 3), (-1, -3), (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2), (-1, 3), (0, -4), (0, -3),
            (0, -2), (0, -1), (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, -3), (1, -2), (1, -1), (1, 0), (1, 1), (1, 2),
            (1, 3), (2, -3), (2, -2), (2, -1), (2, 0), (2, 1), (2, 2), (2, 3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2),
            (4, 0)]
RANGE_25 = [(-5, 0), (-4, -3), (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-3, -4), (-3, -3), (-3, -2),
            (-3, -1), (-3, 0), (-3, 1), (-3, 2), (-3, 3), (-3, 4), (-2, -4), (-2, -3), (-2, -2), (-2, -1), (-2, 0),
            (-2, 1), (-2, 2), (-2, 3), (-2, 4), (-1, -4), (-1, -3), (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2),
            (-1, 3), (-1, 4), (0, -5), (0, -4), (0, -3), (0, -2), (0, -1), (0, 0), (0, 1), (0, 2), (0, 3), (0, 4),
            (0, 5), (1, -4), (1, -3), (1, -2), (1, -1), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (2, -4), (2, -3),
            (2, -2), (2, -1), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (3, -4), (3, -3), (3, -2), (3, -1), (3, 0),
            (3, 1), (3, 2), (3, 3), (3, 4), (4, -3), (4, -2), (4, -1), (4, 0), (4, 1), (4, 2), (4, 3), (5, 0)]
RANGE_36 = [(-6, 0), (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3), (-4, -4), (-4, -3), (-4, -2),
            (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-3, -5), (-3, -4), (-3, -3), (-3, -2), (-3, -1),
            (-3, 0), (-3, 1), (-3, 2), (-3, 3), (-3, 4), (-3, 5), (-2, -5), (-2, -4), (-2, -3), (-2, -2), (-2, -1),
            (-2, 0), (-2, 1), (-2, 2), (-2, 3), (-2, 4), (-2, 5), (-1, -5), (-1, -4), (-1, -3), (-1, -2), (-1, -1),
            (-1, 0), (-1, 1), (-1, 2), (-1, 3), (-1, 4), (-1, 5), (0, -6), (0, -5), (0, -4), (0, -3), (0, -2), (0, -1),
            (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (1, -5), (1, -4), (1, -3), (1, -2), (1, -1), (1, 0),
            (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (2, -5), (2, -4), (2, -3), (2, -2), (2, -1), (2, 0), (2, 1), (2, 2),
            (2, 3), (2, 4), (2, 5), (3, -5), (3, -4), (3, -3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4),
            (3, 5), (4, -4), (4, -3), (4, -2), (4, -1), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (5, -3), (5, -2),
            (5, -1), (5, 0), (5, 1), (5, 2), (5, 3), (6, 0)]
RANGE_49 = [(-7, 0), (-6, -3), (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3), (-5, -4), (-5, -3), (-5, -2),
            (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3), (-5, 4), (-4, -5), (-4, -4), (-4, -3), (-4, -2), (-4, -1),
            (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2),
            (-3, -1), (-3, 0), (-3, 1), (-3, 2), (-3, 3), (-3, 4), (-3, 5), (-3, 6), (-2, -6), (-2, -5), (-2, -4),
            (-2, -3), (-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2), (-2, 3), (-2, 4), (-2, 5), (-2, 6), (-1, -6),
            (-1, -5), (-1, -4), (-1, -3), (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2), (-1, 3), (-1, 4), (-1, 5),
            (-1, 6), (0, -7), (0, -6), (0, -5), (0, -4), (0, -3), (0, -2), (0, -1), (0, 0), (0, 1), (0, 2), (0, 3),
            (0, 4), (0, 5), (0, 6), (0, 7), (1, -6), (1, -5), (1, -4), (1, -3), (1, -2), (1, -1), (1, 0), (1, 1),
            (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (2, -6), (2, -5), (2, -4), (2, -3), (2, -2), (2, -1), (2, 0),
            (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (3, -6), (3, -5), (3, -4), (3, -3), (3, -2), (3, -1),
            (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (4, -5), (4, -4), (4, -3), (4, -2), (4, -1), (4, 0),
            (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (5, -4), (5, -3), (5, -2), (5, -1), (5, 0), (5, 1), (5, 2), (5, 3),
            (5, 4), (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (7, 0)]
RANGE_64 = [(-8, 0), (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2), (-7, 3), (-6, -5), (-6, -4), (-6, -3),
            (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3), (-6, 4), (-6, 5), (-5, -6), (-5, -5), (-5, -4),
            (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3), (-5, 4), (-5, 5), (-5, 6), (-4, -6),
            (-4, -5), (-4, -4), (-4, -3), (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5),
            (-4, 6), (-3, -7), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2), (-3, -1), (-3, 0), (-3, 1), (-3, 2),
            (-3, 3), (-3, 4), (-3, 5), (-3, 6), (-3, 7), (-2, -7), (-2, -6), (-2, -5), (-2, -4), (-2, -3), (-2, -2),
            (-2, -1), (-2, 0), (-2, 1), (-2, 2), (-2, 3), (-2, 4), (-2, 5), (-2, 6), (-2, 7), (-1, -7), (-1, -6),
            (-1, -5), (-1, -4), (-1, -3), (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2), (-1, 3), (-1, 4), (-1, 5),
            (-1, 6), (-1, 7), (0, -8), (0, -7), (0, -6), (0, -5), (0, -4), (0, -3), (0, -2), (0, -1), (0, 0), (0, 1),
            (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (1, -7), (1, -6), (1, -5), (1, -4), (1, -3),
            (1, -2), (1, -1), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (2, -7), (2, -6), (2, -5),
            (2, -4), (2, -3), (2, -2), (2, -1), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (3, -7),
            (3, -6), (3, -5), (3, -4), (3, -3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5),
            (3, 6), (3, 7), (4, -6), (4, -5), (4, -4), (4, -3), (4, -2), (4, -1), (4, 0), (4, 1), (4, 2), (4, 3),
            (4, 4), (4, 5), (4, 6), (5, -6), (5, -5), (5, -4), (5, -3), (5, -2), (5, -1), (5, 0), (5, 1), (5, 2),
            (5, 3), (5, 4), (5, 5), (5, 6), (6, -5), (6, -4), (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2), (6, 3),
            (6, 4), (6, 5), (7, -3), (7, -2), (7, -1), (7, 0), (7, 1), (7, 2), (7, 3), (8, 0)]
RANGE_81 = [(-9, 0), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1), (-8, 2), (-8, 3), (-8, 4), (-7, -5),
            (-7, -4), (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2), (-7, 3), (-7, 4), (-7, 5), (-6, -6),
            (-6, -5), (-6, -4), (-6, -3), (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3), (-6, 4), (-6, 5),
            (-6, 6), (-5, -7), (-5, -6), (-5, -5), (-5, -4), (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2),
            (-5, 3), (-5, 4), (-5, 5), (-5, 6), (-5, 7), (-4, -8), (-4, -7), (-4, -6), (-4, -5), (-4, -4), (-4, -3),
            (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5), (-4, 6), (-4, 7), (-4, 8),
            (-3, -8), (-3, -7), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2), (-3, -1), (-3, 0), (-3, 1), (-3, 2),
            (-3, 3), (-3, 4), (-3, 5), (-3, 6), (-3, 7), (-3, 8), (-2, -8), (-2, -7), (-2, -6), (-2, -5), (-2, -4),
            (-2, -3), (-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2), (-2, 3), (-2, 4), (-2, 5), (-2, 6), (-2, 7),
            (-2, 8), (-1, -8), (-1, -7), (-1, -6), (-1, -5), (-1, -4), (-1, -3), (-1, -2), (-1, -1), (-1, 0), (-1, 1),
            (-1, 2), (-1, 3), (-1, 4), (-1, 5), (-1, 6), (-1, 7), (-1, 8), (0, -9), (0, -8), (0, -7), (0, -6), (0, -5),
            (0, -4), (0, -3), (0, -2), (0, -1), (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8),
            (0, 9), (1, -8), (1, -7), (1, -6), (1, -5), (1, -4), (1, -3), (1, -2), (1, -1), (1, 0), (1, 1), (1, 2),
            (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (2, -8), (2, -7), (2, -6), (2, -5), (2, -4), (2, -3),
            (2, -2), (2, -1), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (3, -8), (3, -7),
            (3, -6), (3, -5), (3, -4), (3, -3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5),
            (3, 6), (3, 7), (3, 8), (4, -8), (4, -7), (4, -6), (4, -5), (4, -4), (4, -3), (4, -2), (4, -1), (4, 0),
            (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (5, -7), (5, -6), (5, -5), (5, -4), (5, -3),
            (5, -2), (5, -1), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (6, -6), (6, -5), (6, -4),
            (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (7, -5), (7, -4),
            (7, -3), (7, -2), (7, -1), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (8, -4), (8, -3), (8, -2),
            (8, -1), (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (9, 0)]
RANGE_100 = [(-10, 0), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 0), (-9, 1), (-9, 2), (-9, 3), (-9, 4), (-8, -6),
             (-8, -5), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1), (-8, 2), (-8, 3), (-8, 4), (-8, 5),
             (-8, 6), (-7, -7), (-7, -6), (-7, -5), (-7, -4), (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2),
             (-7, 3), (-7, 4), (-7, 5), (-7, 6), (-7, 7), (-6, -8), (-6, -7), (-6, -6), (-6, -5), (-6, -4), (-6, -3),
             (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3), (-6, 4), (-6, 5), (-6, 6), (-6, 7), (-6, 8),
             (-5, -8), (-5, -7), (-5, -6), (-5, -5), (-5, -4), (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2),
             (-5, 3), (-5, 4), (-5, 5), (-5, 6), (-5, 7), (-5, 8), (-4, -9), (-4, -8), (-4, -7), (-4, -6), (-4, -5),
             (-4, -4), (-4, -3), (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5), (-4, 6),
             (-4, 7), (-4, 8), (-4, 9), (-3, -9), (-3, -8), (-3, -7), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2),
             (-3, -1), (-3, 0), (-3, 1), (-3, 2), (-3, 3), (-3, 4), (-3, 5), (-3, 6), (-3, 7), (-3, 8), (-3, 9),
             (-2, -9), (-2, -8), (-2, -7), (-2, -6), (-2, -5), (-2, -4), (-2, -3), (-2, -2), (-2, -1), (-2, 0), (-2, 1),
             (-2, 2), (-2, 3), (-2, 4), (-2, 5), (-2, 6), (-2, 7), (-2, 8), (-2, 9), (-1, -9), (-1, -8), (-1, -7),
             (-1, -6), (-1, -5), (-1, -4), (-1, -3), (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2), (-1, 3), (-1, 4),
             (-1, 5), (-1, 6), (-1, 7), (-1, 8), (-1, 9), (0, -10), (0, -9), (0, -8), (0, -7), (0, -6), (0, -5),
             (0, -4), (0, -3), (0, -2), (0, -1), (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8),
             (0, 9), (0, 10), (1, -9), (1, -8), (1, -7), (1, -6), (1, -5), (1, -4), (1, -3), (1, -2), (1, -1), (1, 0),
             (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (2, -9), (2, -8), (2, -7), (2, -6),
             (2, -5), (2, -4), (2, -3), (2, -2), (2, -1), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6),
             (2, 7), (2, 8), (2, 9), (3, -9), (3, -8), (3, -7), (3, -6), (3, -5), (3, -4), (3, -3), (3, -2), (3, -1),
             (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (4, -9), (4, -8), (4, -7),
             (4, -6), (4, -5), (4, -4), (4, -3), (4, -2), (4, -1), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5),
             (4, 6), (4, 7), (4, 8), (4, 9), (5, -8), (5, -7), (5, -6), (5, -5), (5, -4), (5, -3), (5, -2), (5, -1),
             (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (6, -8), (6, -7), (6, -6), (6, -5),
             (6, -4), (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8),
             (7, -7), (7, -6), (7, -5), (7, -4), (7, -3), (7, -2), (7, -1), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4),
             (7, 5), (7, 6), (7, 7), (8, -6), (8, -5), (8, -4), (8, -3), (8, -2), (8, -1), (8, 0), (8, 1), (8, 2),
             (8, 3), (8, 4), (8, 5), (8, 6), (9, -4), (9, -3), (9, -2), (9, -1), (9, 0), (9, 1), (9, 2), (9, 3), (9, 4),
             (10, 0)]
RANGE_121 = [(-11, 0), (-10, -4), (-10, -3), (-10, -2), (-10, -1), (-10, 0), (-10, 1), (-10, 2), (-10, 3), (-10, 4),
             (-9, -6), (-9, -5), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 0), (-9, 1), (-9, 2), (-9, 3), (-9, 4),
             (-9, 5), (-9, 6), (-8, -7), (-8, -6), (-8, -5), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1),
             (-8, 2), (-8, 3), (-8, 4), (-8, 5), (-8, 6), (-8, 7), (-7, -8), (-7, -7), (-7, -6), (-7, -5), (-7, -4),
             (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2), (-7, 3), (-7, 4), (-7, 5), (-7, 6), (-7, 7),
             (-7, 8), (-6, -9), (-6, -8), (-6, -7), (-6, -6), (-6, -5), (-6, -4), (-6, -3), (-6, -2), (-6, -1), (-6, 0),
             (-6, 1), (-6, 2), (-6, 3), (-6, 4), (-6, 5), (-6, 6), (-6, 7), (-6, 8), (-6, 9), (-5, -9), (-5, -8),
             (-5, -7), (-5, -6), (-5, -5), (-5, -4), (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3),
             (-5, 4), (-5, 5), (-5, 6), (-5, 7), (-5, 8), (-5, 9), (-4, -10), (-4, -9), (-4, -8), (-4, -7), (-4, -6),
             (-4, -5), (-4, -4), (-4, -3), (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5),
             (-4, 6), (-4, 7), (-4, 8), (-4, 9), (-4, 10), (-3, -10), (-3, -9), (-3, -8), (-3, -7), (-3, -6), (-3, -5),
             (-3, -4), (-3, -3), (-3, -2), (-3, -1), (-3, 0), (-3, 1), (-3, 2), (-3, 3), (-3, 4), (-3, 5), (-3, 6),
             (-3, 7), (-3, 8), (-3, 9), (-3, 10), (-2, -10), (-2, -9), (-2, -8), (-2, -7), (-2, -6), (-2, -5), (-2, -4),
             (-2, -3), (-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2), (-2, 3), (-2, 4), (-2, 5), (-2, 6), (-2, 7),
             (-2, 8), (-2, 9), (-2, 10), (-1, -10), (-1, -9), (-1, -8), (-1, -7), (-1, -6), (-1, -5), (-1, -4),
             (-1, -3), (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2), (-1, 3), (-1, 4), (-1, 5), (-1, 6), (-1, 7),
             (-1, 8), (-1, 9), (-1, 10), (0, -11), (0, -10), (0, -9), (0, -8), (0, -7), (0, -6), (0, -5), (0, -4),
             (0, -3), (0, -2), (0, -1), (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9),
             (0, 10), (0, 11), (1, -10), (1, -9), (1, -8), (1, -7), (1, -6), (1, -5), (1, -4), (1, -3), (1, -2),
             (1, -1), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10), (2, -10),
             (2, -9), (2, -8), (2, -7), (2, -6), (2, -5), (2, -4), (2, -3), (2, -2), (2, -1), (2, 0), (2, 1), (2, 2),
             (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (2, 10), (3, -10), (3, -9), (3, -8), (3, -7),
             (3, -6), (3, -5), (3, -4), (3, -3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5),
             (3, 6), (3, 7), (3, 8), (3, 9), (3, 10), (4, -10), (4, -9), (4, -8), (4, -7), (4, -6), (4, -5), (4, -4),
             (4, -3), (4, -2), (4, -1), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9),
             (4, 10), (5, -9), (5, -8), (5, -7), (5, -6), (5, -5), (5, -4), (5, -3), (5, -2), (5, -1), (5, 0), (5, 1),
             (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (5, 9), (6, -9), (6, -8), (6, -7), (6, -6),
             (6, -5), (6, -4), (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6),
             (6, 7), (6, 8), (6, 9), (7, -8), (7, -7), (7, -6), (7, -5), (7, -4), (7, -3), (7, -2), (7, -1), (7, 0),
             (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (7, 8), (8, -7), (8, -6), (8, -5), (8, -4),
             (8, -3), (8, -2), (8, -1), (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (9, -6),
             (9, -5), (9, -4), (9, -3), (9, -2), (9, -1), (9, 0), (9, 1), (9, 2), (9, 3), (9, 4), (9, 5), (9, 6),
             (10, -4), (10, -3), (10, -2), (10, -1), (10, 0), (10, 1), (10, 2), (10, 3), (10, 4), (11, 0)]
RANGE_144 = [(-12, 0), (-11, -4), (-11, -3), (-11, -2), (-11, -1), (-11, 0), (-11, 1), (-11, 2), (-11, 3), (-11, 4),
             (-10, -6), (-10, -5), (-10, -4), (-10, -3), (-10, -2), (-10, -1), (-10, 0), (-10, 1), (-10, 2), (-10, 3),
             (-10, 4), (-10, 5), (-10, 6), (-9, -7), (-9, -6), (-9, -5), (-9, -4), (-9, -3), (-9, -2), (-9, -1),
             (-9, 0), (-9, 1), (-9, 2), (-9, 3), (-9, 4), (-9, 5), (-9, 6), (-9, 7), (-8, -8), (-8, -7), (-8, -6),
             (-8, -5), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1), (-8, 2), (-8, 3), (-8, 4), (-8, 5),
             (-8, 6), (-8, 7), (-8, 8), (-7, -9), (-7, -8), (-7, -7), (-7, -6), (-7, -5), (-7, -4), (-7, -3), (-7, -2),
             (-7, -1), (-7, 0), (-7, 1), (-7, 2), (-7, 3), (-7, 4), (-7, 5), (-7, 6), (-7, 7), (-7, 8), (-7, 9),
             (-6, -10), (-6, -9), (-6, -8), (-6, -7), (-6, -6), (-6, -5), (-6, -4), (-6, -3), (-6, -2), (-6, -1),
             (-6, 0), (-6, 1), (-6, 2), (-6, 3), (-6, 4), (-6, 5), (-6, 6), (-6, 7), (-6, 8), (-6, 9), (-6, 10),
             (-5, -10), (-5, -9), (-5, -8), (-5, -7), (-5, -6), (-5, -5), (-5, -4), (-5, -3), (-5, -2), (-5, -1),
             (-5, 0), (-5, 1), (-5, 2), (-5, 3), (-5, 4), (-5, 5), (-5, 6), (-5, 7), (-5, 8), (-5, 9), (-5, 10),
             (-4, -11), (-4, -10), (-4, -9), (-4, -8), (-4, -7), (-4, -6), (-4, -5), (-4, -4), (-4, -3), (-4, -2),
             (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5), (-4, 6), (-4, 7), (-4, 8), (-4, 9),
             (-4, 10), (-4, 11), (-3, -11), (-3, -10), (-3, -9), (-3, -8), (-3, -7), (-3, -6), (-3, -5), (-3, -4),
             (-3, -3), (-3, -2), (-3, -1), (-3, 0), (-3, 1), (-3, 2), (-3, 3), (-3, 4), (-3, 5), (-3, 6), (-3, 7),
             (-3, 8), (-3, 9), (-3, 10), (-3, 11), (-2, -11), (-2, -10), (-2, -9), (-2, -8), (-2, -7), (-2, -6),
             (-2, -5), (-2, -4), (-2, -3), (-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2), (-2, 3), (-2, 4), (-2, 5),
             (-2, 6), (-2, 7), (-2, 8), (-2, 9), (-2, 10), (-2, 11), (-1, -11), (-1, -10), (-1, -9), (-1, -8), (-1, -7),
             (-1, -6), (-1, -5), (-1, -4), (-1, -3), (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2), (-1, 3), (-1, 4),
             (-1, 5), (-1, 6), (-1, 7), (-1, 8), (-1, 9), (-1, 10), (-1, 11), (0, -12), (0, -11), (0, -10), (0, -9),
             (0, -8), (0, -7), (0, -6), (0, -5), (0, -4), (0, -3), (0, -2), (0, -1), (0, 0), (0, 1), (0, 2), (0, 3),
             (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10), (0, 11), (0, 12), (1, -11), (1, -10), (1, -9),
             (1, -8), (1, -7), (1, -6), (1, -5), (1, -4), (1, -3), (1, -2), (1, -1), (1, 0), (1, 1), (1, 2), (1, 3),
             (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10), (1, 11), (2, -11), (2, -10), (2, -9), (2, -8),
             (2, -7), (2, -6), (2, -5), (2, -4), (2, -3), (2, -2), (2, -1), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),
             (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (2, 10), (2, 11), (3, -11), (3, -10), (3, -9), (3, -8), (3, -7),
             (3, -6), (3, -5), (3, -4), (3, -3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5),
             (3, 6), (3, 7), (3, 8), (3, 9), (3, 10), (3, 11), (4, -11), (4, -10), (4, -9), (4, -8), (4, -7), (4, -6),
             (4, -5), (4, -4), (4, -3), (4, -2), (4, -1), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6),
             (4, 7), (4, 8), (4, 9), (4, 10), (4, 11), (5, -10), (5, -9), (5, -8), (5, -7), (5, -6), (5, -5), (5, -4),
             (5, -3), (5, -2), (5, -1), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (5, 9),
             (5, 10), (6, -10), (6, -9), (6, -8), (6, -7), (6, -6), (6, -5), (6, -4), (6, -3), (6, -2), (6, -1), (6, 0),
             (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8), (6, 9), (6, 10), (7, -9), (7, -8), (7, -7),
             (7, -6), (7, -5), (7, -4), (7, -3), (7, -2), (7, -1), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5),
             (7, 6), (7, 7), (7, 8), (7, 9), (8, -8), (8, -7), (8, -6), (8, -5), (8, -4), (8, -3), (8, -2), (8, -1),
             (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (8, 8), (9, -7), (9, -6), (9, -5), (9, -4),
             (9, -3), (9, -2), (9, -1), (9, 0), (9, 1), (9, 2), (9, 3), (9, 4), (9, 5), (9, 6), (9, 7), (10, -6),
             (10, -5), (10, -4), (10, -3), (10, -2), (10, -1), (10, 0), (10, 1), (10, 2), (10, 3), (10, 4), (10, 5),
             (10, 6), (11, -4), (11, -3), (11, -2), (11, -1), (11, 0), (11, 1), (11, 2), (11, 3), (11, 4), (12, 0)]

RANGES = [[(0, 0)],
          RANGE_1,
          RANGE_4,
          RANGE_9,
          RANGE_16,
          RANGE_25,
          RANGE_36,
          RANGE_49,
          RANGE_64,
          RANGE_81,
          RANGE_100,
          RANGE_121,
          RANGE_144]

RINGS = [
    [
        [],
        [(-1, 0), (0, -1), (0, 1), (1, 0)]
        ,
        [(-2, 0), (-1, -1), (-1, 0), (-1, 1), (0, -2), (0, -1), (0, 1), (0, 2), (1, -1), (1, 0), (1, 1), (2, 0)]
        ,
        [(-3, 0), (-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2), (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2), (0, -3),
         (0, -2), (0, -1), (0, 1), (0, 2), (0, 3), (1, -2), (1, -1), (1, 0), (1, 1), (1, 2), (2, -2), (2, -1), (2, 0),
         (2, 1), (2, 2), (3, 0)]
        ,
        [(-4, 0), (-3, -2), (-3, -1), (-3, 0), (-3, 1), (-3, 2), (-2, -3), (-2, -2), (-2, -1), (-2, 0), (-2, 1),
         (-2, 2), (-2, 3), (-1, -3), (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2), (-1, 3), (0, -4), (0, -3), (0, -2),
         (0, -1), (0, 1), (0, 2), (0, 3), (0, 4), (1, -3), (1, -2), (1, -1), (1, 0), (1, 1), (1, 2), (1, 3), (2, -3),
         (2, -2), (2, -1), (2, 0), (2, 1), (2, 2), (2, 3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (4, 0)]
        ,
        [(-5, 0), (-4, -3), (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-3, -4), (-3, -3), (-3, -2),
         (-3, -1), (-3, 0), (-3, 1), (-3, 2), (-3, 3), (-3, 4), (-2, -4), (-2, -3), (-2, -2), (-2, -1), (-2, 0),
         (-2, 1), (-2, 2), (-2, 3), (-2, 4), (-1, -4), (-1, -3), (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2), (-1, 3),
         (-1, 4), (0, -5), (0, -4), (0, -3), (0, -2), (0, -1), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, -4), (1, -3),
         (1, -2), (1, -1), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (2, -4), (2, -3), (2, -2), (2, -1), (2, 0), (2, 1),
         (2, 2), (2, 3), (2, 4), (3, -4), (3, -3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (4, -3),
         (4, -2), (4, -1), (4, 0), (4, 1), (4, 2), (4, 3), (5, 0)]
        ,
        [(-6, 0), (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3), (-4, -4), (-4, -3), (-4, -2),
         (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-3, -5), (-3, -4), (-3, -3), (-3, -2), (-3, -1),
         (-3, 0), (-3, 1), (-3, 2), (-3, 3), (-3, 4), (-3, 5), (-2, -5), (-2, -4), (-2, -3), (-2, -2), (-2, -1),
         (-2, 0), (-2, 1), (-2, 2), (-2, 3), (-2, 4), (-2, 5), (-1, -5), (-1, -4), (-1, -3), (-1, -2), (-1, -1),
         (-1, 0), (-1, 1), (-1, 2), (-1, 3), (-1, 4), (-1, 5), (0, -6), (0, -5), (0, -4), (0, -3), (0, -2), (0, -1),
         (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (1, -5), (1, -4), (1, -3), (1, -2), (1, -1), (1, 0), (1, 1),
         (1, 2), (1, 3), (1, 4), (1, 5), (2, -5), (2, -4), (2, -3), (2, -2), (2, -1), (2, 0), (2, 1), (2, 2), (2, 3),
         (2, 4), (2, 5), (3, -5), (3, -4), (3, -3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5),
         (4, -4), (4, -3), (4, -2), (4, -1), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (5, -3), (5, -2), (5, -1), (5, 0),
         (5, 1), (5, 2), (5, 3), (6, 0)]
        ,
        [(-7, 0), (-6, -3), (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3), (-5, -4), (-5, -3), (-5, -2),
         (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3), (-5, 4), (-4, -5), (-4, -4), (-4, -3), (-4, -2), (-4, -1),
         (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2),
         (-3, -1), (-3, 0), (-3, 1), (-3, 2), (-3, 3), (-3, 4), (-3, 5), (-3, 6), (-2, -6), (-2, -5), (-2, -4),
         (-2, -3), (-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2), (-2, 3), (-2, 4), (-2, 5), (-2, 6), (-1, -6),
         (-1, -5), (-1, -4), (-1, -3), (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2), (-1, 3), (-1, 4), (-1, 5),
         (-1, 6), (0, -7), (0, -6), (0, -5), (0, -4), (0, -3), (0, -2), (0, -1), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5),
         (0, 6), (0, 7), (1, -6), (1, -5), (1, -4), (1, -3), (1, -2), (1, -1), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4),
         (1, 5), (1, 6), (2, -6), (2, -5), (2, -4), (2, -3), (2, -2), (2, -1), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),
         (2, 5), (2, 6), (3, -6), (3, -5), (3, -4), (3, -3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4),
         (3, 5), (3, 6), (4, -5), (4, -4), (4, -3), (4, -2), (4, -1), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5),
         (5, -4), (5, -3), (5, -2), (5, -1), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (6, -3), (6, -2), (6, -1), (6, 0),
         (6, 1), (6, 2), (6, 3), (7, 0)]
        ,
        [(-8, 0), (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2), (-7, 3), (-6, -5), (-6, -4), (-6, -3),
         (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3), (-6, 4), (-6, 5), (-5, -6), (-5, -5), (-5, -4),
         (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3), (-5, 4), (-5, 5), (-5, 6), (-4, -6),
         (-4, -5), (-4, -4), (-4, -3), (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5),
         (-4, 6), (-3, -7), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2), (-3, -1), (-3, 0), (-3, 1), (-3, 2),
         (-3, 3), (-3, 4), (-3, 5), (-3, 6), (-3, 7), (-2, -7), (-2, -6), (-2, -5), (-2, -4), (-2, -3), (-2, -2),
         (-2, -1), (-2, 0), (-2, 1), (-2, 2), (-2, 3), (-2, 4), (-2, 5), (-2, 6), (-2, 7), (-1, -7), (-1, -6), (-1, -5),
         (-1, -4), (-1, -3), (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2), (-1, 3), (-1, 4), (-1, 5), (-1, 6), (-1, 7),
         (0, -8), (0, -7), (0, -6), (0, -5), (0, -4), (0, -3), (0, -2), (0, -1), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5),
         (0, 6), (0, 7), (0, 8), (1, -7), (1, -6), (1, -5), (1, -4), (1, -3), (1, -2), (1, -1), (1, 0), (1, 1), (1, 2),
         (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (2, -7), (2, -6), (2, -5), (2, -4), (2, -3), (2, -2), (2, -1), (2, 0),
         (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (3, -7), (3, -6), (3, -5), (3, -4), (3, -3), (3, -2),
         (3, -1), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (4, -6), (4, -5), (4, -4), (4, -3),
         (4, -2), (4, -1), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (5, -6), (5, -5), (5, -4), (5, -3),
         (5, -2), (5, -1), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (6, -5), (6, -4), (6, -3), (6, -2),
         (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (7, -3), (7, -2), (7, -1), (7, 0), (7, 1), (7, 2),
         (7, 3), (8, 0)]
        ,
        [(-9, 0), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1), (-8, 2), (-8, 3), (-8, 4), (-7, -5),
         (-7, -4), (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2), (-7, 3), (-7, 4), (-7, 5), (-6, -6),
         (-6, -5), (-6, -4), (-6, -3), (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3), (-6, 4), (-6, 5),
         (-6, 6), (-5, -7), (-5, -6), (-5, -5), (-5, -4), (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2),
         (-5, 3), (-5, 4), (-5, 5), (-5, 6), (-5, 7), (-4, -8), (-4, -7), (-4, -6), (-4, -5), (-4, -4), (-4, -3),
         (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5), (-4, 6), (-4, 7), (-4, 8), (-3, -8),
         (-3, -7), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2), (-3, -1), (-3, 0), (-3, 1), (-3, 2), (-3, 3),
         (-3, 4), (-3, 5), (-3, 6), (-3, 7), (-3, 8), (-2, -8), (-2, -7), (-2, -6), (-2, -5), (-2, -4), (-2, -3),
         (-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2), (-2, 3), (-2, 4), (-2, 5), (-2, 6), (-2, 7), (-2, 8), (-1, -8),
         (-1, -7), (-1, -6), (-1, -5), (-1, -4), (-1, -3), (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2), (-1, 3),
         (-1, 4), (-1, 5), (-1, 6), (-1, 7), (-1, 8), (0, -9), (0, -8), (0, -7), (0, -6), (0, -5), (0, -4), (0, -3),
         (0, -2), (0, -1), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (1, -8), (1, -7),
         (1, -6), (1, -5), (1, -4), (1, -3), (1, -2), (1, -1), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6),
         (1, 7), (1, 8), (2, -8), (2, -7), (2, -6), (2, -5), (2, -4), (2, -3), (2, -2), (2, -1), (2, 0), (2, 1), (2, 2),
         (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (3, -8), (3, -7), (3, -6), (3, -5), (3, -4), (3, -3), (3, -2),
         (3, -1), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (4, -8), (4, -7), (4, -6),
         (4, -5), (4, -4), (4, -3), (4, -2), (4, -1), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7),
         (4, 8), (5, -7), (5, -6), (5, -5), (5, -4), (5, -3), (5, -2), (5, -1), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4),
         (5, 5), (5, 6), (5, 7), (6, -6), (6, -5), (6, -4), (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2), (6, 3),
         (6, 4), (6, 5), (6, 6), (7, -5), (7, -4), (7, -3), (7, -2), (7, -1), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4),
         (7, 5), (8, -4), (8, -3), (8, -2), (8, -1), (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (9, 0)]
        ,
        [(-10, 0), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 0), (-9, 1), (-9, 2), (-9, 3), (-9, 4), (-8, -6),
         (-8, -5), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1), (-8, 2), (-8, 3), (-8, 4), (-8, 5),
         (-8, 6), (-7, -7), (-7, -6), (-7, -5), (-7, -4), (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2),
         (-7, 3), (-7, 4), (-7, 5), (-7, 6), (-7, 7), (-6, -8), (-6, -7), (-6, -6), (-6, -5), (-6, -4), (-6, -3),
         (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3), (-6, 4), (-6, 5), (-6, 6), (-6, 7), (-6, 8), (-5, -8),
         (-5, -7), (-5, -6), (-5, -5), (-5, -4), (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3),
         (-5, 4), (-5, 5), (-5, 6), (-5, 7), (-5, 8), (-4, -9), (-4, -8), (-4, -7), (-4, -6), (-4, -5), (-4, -4),
         (-4, -3), (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5), (-4, 6), (-4, 7), (-4, 8),
         (-4, 9), (-3, -9), (-3, -8), (-3, -7), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2), (-3, -1), (-3, 0),
         (-3, 1), (-3, 2), (-3, 3), (-3, 4), (-3, 5), (-3, 6), (-3, 7), (-3, 8), (-3, 9), (-2, -9), (-2, -8), (-2, -7),
         (-2, -6), (-2, -5), (-2, -4), (-2, -3), (-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2), (-2, 3), (-2, 4),
         (-2, 5), (-2, 6), (-2, 7), (-2, 8), (-2, 9), (-1, -9), (-1, -8), (-1, -7), (-1, -6), (-1, -5), (-1, -4),
         (-1, -3), (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2), (-1, 3), (-1, 4), (-1, 5), (-1, 6), (-1, 7), (-1, 8),
         (-1, 9), (0, -10), (0, -9), (0, -8), (0, -7), (0, -6), (0, -5), (0, -4), (0, -3), (0, -2), (0, -1), (0, 1),
         (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10), (1, -9), (1, -8), (1, -7), (1, -6),
         (1, -5), (1, -4), (1, -3), (1, -2), (1, -1), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7),
         (1, 8), (1, 9), (2, -9), (2, -8), (2, -7), (2, -6), (2, -5), (2, -4), (2, -3), (2, -2), (2, -1), (2, 0),
         (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (3, -9), (3, -8), (3, -7), (3, -6),
         (3, -5), (3, -4), (3, -3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7),
         (3, 8), (3, 9), (4, -9), (4, -8), (4, -7), (4, -6), (4, -5), (4, -4), (4, -3), (4, -2), (4, -1), (4, 0),
         (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9), (5, -8), (5, -7), (5, -6), (5, -5),
         (5, -4), (5, -3), (5, -2), (5, -1), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8),
         (6, -8), (6, -7), (6, -6), (6, -5), (6, -4), (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4),
         (6, 5), (6, 6), (6, 7), (6, 8), (7, -7), (7, -6), (7, -5), (7, -4), (7, -3), (7, -2), (7, -1), (7, 0), (7, 1),
         (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (8, -6), (8, -5), (8, -4), (8, -3), (8, -2), (8, -1), (8, 0),
         (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (9, -4), (9, -3), (9, -2), (9, -1), (9, 0), (9, 1), (9, 2),
         (9, 3), (9, 4), (10, 0)]
        ,
        [(-11, 0), (-10, -4), (-10, -3), (-10, -2), (-10, -1), (-10, 0), (-10, 1), (-10, 2), (-10, 3), (-10, 4),
         (-9, -6), (-9, -5), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 0), (-9, 1), (-9, 2), (-9, 3), (-9, 4),
         (-9, 5), (-9, 6), (-8, -7), (-8, -6), (-8, -5), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1),
         (-8, 2), (-8, 3), (-8, 4), (-8, 5), (-8, 6), (-8, 7), (-7, -8), (-7, -7), (-7, -6), (-7, -5), (-7, -4),
         (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2), (-7, 3), (-7, 4), (-7, 5), (-7, 6), (-7, 7), (-7, 8),
         (-6, -9), (-6, -8), (-6, -7), (-6, -6), (-6, -5), (-6, -4), (-6, -3), (-6, -2), (-6, -1), (-6, 0), (-6, 1),
         (-6, 2), (-6, 3), (-6, 4), (-6, 5), (-6, 6), (-6, 7), (-6, 8), (-6, 9), (-5, -9), (-5, -8), (-5, -7), (-5, -6),
         (-5, -5), (-5, -4), (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3), (-5, 4), (-5, 5),
         (-5, 6), (-5, 7), (-5, 8), (-5, 9), (-4, -10), (-4, -9), (-4, -8), (-4, -7), (-4, -6), (-4, -5), (-4, -4),
         (-4, -3), (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5), (-4, 6), (-4, 7), (-4, 8),
         (-4, 9), (-4, 10), (-3, -10), (-3, -9), (-3, -8), (-3, -7), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2),
         (-3, -1), (-3, 0), (-3, 1), (-3, 2), (-3, 3), (-3, 4), (-3, 5), (-3, 6), (-3, 7), (-3, 8), (-3, 9), (-3, 10),
         (-2, -10), (-2, -9), (-2, -8), (-2, -7), (-2, -6), (-2, -5), (-2, -4), (-2, -3), (-2, -2), (-2, -1), (-2, 0),
         (-2, 1), (-2, 2), (-2, 3), (-2, 4), (-2, 5), (-2, 6), (-2, 7), (-2, 8), (-2, 9), (-2, 10), (-1, -10), (-1, -9),
         (-1, -8), (-1, -7), (-1, -6), (-1, -5), (-1, -4), (-1, -3), (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2),
         (-1, 3), (-1, 4), (-1, 5), (-1, 6), (-1, 7), (-1, 8), (-1, 9), (-1, 10), (0, -11), (0, -10), (0, -9), (0, -8),
         (0, -7), (0, -6), (0, -5), (0, -4), (0, -3), (0, -2), (0, -1), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6),
         (0, 7), (0, 8), (0, 9), (0, 10), (0, 11), (1, -10), (1, -9), (1, -8), (1, -7), (1, -6), (1, -5), (1, -4),
         (1, -3), (1, -2), (1, -1), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9),
         (1, 10), (2, -10), (2, -9), (2, -8), (2, -7), (2, -6), (2, -5), (2, -4), (2, -3), (2, -2), (2, -1), (2, 0),
         (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (2, 10), (3, -10), (3, -9), (3, -8),
         (3, -7), (3, -6), (3, -5), (3, -4), (3, -3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5),
         (3, 6), (3, 7), (3, 8), (3, 9), (3, 10), (4, -10), (4, -9), (4, -8), (4, -7), (4, -6), (4, -5), (4, -4),
         (4, -3), (4, -2), (4, -1), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9),
         (4, 10), (5, -9), (5, -8), (5, -7), (5, -6), (5, -5), (5, -4), (5, -3), (5, -2), (5, -1), (5, 0), (5, 1),
         (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (5, 9), (6, -9), (6, -8), (6, -7), (6, -6), (6, -5),
         (6, -4), (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8),
         (6, 9), (7, -8), (7, -7), (7, -6), (7, -5), (7, -4), (7, -3), (7, -2), (7, -1), (7, 0), (7, 1), (7, 2), (7, 3),
         (7, 4), (7, 5), (7, 6), (7, 7), (7, 8), (8, -7), (8, -6), (8, -5), (8, -4), (8, -3), (8, -2), (8, -1), (8, 0),
         (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (9, -6), (9, -5), (9, -4), (9, -3), (9, -2), (9, -1),
         (9, 0), (9, 1), (9, 2), (9, 3), (9, 4), (9, 5), (9, 6), (10, -4), (10, -3), (10, -2), (10, -1), (10, 0),
         (10, 1), (10, 2), (10, 3), (10, 4), (11, 0)]
        ,
        [(-12, 0), (-11, -4), (-11, -3), (-11, -2), (-11, -1), (-11, 0), (-11, 1), (-11, 2), (-11, 3), (-11, 4),
         (-10, -6), (-10, -5), (-10, -4), (-10, -3), (-10, -2), (-10, -1), (-10, 0), (-10, 1), (-10, 2), (-10, 3),
         (-10, 4), (-10, 5), (-10, 6), (-9, -7), (-9, -6), (-9, -5), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 0),
         (-9, 1), (-9, 2), (-9, 3), (-9, 4), (-9, 5), (-9, 6), (-9, 7), (-8, -8), (-8, -7), (-8, -6), (-8, -5),
         (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1), (-8, 2), (-8, 3), (-8, 4), (-8, 5), (-8, 6), (-8, 7),
         (-8, 8), (-7, -9), (-7, -8), (-7, -7), (-7, -6), (-7, -5), (-7, -4), (-7, -3), (-7, -2), (-7, -1), (-7, 0),
         (-7, 1), (-7, 2), (-7, 3), (-7, 4), (-7, 5), (-7, 6), (-7, 7), (-7, 8), (-7, 9), (-6, -10), (-6, -9), (-6, -8),
         (-6, -7), (-6, -6), (-6, -5), (-6, -4), (-6, -3), (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3),
         (-6, 4), (-6, 5), (-6, 6), (-6, 7), (-6, 8), (-6, 9), (-6, 10), (-5, -10), (-5, -9), (-5, -8), (-5, -7),
         (-5, -6), (-5, -5), (-5, -4), (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3), (-5, 4),
         (-5, 5), (-5, 6), (-5, 7), (-5, 8), (-5, 9), (-5, 10), (-4, -11), (-4, -10), (-4, -9), (-4, -8), (-4, -7),
         (-4, -6), (-4, -5), (-4, -4), (-4, -3), (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4),
         (-4, 5), (-4, 6), (-4, 7), (-4, 8), (-4, 9), (-4, 10), (-4, 11), (-3, -11), (-3, -10), (-3, -9), (-3, -8),
         (-3, -7), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2), (-3, -1), (-3, 0), (-3, 1), (-3, 2), (-3, 3),
         (-3, 4), (-3, 5), (-3, 6), (-3, 7), (-3, 8), (-3, 9), (-3, 10), (-3, 11), (-2, -11), (-2, -10), (-2, -9),
         (-2, -8), (-2, -7), (-2, -6), (-2, -5), (-2, -4), (-2, -3), (-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2),
         (-2, 3), (-2, 4), (-2, 5), (-2, 6), (-2, 7), (-2, 8), (-2, 9), (-2, 10), (-2, 11), (-1, -11), (-1, -10),
         (-1, -9), (-1, -8), (-1, -7), (-1, -6), (-1, -5), (-1, -4), (-1, -3), (-1, -2), (-1, -1), (-1, 0), (-1, 1),
         (-1, 2), (-1, 3), (-1, 4), (-1, 5), (-1, 6), (-1, 7), (-1, 8), (-1, 9), (-1, 10), (-1, 11), (0, -12), (0, -11),
         (0, -10), (0, -9), (0, -8), (0, -7), (0, -6), (0, -5), (0, -4), (0, -3), (0, -2), (0, -1), (0, 1), (0, 2),
         (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10), (0, 11), (0, 12), (1, -11), (1, -10), (1, -9),
         (1, -8), (1, -7), (1, -6), (1, -5), (1, -4), (1, -3), (1, -2), (1, -1), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4),
         (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10), (1, 11), (2, -11), (2, -10), (2, -9), (2, -8), (2, -7),
         (2, -6), (2, -5), (2, -4), (2, -3), (2, -2), (2, -1), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6),
         (2, 7), (2, 8), (2, 9), (2, 10), (2, 11), (3, -11), (3, -10), (3, -9), (3, -8), (3, -7), (3, -6), (3, -5),
         (3, -4), (3, -3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8),
         (3, 9), (3, 10), (3, 11), (4, -11), (4, -10), (4, -9), (4, -8), (4, -7), (4, -6), (4, -5), (4, -4), (4, -3),
         (4, -2), (4, -1), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9), (4, 10),
         (4, 11), (5, -10), (5, -9), (5, -8), (5, -7), (5, -6), (5, -5), (5, -4), (5, -3), (5, -2), (5, -1), (5, 0),
         (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (5, 9), (5, 10), (6, -10), (6, -9), (6, -8),
         (6, -7), (6, -6), (6, -5), (6, -4), (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5),
         (6, 6), (6, 7), (6, 8), (6, 9), (6, 10), (7, -9), (7, -8), (7, -7), (7, -6), (7, -5), (7, -4), (7, -3),
         (7, -2), (7, -1), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (7, 8), (7, 9), (8, -8),
         (8, -7), (8, -6), (8, -5), (8, -4), (8, -3), (8, -2), (8, -1), (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5),
         (8, 6), (8, 7), (8, 8), (9, -7), (9, -6), (9, -5), (9, -4), (9, -3), (9, -2), (9, -1), (9, 0), (9, 1), (9, 2),
         (9, 3), (9, 4), (9, 5), (9, 6), (9, 7), (10, -6), (10, -5), (10, -4), (10, -3), (10, -2), (10, -1), (10, 0),
         (10, 1), (10, 2), (10, 3), (10, 4), (10, 5), (10, 6), (11, -4), (11, -3), (11, -2), (11, -1), (11, 0), (11, 1),
         (11, 2), (11, 3), (11, 4), (12, 0)]

    ],
    [
        [],
        [],
        [(-2, 0), (-1, -1), (-1, 1), (0, -2), (0, 2), (1, -1), (1, 1), (2, 0)]
        ,
        [(-3, 0), (-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2), (-1, -2), (-1, -1), (-1, 1), (-1, 2), (0, -3), (0, -2),
         (0, 2), (0, 3), (1, -2), (1, -1), (1, 1), (1, 2), (2, -2), (2, -1), (2, 0), (2, 1), (2, 2), (3, 0)]
        ,
        [(-4, 0), (-3, -2), (-3, -1), (-3, 0), (-3, 1), (-3, 2), (-2, -3), (-2, -2), (-2, -1), (-2, 0), (-2, 1),
         (-2, 2), (-2, 3), (-1, -3), (-1, -2), (-1, -1), (-1, 1), (-1, 2), (-1, 3), (0, -4), (0, -3), (0, -2), (0, 2),
         (0, 3), (0, 4), (1, -3), (1, -2), (1, -1), (1, 1), (1, 2), (1, 3), (2, -3), (2, -2), (2, -1), (2, 0), (2, 1),
         (2, 2), (2, 3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (4, 0)]
        ,
        [(-5, 0), (-4, -3), (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-3, -4), (-3, -3), (-3, -2),
         (-3, -1), (-3, 0), (-3, 1), (-3, 2), (-3, 3), (-3, 4), (-2, -4), (-2, -3), (-2, -2), (-2, -1), (-2, 0),
         (-2, 1), (-2, 2), (-2, 3), (-2, 4), (-1, -4), (-1, -3), (-1, -2), (-1, -1), (-1, 1), (-1, 2), (-1, 3), (-1, 4),
         (0, -5), (0, -4), (0, -3), (0, -2), (0, 2), (0, 3), (0, 4), (0, 5), (1, -4), (1, -3), (1, -2), (1, -1), (1, 1),
         (1, 2), (1, 3), (1, 4), (2, -4), (2, -3), (2, -2), (2, -1), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (3, -4),
         (3, -3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (4, -3), (4, -2), (4, -1), (4, 0), (4, 1),
         (4, 2), (4, 3), (5, 0)]
        ,
        [(-6, 0), (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3), (-4, -4), (-4, -3), (-4, -2),
         (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-3, -5), (-3, -4), (-3, -3), (-3, -2), (-3, -1),
         (-3, 0), (-3, 1), (-3, 2), (-3, 3), (-3, 4), (-3, 5), (-2, -5), (-2, -4), (-2, -3), (-2, -2), (-2, -1),
         (-2, 0), (-2, 1), (-2, 2), (-2, 3), (-2, 4), (-2, 5), (-1, -5), (-1, -4), (-1, -3), (-1, -2), (-1, -1),
         (-1, 1), (-1, 2), (-1, 3), (-1, 4), (-1, 5), (0, -6), (0, -5), (0, -4), (0, -3), (0, -2), (0, 2), (0, 3),
         (0, 4), (0, 5), (0, 6), (1, -5), (1, -4), (1, -3), (1, -2), (1, -1), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5),
         (2, -5), (2, -4), (2, -3), (2, -2), (2, -1), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (3, -5), (3, -4),
         (3, -3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (4, -4), (4, -3), (4, -2), (4, -1),
         (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (5, -3), (5, -2), (5, -1), (5, 0), (5, 1), (5, 2), (5, 3), (6, 0)]
        ,
        [(-7, 0), (-6, -3), (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3), (-5, -4), (-5, -3), (-5, -2),
         (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3), (-5, 4), (-4, -5), (-4, -4), (-4, -3), (-4, -2), (-4, -1),
         (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2),
         (-3, -1), (-3, 0), (-3, 1), (-3, 2), (-3, 3), (-3, 4), (-3, 5), (-3, 6), (-2, -6), (-2, -5), (-2, -4),
         (-2, -3), (-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2), (-2, 3), (-2, 4), (-2, 5), (-2, 6), (-1, -6),
         (-1, -5), (-1, -4), (-1, -3), (-1, -2), (-1, -1), (-1, 1), (-1, 2), (-1, 3), (-1, 4), (-1, 5), (-1, 6),
         (0, -7), (0, -6), (0, -5), (0, -4), (0, -3), (0, -2), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (1, -6),
         (1, -5), (1, -4), (1, -3), (1, -2), (1, -1), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (2, -6), (2, -5),
         (2, -4), (2, -3), (2, -2), (2, -1), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (3, -6), (3, -5),
         (3, -4), (3, -3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (4, -5), (4, -4),
         (4, -3), (4, -2), (4, -1), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (5, -4), (5, -3), (5, -2), (5, -1),
         (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (7, 0)]
        ,
        [(-8, 0), (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2), (-7, 3), (-6, -5), (-6, -4), (-6, -3),
         (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3), (-6, 4), (-6, 5), (-5, -6), (-5, -5), (-5, -4),
         (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3), (-5, 4), (-5, 5), (-5, 6), (-4, -6),
         (-4, -5), (-4, -4), (-4, -3), (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5),
         (-4, 6), (-3, -7), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2), (-3, -1), (-3, 0), (-3, 1), (-3, 2),
         (-3, 3), (-3, 4), (-3, 5), (-3, 6), (-3, 7), (-2, -7), (-2, -6), (-2, -5), (-2, -4), (-2, -3), (-2, -2),
         (-2, -1), (-2, 0), (-2, 1), (-2, 2), (-2, 3), (-2, 4), (-2, 5), (-2, 6), (-2, 7), (-1, -7), (-1, -6), (-1, -5),
         (-1, -4), (-1, -3), (-1, -2), (-1, -1), (-1, 1), (-1, 2), (-1, 3), (-1, 4), (-1, 5), (-1, 6), (-1, 7), (0, -8),
         (0, -7), (0, -6), (0, -5), (0, -4), (0, -3), (0, -2), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8),
         (1, -7), (1, -6), (1, -5), (1, -4), (1, -3), (1, -2), (1, -1), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6),
         (1, 7), (2, -7), (2, -6), (2, -5), (2, -4), (2, -3), (2, -2), (2, -1), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),
         (2, 5), (2, 6), (2, 7), (3, -7), (3, -6), (3, -5), (3, -4), (3, -3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2),
         (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (4, -6), (4, -5), (4, -4), (4, -3), (4, -2), (4, -1), (4, 0), (4, 1),
         (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (5, -6), (5, -5), (5, -4), (5, -3), (5, -2), (5, -1), (5, 0), (5, 1),
         (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (6, -5), (6, -4), (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2),
         (6, 3), (6, 4), (6, 5), (7, -3), (7, -2), (7, -1), (7, 0), (7, 1), (7, 2), (7, 3), (8, 0)]
        ,
        [(-9, 0), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1), (-8, 2), (-8, 3), (-8, 4), (-7, -5),
         (-7, -4), (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2), (-7, 3), (-7, 4), (-7, 5), (-6, -6),
         (-6, -5), (-6, -4), (-6, -3), (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3), (-6, 4), (-6, 5),
         (-6, 6), (-5, -7), (-5, -6), (-5, -5), (-5, -4), (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2),
         (-5, 3), (-5, 4), (-5, 5), (-5, 6), (-5, 7), (-4, -8), (-4, -7), (-4, -6), (-4, -5), (-4, -4), (-4, -3),
         (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5), (-4, 6), (-4, 7), (-4, 8), (-3, -8),
         (-3, -7), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2), (-3, -1), (-3, 0), (-3, 1), (-3, 2), (-3, 3),
         (-3, 4), (-3, 5), (-3, 6), (-3, 7), (-3, 8), (-2, -8), (-2, -7), (-2, -6), (-2, -5), (-2, -4), (-2, -3),
         (-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2), (-2, 3), (-2, 4), (-2, 5), (-2, 6), (-2, 7), (-2, 8), (-1, -8),
         (-1, -7), (-1, -6), (-1, -5), (-1, -4), (-1, -3), (-1, -2), (-1, -1), (-1, 1), (-1, 2), (-1, 3), (-1, 4),
         (-1, 5), (-1, 6), (-1, 7), (-1, 8), (0, -9), (0, -8), (0, -7), (0, -6), (0, -5), (0, -4), (0, -3), (0, -2),
         (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (1, -8), (1, -7), (1, -6), (1, -5), (1, -4),
         (1, -3), (1, -2), (1, -1), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (2, -8), (2, -7),
         (2, -6), (2, -5), (2, -4), (2, -3), (2, -2), (2, -1), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6),
         (2, 7), (2, 8), (3, -8), (3, -7), (3, -6), (3, -5), (3, -4), (3, -3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2),
         (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (4, -8), (4, -7), (4, -6), (4, -5), (4, -4), (4, -3), (4, -2),
         (4, -1), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (5, -7), (5, -6), (5, -5),
         (5, -4), (5, -3), (5, -2), (5, -1), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (6, -6),
         (6, -5), (6, -4), (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (7, -5),
         (7, -4), (7, -3), (7, -2), (7, -1), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (8, -4), (8, -3), (8, -2),
         (8, -1), (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (9, 0)]
        ,
        [(-10, 0), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 0), (-9, 1), (-9, 2), (-9, 3), (-9, 4), (-8, -6),
         (-8, -5), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1), (-8, 2), (-8, 3), (-8, 4), (-8, 5),
         (-8, 6), (-7, -7), (-7, -6), (-7, -5), (-7, -4), (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2),
         (-7, 3), (-7, 4), (-7, 5), (-7, 6), (-7, 7), (-6, -8), (-6, -7), (-6, -6), (-6, -5), (-6, -4), (-6, -3),
         (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3), (-6, 4), (-6, 5), (-6, 6), (-6, 7), (-6, 8), (-5, -8),
         (-5, -7), (-5, -6), (-5, -5), (-5, -4), (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3),
         (-5, 4), (-5, 5), (-5, 6), (-5, 7), (-5, 8), (-4, -9), (-4, -8), (-4, -7), (-4, -6), (-4, -5), (-4, -4),
         (-4, -3), (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5), (-4, 6), (-4, 7), (-4, 8),
         (-4, 9), (-3, -9), (-3, -8), (-3, -7), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2), (-3, -1), (-3, 0),
         (-3, 1), (-3, 2), (-3, 3), (-3, 4), (-3, 5), (-3, 6), (-3, 7), (-3, 8), (-3, 9), (-2, -9), (-2, -8), (-2, -7),
         (-2, -6), (-2, -5), (-2, -4), (-2, -3), (-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2), (-2, 3), (-2, 4),
         (-2, 5), (-2, 6), (-2, 7), (-2, 8), (-2, 9), (-1, -9), (-1, -8), (-1, -7), (-1, -6), (-1, -5), (-1, -4),
         (-1, -3), (-1, -2), (-1, -1), (-1, 1), (-1, 2), (-1, 3), (-1, 4), (-1, 5), (-1, 6), (-1, 7), (-1, 8), (-1, 9),
         (0, -10), (0, -9), (0, -8), (0, -7), (0, -6), (0, -5), (0, -4), (0, -3), (0, -2), (0, 2), (0, 3), (0, 4),
         (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10), (1, -9), (1, -8), (1, -7), (1, -6), (1, -5), (1, -4), (1, -3),
         (1, -2), (1, -1), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (2, -9), (2, -8),
         (2, -7), (2, -6), (2, -5), (2, -4), (2, -3), (2, -2), (2, -1), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5),
         (2, 6), (2, 7), (2, 8), (2, 9), (3, -9), (3, -8), (3, -7), (3, -6), (3, -5), (3, -4), (3, -3), (3, -2),
         (3, -1), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (4, -9), (4, -8),
         (4, -7), (4, -6), (4, -5), (4, -4), (4, -3), (4, -2), (4, -1), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5),
         (4, 6), (4, 7), (4, 8), (4, 9), (5, -8), (5, -7), (5, -6), (5, -5), (5, -4), (5, -3), (5, -2), (5, -1), (5, 0),
         (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (6, -8), (6, -7), (6, -6), (6, -5), (6, -4),
         (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8), (7, -7),
         (7, -6), (7, -5), (7, -4), (7, -3), (7, -2), (7, -1), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6),
         (7, 7), (8, -6), (8, -5), (8, -4), (8, -3), (8, -2), (8, -1), (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5),
         (8, 6), (9, -4), (9, -3), (9, -2), (9, -1), (9, 0), (9, 1), (9, 2), (9, 3), (9, 4), (10, 0)]
        ,
        [(-11, 0), (-10, -4), (-10, -3), (-10, -2), (-10, -1), (-10, 0), (-10, 1), (-10, 2), (-10, 3), (-10, 4),
         (-9, -6), (-9, -5), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 0), (-9, 1), (-9, 2), (-9, 3), (-9, 4),
         (-9, 5), (-9, 6), (-8, -7), (-8, -6), (-8, -5), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1),
         (-8, 2), (-8, 3), (-8, 4), (-8, 5), (-8, 6), (-8, 7), (-7, -8), (-7, -7), (-7, -6), (-7, -5), (-7, -4),
         (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2), (-7, 3), (-7, 4), (-7, 5), (-7, 6), (-7, 7), (-7, 8),
         (-6, -9), (-6, -8), (-6, -7), (-6, -6), (-6, -5), (-6, -4), (-6, -3), (-6, -2), (-6, -1), (-6, 0), (-6, 1),
         (-6, 2), (-6, 3), (-6, 4), (-6, 5), (-6, 6), (-6, 7), (-6, 8), (-6, 9), (-5, -9), (-5, -8), (-5, -7), (-5, -6),
         (-5, -5), (-5, -4), (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3), (-5, 4), (-5, 5),
         (-5, 6), (-5, 7), (-5, 8), (-5, 9), (-4, -10), (-4, -9), (-4, -8), (-4, -7), (-4, -6), (-4, -5), (-4, -4),
         (-4, -3), (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5), (-4, 6), (-4, 7), (-4, 8),
         (-4, 9), (-4, 10), (-3, -10), (-3, -9), (-3, -8), (-3, -7), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2),
         (-3, -1), (-3, 0), (-3, 1), (-3, 2), (-3, 3), (-3, 4), (-3, 5), (-3, 6), (-3, 7), (-3, 8), (-3, 9), (-3, 10),
         (-2, -10), (-2, -9), (-2, -8), (-2, -7), (-2, -6), (-2, -5), (-2, -4), (-2, -3), (-2, -2), (-2, -1), (-2, 0),
         (-2, 1), (-2, 2), (-2, 3), (-2, 4), (-2, 5), (-2, 6), (-2, 7), (-2, 8), (-2, 9), (-2, 10), (-1, -10), (-1, -9),
         (-1, -8), (-1, -7), (-1, -6), (-1, -5), (-1, -4), (-1, -3), (-1, -2), (-1, -1), (-1, 1), (-1, 2), (-1, 3),
         (-1, 4), (-1, 5), (-1, 6), (-1, 7), (-1, 8), (-1, 9), (-1, 10), (0, -11), (0, -10), (0, -9), (0, -8), (0, -7),
         (0, -6), (0, -5), (0, -4), (0, -3), (0, -2), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9),
         (0, 10), (0, 11), (1, -10), (1, -9), (1, -8), (1, -7), (1, -6), (1, -5), (1, -4), (1, -3), (1, -2), (1, -1),
         (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10), (2, -10), (2, -9), (2, -8),
         (2, -7), (2, -6), (2, -5), (2, -4), (2, -3), (2, -2), (2, -1), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5),
         (2, 6), (2, 7), (2, 8), (2, 9), (2, 10), (3, -10), (3, -9), (3, -8), (3, -7), (3, -6), (3, -5), (3, -4),
         (3, -3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9),
         (3, 10), (4, -10), (4, -9), (4, -8), (4, -7), (4, -6), (4, -5), (4, -4), (4, -3), (4, -2), (4, -1), (4, 0),
         (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9), (4, 10), (5, -9), (5, -8), (5, -7),
         (5, -6), (5, -5), (5, -4), (5, -3), (5, -2), (5, -1), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6),
         (5, 7), (5, 8), (5, 9), (6, -9), (6, -8), (6, -7), (6, -6), (6, -5), (6, -4), (6, -3), (6, -2), (6, -1),
         (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8), (6, 9), (7, -8), (7, -7), (7, -6),
         (7, -5), (7, -4), (7, -3), (7, -2), (7, -1), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7),
         (7, 8), (8, -7), (8, -6), (8, -5), (8, -4), (8, -3), (8, -2), (8, -1), (8, 0), (8, 1), (8, 2), (8, 3), (8, 4),
         (8, 5), (8, 6), (8, 7), (9, -6), (9, -5), (9, -4), (9, -3), (9, -2), (9, -1), (9, 0), (9, 1), (9, 2), (9, 3),
         (9, 4), (9, 5), (9, 6), (10, -4), (10, -3), (10, -2), (10, -1), (10, 0), (10, 1), (10, 2), (10, 3), (10, 4),
         (11, 0)]
        ,
        [(-12, 0), (-11, -4), (-11, -3), (-11, -2), (-11, -1), (-11, 0), (-11, 1), (-11, 2), (-11, 3), (-11, 4),
         (-10, -6), (-10, -5), (-10, -4), (-10, -3), (-10, -2), (-10, -1), (-10, 0), (-10, 1), (-10, 2), (-10, 3),
         (-10, 4), (-10, 5), (-10, 6), (-9, -7), (-9, -6), (-9, -5), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 0),
         (-9, 1), (-9, 2), (-9, 3), (-9, 4), (-9, 5), (-9, 6), (-9, 7), (-8, -8), (-8, -7), (-8, -6), (-8, -5),
         (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1), (-8, 2), (-8, 3), (-8, 4), (-8, 5), (-8, 6), (-8, 7),
         (-8, 8), (-7, -9), (-7, -8), (-7, -7), (-7, -6), (-7, -5), (-7, -4), (-7, -3), (-7, -2), (-7, -1), (-7, 0),
         (-7, 1), (-7, 2), (-7, 3), (-7, 4), (-7, 5), (-7, 6), (-7, 7), (-7, 8), (-7, 9), (-6, -10), (-6, -9), (-6, -8),
         (-6, -7), (-6, -6), (-6, -5), (-6, -4), (-6, -3), (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3),
         (-6, 4), (-6, 5), (-6, 6), (-6, 7), (-6, 8), (-6, 9), (-6, 10), (-5, -10), (-5, -9), (-5, -8), (-5, -7),
         (-5, -6), (-5, -5), (-5, -4), (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3), (-5, 4),
         (-5, 5), (-5, 6), (-5, 7), (-5, 8), (-5, 9), (-5, 10), (-4, -11), (-4, -10), (-4, -9), (-4, -8), (-4, -7),
         (-4, -6), (-4, -5), (-4, -4), (-4, -3), (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4),
         (-4, 5), (-4, 6), (-4, 7), (-4, 8), (-4, 9), (-4, 10), (-4, 11), (-3, -11), (-3, -10), (-3, -9), (-3, -8),
         (-3, -7), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2), (-3, -1), (-3, 0), (-3, 1), (-3, 2), (-3, 3),
         (-3, 4), (-3, 5), (-3, 6), (-3, 7), (-3, 8), (-3, 9), (-3, 10), (-3, 11), (-2, -11), (-2, -10), (-2, -9),
         (-2, -8), (-2, -7), (-2, -6), (-2, -5), (-2, -4), (-2, -3), (-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2),
         (-2, 3), (-2, 4), (-2, 5), (-2, 6), (-2, 7), (-2, 8), (-2, 9), (-2, 10), (-2, 11), (-1, -11), (-1, -10),
         (-1, -9), (-1, -8), (-1, -7), (-1, -6), (-1, -5), (-1, -4), (-1, -3), (-1, -2), (-1, -1), (-1, 1), (-1, 2),
         (-1, 3), (-1, 4), (-1, 5), (-1, 6), (-1, 7), (-1, 8), (-1, 9), (-1, 10), (-1, 11), (0, -12), (0, -11),
         (0, -10), (0, -9), (0, -8), (0, -7), (0, -6), (0, -5), (0, -4), (0, -3), (0, -2), (0, 2), (0, 3), (0, 4),
         (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10), (0, 11), (0, 12), (1, -11), (1, -10), (1, -9), (1, -8),
         (1, -7), (1, -6), (1, -5), (1, -4), (1, -3), (1, -2), (1, -1), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6),
         (1, 7), (1, 8), (1, 9), (1, 10), (1, 11), (2, -11), (2, -10), (2, -9), (2, -8), (2, -7), (2, -6), (2, -5),
         (2, -4), (2, -3), (2, -2), (2, -1), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8),
         (2, 9), (2, 10), (2, 11), (3, -11), (3, -10), (3, -9), (3, -8), (3, -7), (3, -6), (3, -5), (3, -4), (3, -3),
         (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (3, 10),
         (3, 11), (4, -11), (4, -10), (4, -9), (4, -8), (4, -7), (4, -6), (4, -5), (4, -4), (4, -3), (4, -2), (4, -1),
         (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9), (4, 10), (4, 11), (5, -10),
         (5, -9), (5, -8), (5, -7), (5, -6), (5, -5), (5, -4), (5, -3), (5, -2), (5, -1), (5, 0), (5, 1), (5, 2),
         (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (5, 9), (5, 10), (6, -10), (6, -9), (6, -8), (6, -7), (6, -6),
         (6, -5), (6, -4), (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7),
         (6, 8), (6, 9), (6, 10), (7, -9), (7, -8), (7, -7), (7, -6), (7, -5), (7, -4), (7, -3), (7, -2), (7, -1),
         (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (7, 8), (7, 9), (8, -8), (8, -7), (8, -6),
         (8, -5), (8, -4), (8, -3), (8, -2), (8, -1), (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7),
         (8, 8), (9, -7), (9, -6), (9, -5), (9, -4), (9, -3), (9, -2), (9, -1), (9, 0), (9, 1), (9, 2), (9, 3), (9, 4),
         (9, 5), (9, 6), (9, 7), (10, -6), (10, -5), (10, -4), (10, -3), (10, -2), (10, -1), (10, 0), (10, 1), (10, 2),
         (10, 3), (10, 4), (10, 5), (10, 6), (11, -4), (11, -3), (11, -2), (11, -1), (11, 0), (11, 1), (11, 2), (11, 3),
         (11, 4), (12, 0)]

    ],
    [
        [],
        [],
        [],
        [(-3, 0), (-2, -2), (-2, -1), (-2, 1), (-2, 2), (-1, -2), (-1, 2), (0, -3), (0, 3), (1, -2), (1, 2), (2, -2),
         (2, -1), (2, 1), (2, 2), (3, 0)]
        ,
        [(-4, 0), (-3, -2), (-3, -1), (-3, 0), (-3, 1), (-3, 2), (-2, -3), (-2, -2), (-2, -1), (-2, 1), (-2, 2),
         (-2, 3), (-1, -3), (-1, -2), (-1, 2), (-1, 3), (0, -4), (0, -3), (0, 3), (0, 4), (1, -3), (1, -2), (1, 2),
         (1, 3), (2, -3), (2, -2), (2, -1), (2, 1), (2, 2), (2, 3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (4, 0)]
        ,
        [(-5, 0), (-4, -3), (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-3, -4), (-3, -3), (-3, -2),
         (-3, -1), (-3, 0), (-3, 1), (-3, 2), (-3, 3), (-3, 4), (-2, -4), (-2, -3), (-2, -2), (-2, -1), (-2, 1),
         (-2, 2), (-2, 3), (-2, 4), (-1, -4), (-1, -3), (-1, -2), (-1, 2), (-1, 3), (-1, 4), (0, -5), (0, -4), (0, -3),
         (0, 3), (0, 4), (0, 5), (1, -4), (1, -3), (1, -2), (1, 2), (1, 3), (1, 4), (2, -4), (2, -3), (2, -2), (2, -1),
         (2, 1), (2, 2), (2, 3), (2, 4), (3, -4), (3, -3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4),
         (4, -3), (4, -2), (4, -1), (4, 0), (4, 1), (4, 2), (4, 3), (5, 0)]
        ,
        [(-6, 0), (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3), (-4, -4), (-4, -3), (-4, -2),
         (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-3, -5), (-3, -4), (-3, -3), (-3, -2), (-3, -1),
         (-3, 0), (-3, 1), (-3, 2), (-3, 3), (-3, 4), (-3, 5), (-2, -5), (-2, -4), (-2, -3), (-2, -2), (-2, -1),
         (-2, 1), (-2, 2), (-2, 3), (-2, 4), (-2, 5), (-1, -5), (-1, -4), (-1, -3), (-1, -2), (-1, 2), (-1, 3), (-1, 4),
         (-1, 5), (0, -6), (0, -5), (0, -4), (0, -3), (0, 3), (0, 4), (0, 5), (0, 6), (1, -5), (1, -4), (1, -3),
         (1, -2), (1, 2), (1, 3), (1, 4), (1, 5), (2, -5), (2, -4), (2, -3), (2, -2), (2, -1), (2, 1), (2, 2), (2, 3),
         (2, 4), (2, 5), (3, -5), (3, -4), (3, -3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5),
         (4, -4), (4, -3), (4, -2), (4, -1), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (5, -3), (5, -2), (5, -1), (5, 0),
         (5, 1), (5, 2), (5, 3), (6, 0)]
        ,
        [(-7, 0), (-6, -3), (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3), (-5, -4), (-5, -3), (-5, -2),
         (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3), (-5, 4), (-4, -5), (-4, -4), (-4, -3), (-4, -2), (-4, -1),
         (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2),
         (-3, -1), (-3, 0), (-3, 1), (-3, 2), (-3, 3), (-3, 4), (-3, 5), (-3, 6), (-2, -6), (-2, -5), (-2, -4),
         (-2, -3), (-2, -2), (-2, -1), (-2, 1), (-2, 2), (-2, 3), (-2, 4), (-2, 5), (-2, 6), (-1, -6), (-1, -5),
         (-1, -4), (-1, -3), (-1, -2), (-1, 2), (-1, 3), (-1, 4), (-1, 5), (-1, 6), (0, -7), (0, -6), (0, -5), (0, -4),
         (0, -3), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (1, -6), (1, -5), (1, -4), (1, -3), (1, -2), (1, 2), (1, 3),
         (1, 4), (1, 5), (1, 6), (2, -6), (2, -5), (2, -4), (2, -3), (2, -2), (2, -1), (2, 1), (2, 2), (2, 3), (2, 4),
         (2, 5), (2, 6), (3, -6), (3, -5), (3, -4), (3, -3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4),
         (3, 5), (3, 6), (4, -5), (4, -4), (4, -3), (4, -2), (4, -1), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5),
         (5, -4), (5, -3), (5, -2), (5, -1), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (6, -3), (6, -2), (6, -1), (6, 0),
         (6, 1), (6, 2), (6, 3), (7, 0)]
        ,
        [(-8, 0), (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2), (-7, 3), (-6, -5), (-6, -4), (-6, -3),
         (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3), (-6, 4), (-6, 5), (-5, -6), (-5, -5), (-5, -4),
         (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3), (-5, 4), (-5, 5), (-5, 6), (-4, -6),
         (-4, -5), (-4, -4), (-4, -3), (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5),
         (-4, 6), (-3, -7), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2), (-3, -1), (-3, 0), (-3, 1), (-3, 2),
         (-3, 3), (-3, 4), (-3, 5), (-3, 6), (-3, 7), (-2, -7), (-2, -6), (-2, -5), (-2, -4), (-2, -3), (-2, -2),
         (-2, -1), (-2, 1), (-2, 2), (-2, 3), (-2, 4), (-2, 5), (-2, 6), (-2, 7), (-1, -7), (-1, -6), (-1, -5),
         (-1, -4), (-1, -3), (-1, -2), (-1, 2), (-1, 3), (-1, 4), (-1, 5), (-1, 6), (-1, 7), (0, -8), (0, -7), (0, -6),
         (0, -5), (0, -4), (0, -3), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (1, -7), (1, -6), (1, -5), (1, -4),
         (1, -3), (1, -2), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (2, -7), (2, -6), (2, -5), (2, -4), (2, -3),
         (2, -2), (2, -1), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (3, -7), (3, -6), (3, -5), (3, -4),
         (3, -3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (4, -6), (4, -5),
         (4, -4), (4, -3), (4, -2), (4, -1), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (5, -6), (5, -5),
         (5, -4), (5, -3), (5, -2), (5, -1), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (6, -5), (6, -4),
         (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (7, -3), (7, -2), (7, -1), (7, 0),
         (7, 1), (7, 2), (7, 3), (8, 0)]
        ,
        [(-9, 0), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1), (-8, 2), (-8, 3), (-8, 4), (-7, -5),
         (-7, -4), (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2), (-7, 3), (-7, 4), (-7, 5), (-6, -6),
         (-6, -5), (-6, -4), (-6, -3), (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3), (-6, 4), (-6, 5),
         (-6, 6), (-5, -7), (-5, -6), (-5, -5), (-5, -4), (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2),
         (-5, 3), (-5, 4), (-5, 5), (-5, 6), (-5, 7), (-4, -8), (-4, -7), (-4, -6), (-4, -5), (-4, -4), (-4, -3),
         (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5), (-4, 6), (-4, 7), (-4, 8), (-3, -8),
         (-3, -7), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2), (-3, -1), (-3, 0), (-3, 1), (-3, 2), (-3, 3),
         (-3, 4), (-3, 5), (-3, 6), (-3, 7), (-3, 8), (-2, -8), (-2, -7), (-2, -6), (-2, -5), (-2, -4), (-2, -3),
         (-2, -2), (-2, -1), (-2, 1), (-2, 2), (-2, 3), (-2, 4), (-2, 5), (-2, 6), (-2, 7), (-2, 8), (-1, -8), (-1, -7),
         (-1, -6), (-1, -5), (-1, -4), (-1, -3), (-1, -2), (-1, 2), (-1, 3), (-1, 4), (-1, 5), (-1, 6), (-1, 7),
         (-1, 8), (0, -9), (0, -8), (0, -7), (0, -6), (0, -5), (0, -4), (0, -3), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7),
         (0, 8), (0, 9), (1, -8), (1, -7), (1, -6), (1, -5), (1, -4), (1, -3), (1, -2), (1, 2), (1, 3), (1, 4), (1, 5),
         (1, 6), (1, 7), (1, 8), (2, -8), (2, -7), (2, -6), (2, -5), (2, -4), (2, -3), (2, -2), (2, -1), (2, 1), (2, 2),
         (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (3, -8), (3, -7), (3, -6), (3, -5), (3, -4), (3, -3), (3, -2),
         (3, -1), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (4, -8), (4, -7), (4, -6),
         (4, -5), (4, -4), (4, -3), (4, -2), (4, -1), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7),
         (4, 8), (5, -7), (5, -6), (5, -5), (5, -4), (5, -3), (5, -2), (5, -1), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4),
         (5, 5), (5, 6), (5, 7), (6, -6), (6, -5), (6, -4), (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2), (6, 3),
         (6, 4), (6, 5), (6, 6), (7, -5), (7, -4), (7, -3), (7, -2), (7, -1), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4),
         (7, 5), (8, -4), (8, -3), (8, -2), (8, -1), (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (9, 0)]
        ,
        [(-10, 0), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 0), (-9, 1), (-9, 2), (-9, 3), (-9, 4), (-8, -6),
         (-8, -5), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1), (-8, 2), (-8, 3), (-8, 4), (-8, 5),
         (-8, 6), (-7, -7), (-7, -6), (-7, -5), (-7, -4), (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2),
         (-7, 3), (-7, 4), (-7, 5), (-7, 6), (-7, 7), (-6, -8), (-6, -7), (-6, -6), (-6, -5), (-6, -4), (-6, -3),
         (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3), (-6, 4), (-6, 5), (-6, 6), (-6, 7), (-6, 8), (-5, -8),
         (-5, -7), (-5, -6), (-5, -5), (-5, -4), (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3),
         (-5, 4), (-5, 5), (-5, 6), (-5, 7), (-5, 8), (-4, -9), (-4, -8), (-4, -7), (-4, -6), (-4, -5), (-4, -4),
         (-4, -3), (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5), (-4, 6), (-4, 7), (-4, 8),
         (-4, 9), (-3, -9), (-3, -8), (-3, -7), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2), (-3, -1), (-3, 0),
         (-3, 1), (-3, 2), (-3, 3), (-3, 4), (-3, 5), (-3, 6), (-3, 7), (-3, 8), (-3, 9), (-2, -9), (-2, -8), (-2, -7),
         (-2, -6), (-2, -5), (-2, -4), (-2, -3), (-2, -2), (-2, -1), (-2, 1), (-2, 2), (-2, 3), (-2, 4), (-2, 5),
         (-2, 6), (-2, 7), (-2, 8), (-2, 9), (-1, -9), (-1, -8), (-1, -7), (-1, -6), (-1, -5), (-1, -4), (-1, -3),
         (-1, -2), (-1, 2), (-1, 3), (-1, 4), (-1, 5), (-1, 6), (-1, 7), (-1, 8), (-1, 9), (0, -10), (0, -9), (0, -8),
         (0, -7), (0, -6), (0, -5), (0, -4), (0, -3), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10),
         (1, -9), (1, -8), (1, -7), (1, -6), (1, -5), (1, -4), (1, -3), (1, -2), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6),
         (1, 7), (1, 8), (1, 9), (2, -9), (2, -8), (2, -7), (2, -6), (2, -5), (2, -4), (2, -3), (2, -2), (2, -1),
         (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (3, -9), (3, -8), (3, -7), (3, -6),
         (3, -5), (3, -4), (3, -3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7),
         (3, 8), (3, 9), (4, -9), (4, -8), (4, -7), (4, -6), (4, -5), (4, -4), (4, -3), (4, -2), (4, -1), (4, 0),
         (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9), (5, -8), (5, -7), (5, -6), (5, -5),
         (5, -4), (5, -3), (5, -2), (5, -1), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8),
         (6, -8), (6, -7), (6, -6), (6, -5), (6, -4), (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4),
         (6, 5), (6, 6), (6, 7), (6, 8), (7, -7), (7, -6), (7, -5), (7, -4), (7, -3), (7, -2), (7, -1), (7, 0), (7, 1),
         (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (8, -6), (8, -5), (8, -4), (8, -3), (8, -2), (8, -1), (8, 0),
         (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (9, -4), (9, -3), (9, -2), (9, -1), (9, 0), (9, 1), (9, 2),
         (9, 3), (9, 4), (10, 0)]
        ,
        [(-11, 0), (-10, -4), (-10, -3), (-10, -2), (-10, -1), (-10, 0), (-10, 1), (-10, 2), (-10, 3), (-10, 4),
         (-9, -6), (-9, -5), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 0), (-9, 1), (-9, 2), (-9, 3), (-9, 4),
         (-9, 5), (-9, 6), (-8, -7), (-8, -6), (-8, -5), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1),
         (-8, 2), (-8, 3), (-8, 4), (-8, 5), (-8, 6), (-8, 7), (-7, -8), (-7, -7), (-7, -6), (-7, -5), (-7, -4),
         (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2), (-7, 3), (-7, 4), (-7, 5), (-7, 6), (-7, 7), (-7, 8),
         (-6, -9), (-6, -8), (-6, -7), (-6, -6), (-6, -5), (-6, -4), (-6, -3), (-6, -2), (-6, -1), (-6, 0), (-6, 1),
         (-6, 2), (-6, 3), (-6, 4), (-6, 5), (-6, 6), (-6, 7), (-6, 8), (-6, 9), (-5, -9), (-5, -8), (-5, -7), (-5, -6),
         (-5, -5), (-5, -4), (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3), (-5, 4), (-5, 5),
         (-5, 6), (-5, 7), (-5, 8), (-5, 9), (-4, -10), (-4, -9), (-4, -8), (-4, -7), (-4, -6), (-4, -5), (-4, -4),
         (-4, -3), (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5), (-4, 6), (-4, 7), (-4, 8),
         (-4, 9), (-4, 10), (-3, -10), (-3, -9), (-3, -8), (-3, -7), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2),
         (-3, -1), (-3, 0), (-3, 1), (-3, 2), (-3, 3), (-3, 4), (-3, 5), (-3, 6), (-3, 7), (-3, 8), (-3, 9), (-3, 10),
         (-2, -10), (-2, -9), (-2, -8), (-2, -7), (-2, -6), (-2, -5), (-2, -4), (-2, -3), (-2, -2), (-2, -1), (-2, 1),
         (-2, 2), (-2, 3), (-2, 4), (-2, 5), (-2, 6), (-2, 7), (-2, 8), (-2, 9), (-2, 10), (-1, -10), (-1, -9),
         (-1, -8), (-1, -7), (-1, -6), (-1, -5), (-1, -4), (-1, -3), (-1, -2), (-1, 2), (-1, 3), (-1, 4), (-1, 5),
         (-1, 6), (-1, 7), (-1, 8), (-1, 9), (-1, 10), (0, -11), (0, -10), (0, -9), (0, -8), (0, -7), (0, -6), (0, -5),
         (0, -4), (0, -3), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10), (0, 11), (1, -10), (1, -9),
         (1, -8), (1, -7), (1, -6), (1, -5), (1, -4), (1, -3), (1, -2), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7),
         (1, 8), (1, 9), (1, 10), (2, -10), (2, -9), (2, -8), (2, -7), (2, -6), (2, -5), (2, -4), (2, -3), (2, -2),
         (2, -1), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (2, 10), (3, -10), (3, -9),
         (3, -8), (3, -7), (3, -6), (3, -5), (3, -4), (3, -3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4),
         (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (3, 10), (4, -10), (4, -9), (4, -8), (4, -7), (4, -6), (4, -5),
         (4, -4), (4, -3), (4, -2), (4, -1), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8),
         (4, 9), (4, 10), (5, -9), (5, -8), (5, -7), (5, -6), (5, -5), (5, -4), (5, -3), (5, -2), (5, -1), (5, 0),
         (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (5, 9), (6, -9), (6, -8), (6, -7), (6, -6),
         (6, -5), (6, -4), (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7),
         (6, 8), (6, 9), (7, -8), (7, -7), (7, -6), (7, -5), (7, -4), (7, -3), (7, -2), (7, -1), (7, 0), (7, 1), (7, 2),
         (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (7, 8), (8, -7), (8, -6), (8, -5), (8, -4), (8, -3), (8, -2), (8, -1),
         (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (9, -6), (9, -5), (9, -4), (9, -3), (9, -2),
         (9, -1), (9, 0), (9, 1), (9, 2), (9, 3), (9, 4), (9, 5), (9, 6), (10, -4), (10, -3), (10, -2), (10, -1),
         (10, 0), (10, 1), (10, 2), (10, 3), (10, 4), (11, 0)]
        ,
        [(-12, 0), (-11, -4), (-11, -3), (-11, -2), (-11, -1), (-11, 0), (-11, 1), (-11, 2), (-11, 3), (-11, 4),
         (-10, -6), (-10, -5), (-10, -4), (-10, -3), (-10, -2), (-10, -1), (-10, 0), (-10, 1), (-10, 2), (-10, 3),
         (-10, 4), (-10, 5), (-10, 6), (-9, -7), (-9, -6), (-9, -5), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 0),
         (-9, 1), (-9, 2), (-9, 3), (-9, 4), (-9, 5), (-9, 6), (-9, 7), (-8, -8), (-8, -7), (-8, -6), (-8, -5),
         (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1), (-8, 2), (-8, 3), (-8, 4), (-8, 5), (-8, 6), (-8, 7),
         (-8, 8), (-7, -9), (-7, -8), (-7, -7), (-7, -6), (-7, -5), (-7, -4), (-7, -3), (-7, -2), (-7, -1), (-7, 0),
         (-7, 1), (-7, 2), (-7, 3), (-7, 4), (-7, 5), (-7, 6), (-7, 7), (-7, 8), (-7, 9), (-6, -10), (-6, -9), (-6, -8),
         (-6, -7), (-6, -6), (-6, -5), (-6, -4), (-6, -3), (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3),
         (-6, 4), (-6, 5), (-6, 6), (-6, 7), (-6, 8), (-6, 9), (-6, 10), (-5, -10), (-5, -9), (-5, -8), (-5, -7),
         (-5, -6), (-5, -5), (-5, -4), (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3), (-5, 4),
         (-5, 5), (-5, 6), (-5, 7), (-5, 8), (-5, 9), (-5, 10), (-4, -11), (-4, -10), (-4, -9), (-4, -8), (-4, -7),
         (-4, -6), (-4, -5), (-4, -4), (-4, -3), (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4),
         (-4, 5), (-4, 6), (-4, 7), (-4, 8), (-4, 9), (-4, 10), (-4, 11), (-3, -11), (-3, -10), (-3, -9), (-3, -8),
         (-3, -7), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2), (-3, -1), (-3, 0), (-3, 1), (-3, 2), (-3, 3),
         (-3, 4), (-3, 5), (-3, 6), (-3, 7), (-3, 8), (-3, 9), (-3, 10), (-3, 11), (-2, -11), (-2, -10), (-2, -9),
         (-2, -8), (-2, -7), (-2, -6), (-2, -5), (-2, -4), (-2, -3), (-2, -2), (-2, -1), (-2, 1), (-2, 2), (-2, 3),
         (-2, 4), (-2, 5), (-2, 6), (-2, 7), (-2, 8), (-2, 9), (-2, 10), (-2, 11), (-1, -11), (-1, -10), (-1, -9),
         (-1, -8), (-1, -7), (-1, -6), (-1, -5), (-1, -4), (-1, -3), (-1, -2), (-1, 2), (-1, 3), (-1, 4), (-1, 5),
         (-1, 6), (-1, 7), (-1, 8), (-1, 9), (-1, 10), (-1, 11), (0, -12), (0, -11), (0, -10), (0, -9), (0, -8),
         (0, -7), (0, -6), (0, -5), (0, -4), (0, -3), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10),
         (0, 11), (0, 12), (1, -11), (1, -10), (1, -9), (1, -8), (1, -7), (1, -6), (1, -5), (1, -4), (1, -3), (1, -2),
         (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10), (1, 11), (2, -11), (2, -10), (2, -9),
         (2, -8), (2, -7), (2, -6), (2, -5), (2, -4), (2, -3), (2, -2), (2, -1), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5),
         (2, 6), (2, 7), (2, 8), (2, 9), (2, 10), (2, 11), (3, -11), (3, -10), (3, -9), (3, -8), (3, -7), (3, -6),
         (3, -5), (3, -4), (3, -3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7),
         (3, 8), (3, 9), (3, 10), (3, 11), (4, -11), (4, -10), (4, -9), (4, -8), (4, -7), (4, -6), (4, -5), (4, -4),
         (4, -3), (4, -2), (4, -1), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9),
         (4, 10), (4, 11), (5, -10), (5, -9), (5, -8), (5, -7), (5, -6), (5, -5), (5, -4), (5, -3), (5, -2), (5, -1),
         (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (5, 9), (5, 10), (6, -10), (6, -9),
         (6, -8), (6, -7), (6, -6), (6, -5), (6, -4), (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4),
         (6, 5), (6, 6), (6, 7), (6, 8), (6, 9), (6, 10), (7, -9), (7, -8), (7, -7), (7, -6), (7, -5), (7, -4), (7, -3),
         (7, -2), (7, -1), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (7, 8), (7, 9), (8, -8),
         (8, -7), (8, -6), (8, -5), (8, -4), (8, -3), (8, -2), (8, -1), (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5),
         (8, 6), (8, 7), (8, 8), (9, -7), (9, -6), (9, -5), (9, -4), (9, -3), (9, -2), (9, -1), (9, 0), (9, 1), (9, 2),
         (9, 3), (9, 4), (9, 5), (9, 6), (9, 7), (10, -6), (10, -5), (10, -4), (10, -3), (10, -2), (10, -1), (10, 0),
         (10, 1), (10, 2), (10, 3), (10, 4), (10, 5), (10, 6), (11, -4), (11, -3), (11, -2), (11, -1), (11, 0), (11, 1),
         (11, 2), (11, 3), (11, 4), (12, 0)]

    ],
    [
        [],
        [],
        [],
        [],
        [(-4, 0), (-3, -2), (-3, -1), (-3, 1), (-3, 2), (-2, -3), (-2, 3), (-1, -3), (-1, 3), (0, -4), (0, 4), (1, -3),
         (1, 3), (2, -3), (2, 3), (3, -2), (3, -1), (3, 1), (3, 2), (4, 0)]
        ,
        [(-5, 0), (-4, -3), (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-3, -4), (-3, -3), (-3, -2),
         (-3, -1), (-3, 1), (-3, 2), (-3, 3), (-3, 4), (-2, -4), (-2, -3), (-2, 3), (-2, 4), (-1, -4), (-1, -3),
         (-1, 3), (-1, 4), (0, -5), (0, -4), (0, 4), (0, 5), (1, -4), (1, -3), (1, 3), (1, 4), (2, -4), (2, -3), (2, 3),
         (2, 4), (3, -4), (3, -3), (3, -2), (3, -1), (3, 1), (3, 2), (3, 3), (3, 4), (4, -3), (4, -2), (4, -1), (4, 0),
         (4, 1), (4, 2), (4, 3), (5, 0)]
        ,
        [(-6, 0), (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3), (-4, -4), (-4, -3), (-4, -2),
         (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-3, -5), (-3, -4), (-3, -3), (-3, -2), (-3, -1),
         (-3, 1), (-3, 2), (-3, 3), (-3, 4), (-3, 5), (-2, -5), (-2, -4), (-2, -3), (-2, 3), (-2, 4), (-2, 5), (-1, -5),
         (-1, -4), (-1, -3), (-1, 3), (-1, 4), (-1, 5), (0, -6), (0, -5), (0, -4), (0, 4), (0, 5), (0, 6), (1, -5),
         (1, -4), (1, -3), (1, 3), (1, 4), (1, 5), (2, -5), (2, -4), (2, -3), (2, 3), (2, 4), (2, 5), (3, -5), (3, -4),
         (3, -3), (3, -2), (3, -1), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (4, -4), (4, -3), (4, -2), (4, -1), (4, 0),
         (4, 1), (4, 2), (4, 3), (4, 4), (5, -3), (5, -2), (5, -1), (5, 0), (5, 1), (5, 2), (5, 3), (6, 0)]
        ,
        [(-7, 0), (-6, -3), (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3), (-5, -4), (-5, -3), (-5, -2),
         (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3), (-5, 4), (-4, -5), (-4, -4), (-4, -3), (-4, -2), (-4, -1),
         (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2),
         (-3, -1), (-3, 1), (-3, 2), (-3, 3), (-3, 4), (-3, 5), (-3, 6), (-2, -6), (-2, -5), (-2, -4), (-2, -3),
         (-2, 3), (-2, 4), (-2, 5), (-2, 6), (-1, -6), (-1, -5), (-1, -4), (-1, -3), (-1, 3), (-1, 4), (-1, 5), (-1, 6),
         (0, -7), (0, -6), (0, -5), (0, -4), (0, 4), (0, 5), (0, 6), (0, 7), (1, -6), (1, -5), (1, -4), (1, -3), (1, 3),
         (1, 4), (1, 5), (1, 6), (2, -6), (2, -5), (2, -4), (2, -3), (2, 3), (2, 4), (2, 5), (2, 6), (3, -6), (3, -5),
         (3, -4), (3, -3), (3, -2), (3, -1), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (4, -5), (4, -4), (4, -3),
         (4, -2), (4, -1), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (5, -4), (5, -3), (5, -2), (5, -1), (5, 0),
         (5, 1), (5, 2), (5, 3), (5, 4), (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (7, 0)]
        ,
        [(-8, 0), (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2), (-7, 3), (-6, -5), (-6, -4), (-6, -3),
         (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3), (-6, 4), (-6, 5), (-5, -6), (-5, -5), (-5, -4),
         (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3), (-5, 4), (-5, 5), (-5, 6), (-4, -6),
         (-4, -5), (-4, -4), (-4, -3), (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5),
         (-4, 6), (-3, -7), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2), (-3, -1), (-3, 1), (-3, 2), (-3, 3),
         (-3, 4), (-3, 5), (-3, 6), (-3, 7), (-2, -7), (-2, -6), (-2, -5), (-2, -4), (-2, -3), (-2, 3), (-2, 4),
         (-2, 5), (-2, 6), (-2, 7), (-1, -7), (-1, -6), (-1, -5), (-1, -4), (-1, -3), (-1, 3), (-1, 4), (-1, 5),
         (-1, 6), (-1, 7), (0, -8), (0, -7), (0, -6), (0, -5), (0, -4), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (1, -7),
         (1, -6), (1, -5), (1, -4), (1, -3), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (2, -7), (2, -6), (2, -5), (2, -4),
         (2, -3), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (3, -7), (3, -6), (3, -5), (3, -4), (3, -3), (3, -2), (3, -1),
         (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (4, -6), (4, -5), (4, -4), (4, -3), (4, -2), (4, -1),
         (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (5, -6), (5, -5), (5, -4), (5, -3), (5, -2), (5, -1),
         (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (6, -5), (6, -4), (6, -3), (6, -2), (6, -1), (6, 0),
         (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (7, -3), (7, -2), (7, -1), (7, 0), (7, 1), (7, 2), (7, 3), (8, 0)]
        ,
        [(-9, 0), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1), (-8, 2), (-8, 3), (-8, 4), (-7, -5),
         (-7, -4), (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2), (-7, 3), (-7, 4), (-7, 5), (-6, -6),
         (-6, -5), (-6, -4), (-6, -3), (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3), (-6, 4), (-6, 5),
         (-6, 6), (-5, -7), (-5, -6), (-5, -5), (-5, -4), (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2),
         (-5, 3), (-5, 4), (-5, 5), (-5, 6), (-5, 7), (-4, -8), (-4, -7), (-4, -6), (-4, -5), (-4, -4), (-4, -3),
         (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5), (-4, 6), (-4, 7), (-4, 8), (-3, -8),
         (-3, -7), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2), (-3, -1), (-3, 1), (-3, 2), (-3, 3), (-3, 4),
         (-3, 5), (-3, 6), (-3, 7), (-3, 8), (-2, -8), (-2, -7), (-2, -6), (-2, -5), (-2, -4), (-2, -3), (-2, 3),
         (-2, 4), (-2, 5), (-2, 6), (-2, 7), (-2, 8), (-1, -8), (-1, -7), (-1, -6), (-1, -5), (-1, -4), (-1, -3),
         (-1, 3), (-1, 4), (-1, 5), (-1, 6), (-1, 7), (-1, 8), (0, -9), (0, -8), (0, -7), (0, -6), (0, -5), (0, -4),
         (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (1, -8), (1, -7), (1, -6), (1, -5), (1, -4), (1, -3), (1, 3),
         (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (2, -8), (2, -7), (2, -6), (2, -5), (2, -4), (2, -3), (2, 3), (2, 4),
         (2, 5), (2, 6), (2, 7), (2, 8), (3, -8), (3, -7), (3, -6), (3, -5), (3, -4), (3, -3), (3, -2), (3, -1), (3, 1),
         (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (4, -8), (4, -7), (4, -6), (4, -5), (4, -4), (4, -3),
         (4, -2), (4, -1), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (5, -7), (5, -6),
         (5, -5), (5, -4), (5, -3), (5, -2), (5, -1), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7),
         (6, -6), (6, -5), (6, -4), (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6),
         (7, -5), (7, -4), (7, -3), (7, -2), (7, -1), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (8, -4), (8, -3),
         (8, -2), (8, -1), (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (9, 0)]
        ,
        [(-10, 0), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 0), (-9, 1), (-9, 2), (-9, 3), (-9, 4), (-8, -6),
         (-8, -5), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1), (-8, 2), (-8, 3), (-8, 4), (-8, 5),
         (-8, 6), (-7, -7), (-7, -6), (-7, -5), (-7, -4), (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2),
         (-7, 3), (-7, 4), (-7, 5), (-7, 6), (-7, 7), (-6, -8), (-6, -7), (-6, -6), (-6, -5), (-6, -4), (-6, -3),
         (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3), (-6, 4), (-6, 5), (-6, 6), (-6, 7), (-6, 8), (-5, -8),
         (-5, -7), (-5, -6), (-5, -5), (-5, -4), (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3),
         (-5, 4), (-5, 5), (-5, 6), (-5, 7), (-5, 8), (-4, -9), (-4, -8), (-4, -7), (-4, -6), (-4, -5), (-4, -4),
         (-4, -3), (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5), (-4, 6), (-4, 7), (-4, 8),
         (-4, 9), (-3, -9), (-3, -8), (-3, -7), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2), (-3, -1), (-3, 1),
         (-3, 2), (-3, 3), (-3, 4), (-3, 5), (-3, 6), (-3, 7), (-3, 8), (-3, 9), (-2, -9), (-2, -8), (-2, -7), (-2, -6),
         (-2, -5), (-2, -4), (-2, -3), (-2, 3), (-2, 4), (-2, 5), (-2, 6), (-2, 7), (-2, 8), (-2, 9), (-1, -9),
         (-1, -8), (-1, -7), (-1, -6), (-1, -5), (-1, -4), (-1, -3), (-1, 3), (-1, 4), (-1, 5), (-1, 6), (-1, 7),
         (-1, 8), (-1, 9), (0, -10), (0, -9), (0, -8), (0, -7), (0, -6), (0, -5), (0, -4), (0, 4), (0, 5), (0, 6),
         (0, 7), (0, 8), (0, 9), (0, 10), (1, -9), (1, -8), (1, -7), (1, -6), (1, -5), (1, -4), (1, -3), (1, 3), (1, 4),
         (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (2, -9), (2, -8), (2, -7), (2, -6), (2, -5), (2, -4), (2, -3), (2, 3),
         (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (3, -9), (3, -8), (3, -7), (3, -6), (3, -5), (3, -4), (3, -3),
         (3, -2), (3, -1), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (4, -9), (4, -8),
         (4, -7), (4, -6), (4, -5), (4, -4), (4, -3), (4, -2), (4, -1), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5),
         (4, 6), (4, 7), (4, 8), (4, 9), (5, -8), (5, -7), (5, -6), (5, -5), (5, -4), (5, -3), (5, -2), (5, -1), (5, 0),
         (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (6, -8), (6, -7), (6, -6), (6, -5), (6, -4),
         (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8), (7, -7),
         (7, -6), (7, -5), (7, -4), (7, -3), (7, -2), (7, -1), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6),
         (7, 7), (8, -6), (8, -5), (8, -4), (8, -3), (8, -2), (8, -1), (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5),
         (8, 6), (9, -4), (9, -3), (9, -2), (9, -1), (9, 0), (9, 1), (9, 2), (9, 3), (9, 4), (10, 0)]
        ,
        [(-11, 0), (-10, -4), (-10, -3), (-10, -2), (-10, -1), (-10, 0), (-10, 1), (-10, 2), (-10, 3), (-10, 4),
         (-9, -6), (-9, -5), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 0), (-9, 1), (-9, 2), (-9, 3), (-9, 4),
         (-9, 5), (-9, 6), (-8, -7), (-8, -6), (-8, -5), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1),
         (-8, 2), (-8, 3), (-8, 4), (-8, 5), (-8, 6), (-8, 7), (-7, -8), (-7, -7), (-7, -6), (-7, -5), (-7, -4),
         (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2), (-7, 3), (-7, 4), (-7, 5), (-7, 6), (-7, 7), (-7, 8),
         (-6, -9), (-6, -8), (-6, -7), (-6, -6), (-6, -5), (-6, -4), (-6, -3), (-6, -2), (-6, -1), (-6, 0), (-6, 1),
         (-6, 2), (-6, 3), (-6, 4), (-6, 5), (-6, 6), (-6, 7), (-6, 8), (-6, 9), (-5, -9), (-5, -8), (-5, -7), (-5, -6),
         (-5, -5), (-5, -4), (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3), (-5, 4), (-5, 5),
         (-5, 6), (-5, 7), (-5, 8), (-5, 9), (-4, -10), (-4, -9), (-4, -8), (-4, -7), (-4, -6), (-4, -5), (-4, -4),
         (-4, -3), (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5), (-4, 6), (-4, 7), (-4, 8),
         (-4, 9), (-4, 10), (-3, -10), (-3, -9), (-3, -8), (-3, -7), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2),
         (-3, -1), (-3, 1), (-3, 2), (-3, 3), (-3, 4), (-3, 5), (-3, 6), (-3, 7), (-3, 8), (-3, 9), (-3, 10), (-2, -10),
         (-2, -9), (-2, -8), (-2, -7), (-2, -6), (-2, -5), (-2, -4), (-2, -3), (-2, 3), (-2, 4), (-2, 5), (-2, 6),
         (-2, 7), (-2, 8), (-2, 9), (-2, 10), (-1, -10), (-1, -9), (-1, -8), (-1, -7), (-1, -6), (-1, -5), (-1, -4),
         (-1, -3), (-1, 3), (-1, 4), (-1, 5), (-1, 6), (-1, 7), (-1, 8), (-1, 9), (-1, 10), (0, -11), (0, -10), (0, -9),
         (0, -8), (0, -7), (0, -6), (0, -5), (0, -4), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10), (0, 11),
         (1, -10), (1, -9), (1, -8), (1, -7), (1, -6), (1, -5), (1, -4), (1, -3), (1, 3), (1, 4), (1, 5), (1, 6),
         (1, 7), (1, 8), (1, 9), (1, 10), (2, -10), (2, -9), (2, -8), (2, -7), (2, -6), (2, -5), (2, -4), (2, -3),
         (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (2, 10), (3, -10), (3, -9), (3, -8), (3, -7), (3, -6),
         (3, -5), (3, -4), (3, -3), (3, -2), (3, -1), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8),
         (3, 9), (3, 10), (4, -10), (4, -9), (4, -8), (4, -7), (4, -6), (4, -5), (4, -4), (4, -3), (4, -2), (4, -1),
         (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9), (4, 10), (5, -9), (5, -8),
         (5, -7), (5, -6), (5, -5), (5, -4), (5, -3), (5, -2), (5, -1), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5),
         (5, 6), (5, 7), (5, 8), (5, 9), (6, -9), (6, -8), (6, -7), (6, -6), (6, -5), (6, -4), (6, -3), (6, -2),
         (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8), (6, 9), (7, -8), (7, -7),
         (7, -6), (7, -5), (7, -4), (7, -3), (7, -2), (7, -1), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6),
         (7, 7), (7, 8), (8, -7), (8, -6), (8, -5), (8, -4), (8, -3), (8, -2), (8, -1), (8, 0), (8, 1), (8, 2), (8, 3),
         (8, 4), (8, 5), (8, 6), (8, 7), (9, -6), (9, -5), (9, -4), (9, -3), (9, -2), (9, -1), (9, 0), (9, 1), (9, 2),
         (9, 3), (9, 4), (9, 5), (9, 6), (10, -4), (10, -3), (10, -2), (10, -1), (10, 0), (10, 1), (10, 2), (10, 3),
         (10, 4), (11, 0)]
        ,
        [(-12, 0), (-11, -4), (-11, -3), (-11, -2), (-11, -1), (-11, 0), (-11, 1), (-11, 2), (-11, 3), (-11, 4),
         (-10, -6), (-10, -5), (-10, -4), (-10, -3), (-10, -2), (-10, -1), (-10, 0), (-10, 1), (-10, 2), (-10, 3),
         (-10, 4), (-10, 5), (-10, 6), (-9, -7), (-9, -6), (-9, -5), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 0),
         (-9, 1), (-9, 2), (-9, 3), (-9, 4), (-9, 5), (-9, 6), (-9, 7), (-8, -8), (-8, -7), (-8, -6), (-8, -5),
         (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1), (-8, 2), (-8, 3), (-8, 4), (-8, 5), (-8, 6), (-8, 7),
         (-8, 8), (-7, -9), (-7, -8), (-7, -7), (-7, -6), (-7, -5), (-7, -4), (-7, -3), (-7, -2), (-7, -1), (-7, 0),
         (-7, 1), (-7, 2), (-7, 3), (-7, 4), (-7, 5), (-7, 6), (-7, 7), (-7, 8), (-7, 9), (-6, -10), (-6, -9), (-6, -8),
         (-6, -7), (-6, -6), (-6, -5), (-6, -4), (-6, -3), (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3),
         (-6, 4), (-6, 5), (-6, 6), (-6, 7), (-6, 8), (-6, 9), (-6, 10), (-5, -10), (-5, -9), (-5, -8), (-5, -7),
         (-5, -6), (-5, -5), (-5, -4), (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3), (-5, 4),
         (-5, 5), (-5, 6), (-5, 7), (-5, 8), (-5, 9), (-5, 10), (-4, -11), (-4, -10), (-4, -9), (-4, -8), (-4, -7),
         (-4, -6), (-4, -5), (-4, -4), (-4, -3), (-4, -2), (-4, -1), (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4),
         (-4, 5), (-4, 6), (-4, 7), (-4, 8), (-4, 9), (-4, 10), (-4, 11), (-3, -11), (-3, -10), (-3, -9), (-3, -8),
         (-3, -7), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, -2), (-3, -1), (-3, 1), (-3, 2), (-3, 3), (-3, 4),
         (-3, 5), (-3, 6), (-3, 7), (-3, 8), (-3, 9), (-3, 10), (-3, 11), (-2, -11), (-2, -10), (-2, -9), (-2, -8),
         (-2, -7), (-2, -6), (-2, -5), (-2, -4), (-2, -3), (-2, 3), (-2, 4), (-2, 5), (-2, 6), (-2, 7), (-2, 8),
         (-2, 9), (-2, 10), (-2, 11), (-1, -11), (-1, -10), (-1, -9), (-1, -8), (-1, -7), (-1, -6), (-1, -5), (-1, -4),
         (-1, -3), (-1, 3), (-1, 4), (-1, 5), (-1, 6), (-1, 7), (-1, 8), (-1, 9), (-1, 10), (-1, 11), (0, -12),
         (0, -11), (0, -10), (0, -9), (0, -8), (0, -7), (0, -6), (0, -5), (0, -4), (0, 4), (0, 5), (0, 6), (0, 7),
         (0, 8), (0, 9), (0, 10), (0, 11), (0, 12), (1, -11), (1, -10), (1, -9), (1, -8), (1, -7), (1, -6), (1, -5),
         (1, -4), (1, -3), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10), (1, 11), (2, -11), (2, -10),
         (2, -9), (2, -8), (2, -7), (2, -6), (2, -5), (2, -4), (2, -3), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8),
         (2, 9), (2, 10), (2, 11), (3, -11), (3, -10), (3, -9), (3, -8), (3, -7), (3, -6), (3, -5), (3, -4), (3, -3),
         (3, -2), (3, -1), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (3, 10), (3, 11),
         (4, -11), (4, -10), (4, -9), (4, -8), (4, -7), (4, -6), (4, -5), (4, -4), (4, -3), (4, -2), (4, -1), (4, 0),
         (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9), (4, 10), (4, 11), (5, -10), (5, -9),
         (5, -8), (5, -7), (5, -6), (5, -5), (5, -4), (5, -3), (5, -2), (5, -1), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4),
         (5, 5), (5, 6), (5, 7), (5, 8), (5, 9), (5, 10), (6, -10), (6, -9), (6, -8), (6, -7), (6, -6), (6, -5),
         (6, -4), (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8),
         (6, 9), (6, 10), (7, -9), (7, -8), (7, -7), (7, -6), (7, -5), (7, -4), (7, -3), (7, -2), (7, -1), (7, 0),
         (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (7, 8), (7, 9), (8, -8), (8, -7), (8, -6), (8, -5),
         (8, -4), (8, -3), (8, -2), (8, -1), (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (8, 8),
         (9, -7), (9, -6), (9, -5), (9, -4), (9, -3), (9, -2), (9, -1), (9, 0), (9, 1), (9, 2), (9, 3), (9, 4), (9, 5),
         (9, 6), (9, 7), (10, -6), (10, -5), (10, -4), (10, -3), (10, -2), (10, -1), (10, 0), (10, 1), (10, 2), (10, 3),
         (10, 4), (10, 5), (10, 6), (11, -4), (11, -3), (11, -2), (11, -1), (11, 0), (11, 1), (11, 2), (11, 3), (11, 4),
         (12, 0)]

    ],
    [
        [],
        [],
        [],
        [],
        [],
        [(-5, 0), (-4, -3), (-4, -2), (-4, -1), (-4, 1), (-4, 2), (-4, 3), (-3, -4), (-3, -3), (-3, 3), (-3, 4),
         (-2, -4), (-2, 4), (-1, -4), (-1, 4), (0, -5), (0, 5), (1, -4), (1, 4), (2, -4), (2, 4), (3, -4), (3, -3),
         (3, 3), (3, 4), (4, -3), (4, -2), (4, -1), (4, 1), (4, 2), (4, 3), (5, 0)]
        ,
        [(-6, 0), (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3), (-4, -4), (-4, -3), (-4, -2),
         (-4, -1), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-3, -5), (-3, -4), (-3, -3), (-3, 3), (-3, 4), (-3, 5),
         (-2, -5), (-2, -4), (-2, 4), (-2, 5), (-1, -5), (-1, -4), (-1, 4), (-1, 5), (0, -6), (0, -5), (0, 5), (0, 6),
         (1, -5), (1, -4), (1, 4), (1, 5), (2, -5), (2, -4), (2, 4), (2, 5), (3, -5), (3, -4), (3, -3), (3, 3), (3, 4),
         (3, 5), (4, -4), (4, -3), (4, -2), (4, -1), (4, 1), (4, 2), (4, 3), (4, 4), (5, -3), (5, -2), (5, -1), (5, 0),
         (5, 1), (5, 2), (5, 3), (6, 0)]
        ,
        [(-7, 0), (-6, -3), (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3), (-5, -4), (-5, -3), (-5, -2),
         (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3), (-5, 4), (-4, -5), (-4, -4), (-4, -3), (-4, -2), (-4, -1),
         (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, 3), (-3, 4), (-3, 5),
         (-3, 6), (-2, -6), (-2, -5), (-2, -4), (-2, 4), (-2, 5), (-2, 6), (-1, -6), (-1, -5), (-1, -4), (-1, 4),
         (-1, 5), (-1, 6), (0, -7), (0, -6), (0, -5), (0, 5), (0, 6), (0, 7), (1, -6), (1, -5), (1, -4), (1, 4), (1, 5),
         (1, 6), (2, -6), (2, -5), (2, -4), (2, 4), (2, 5), (2, 6), (3, -6), (3, -5), (3, -4), (3, -3), (3, 3), (3, 4),
         (3, 5), (3, 6), (4, -5), (4, -4), (4, -3), (4, -2), (4, -1), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (5, -4),
         (5, -3), (5, -2), (5, -1), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (6, -3), (6, -2), (6, -1), (6, 0), (6, 1),
         (6, 2), (6, 3), (7, 0)]
        ,
        [(-8, 0), (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2), (-7, 3), (-6, -5), (-6, -4), (-6, -3),
         (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3), (-6, 4), (-6, 5), (-5, -6), (-5, -5), (-5, -4),
         (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3), (-5, 4), (-5, 5), (-5, 6), (-4, -6),
         (-4, -5), (-4, -4), (-4, -3), (-4, -2), (-4, -1), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5), (-4, 6),
         (-3, -7), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, 3), (-3, 4), (-3, 5), (-3, 6), (-3, 7), (-2, -7),
         (-2, -6), (-2, -5), (-2, -4), (-2, 4), (-2, 5), (-2, 6), (-2, 7), (-1, -7), (-1, -6), (-1, -5), (-1, -4),
         (-1, 4), (-1, 5), (-1, 6), (-1, 7), (0, -8), (0, -7), (0, -6), (0, -5), (0, 5), (0, 6), (0, 7), (0, 8),
         (1, -7), (1, -6), (1, -5), (1, -4), (1, 4), (1, 5), (1, 6), (1, 7), (2, -7), (2, -6), (2, -5), (2, -4), (2, 4),
         (2, 5), (2, 6), (2, 7), (3, -7), (3, -6), (3, -5), (3, -4), (3, -3), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7),
         (4, -6), (4, -5), (4, -4), (4, -3), (4, -2), (4, -1), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (5, -6),
         (5, -5), (5, -4), (5, -3), (5, -2), (5, -1), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (6, -5),
         (6, -4), (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (7, -3), (7, -2), (7, -1),
         (7, 0), (7, 1), (7, 2), (7, 3), (8, 0)]
        ,
        [(-9, 0), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1), (-8, 2), (-8, 3), (-8, 4), (-7, -5),
         (-7, -4), (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2), (-7, 3), (-7, 4), (-7, 5), (-6, -6),
         (-6, -5), (-6, -4), (-6, -3), (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3), (-6, 4), (-6, 5),
         (-6, 6), (-5, -7), (-5, -6), (-5, -5), (-5, -4), (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2),
         (-5, 3), (-5, 4), (-5, 5), (-5, 6), (-5, 7), (-4, -8), (-4, -7), (-4, -6), (-4, -5), (-4, -4), (-4, -3),
         (-4, -2), (-4, -1), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5), (-4, 6), (-4, 7), (-4, 8), (-3, -8), (-3, -7),
         (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, 3), (-3, 4), (-3, 5), (-3, 6), (-3, 7), (-3, 8), (-2, -8),
         (-2, -7), (-2, -6), (-2, -5), (-2, -4), (-2, 4), (-2, 5), (-2, 6), (-2, 7), (-2, 8), (-1, -8), (-1, -7),
         (-1, -6), (-1, -5), (-1, -4), (-1, 4), (-1, 5), (-1, 6), (-1, 7), (-1, 8), (0, -9), (0, -8), (0, -7), (0, -6),
         (0, -5), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (1, -8), (1, -7), (1, -6), (1, -5), (1, -4), (1, 4), (1, 5),
         (1, 6), (1, 7), (1, 8), (2, -8), (2, -7), (2, -6), (2, -5), (2, -4), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8),
         (3, -8), (3, -7), (3, -6), (3, -5), (3, -4), (3, -3), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (4, -8),
         (4, -7), (4, -6), (4, -5), (4, -4), (4, -3), (4, -2), (4, -1), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6),
         (4, 7), (4, 8), (5, -7), (5, -6), (5, -5), (5, -4), (5, -3), (5, -2), (5, -1), (5, 0), (5, 1), (5, 2), (5, 3),
         (5, 4), (5, 5), (5, 6), (5, 7), (6, -6), (6, -5), (6, -4), (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2),
         (6, 3), (6, 4), (6, 5), (6, 6), (7, -5), (7, -4), (7, -3), (7, -2), (7, -1), (7, 0), (7, 1), (7, 2), (7, 3),
         (7, 4), (7, 5), (8, -4), (8, -3), (8, -2), (8, -1), (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (9, 0)]
        ,
        [(-10, 0), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 0), (-9, 1), (-9, 2), (-9, 3), (-9, 4), (-8, -6),
         (-8, -5), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1), (-8, 2), (-8, 3), (-8, 4), (-8, 5),
         (-8, 6), (-7, -7), (-7, -6), (-7, -5), (-7, -4), (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2),
         (-7, 3), (-7, 4), (-7, 5), (-7, 6), (-7, 7), (-6, -8), (-6, -7), (-6, -6), (-6, -5), (-6, -4), (-6, -3),
         (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3), (-6, 4), (-6, 5), (-6, 6), (-6, 7), (-6, 8), (-5, -8),
         (-5, -7), (-5, -6), (-5, -5), (-5, -4), (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3),
         (-5, 4), (-5, 5), (-5, 6), (-5, 7), (-5, 8), (-4, -9), (-4, -8), (-4, -7), (-4, -6), (-4, -5), (-4, -4),
         (-4, -3), (-4, -2), (-4, -1), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5), (-4, 6), (-4, 7), (-4, 8), (-4, 9),
         (-3, -9), (-3, -8), (-3, -7), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, 3), (-3, 4), (-3, 5), (-3, 6),
         (-3, 7), (-3, 8), (-3, 9), (-2, -9), (-2, -8), (-2, -7), (-2, -6), (-2, -5), (-2, -4), (-2, 4), (-2, 5),
         (-2, 6), (-2, 7), (-2, 8), (-2, 9), (-1, -9), (-1, -8), (-1, -7), (-1, -6), (-1, -5), (-1, -4), (-1, 4),
         (-1, 5), (-1, 6), (-1, 7), (-1, 8), (-1, 9), (0, -10), (0, -9), (0, -8), (0, -7), (0, -6), (0, -5), (0, 5),
         (0, 6), (0, 7), (0, 8), (0, 9), (0, 10), (1, -9), (1, -8), (1, -7), (1, -6), (1, -5), (1, -4), (1, 4), (1, 5),
         (1, 6), (1, 7), (1, 8), (1, 9), (2, -9), (2, -8), (2, -7), (2, -6), (2, -5), (2, -4), (2, 4), (2, 5), (2, 6),
         (2, 7), (2, 8), (2, 9), (3, -9), (3, -8), (3, -7), (3, -6), (3, -5), (3, -4), (3, -3), (3, 3), (3, 4), (3, 5),
         (3, 6), (3, 7), (3, 8), (3, 9), (4, -9), (4, -8), (4, -7), (4, -6), (4, -5), (4, -4), (4, -3), (4, -2),
         (4, -1), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9), (5, -8), (5, -7), (5, -6),
         (5, -5), (5, -4), (5, -3), (5, -2), (5, -1), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7),
         (5, 8), (6, -8), (6, -7), (6, -6), (6, -5), (6, -4), (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2), (6, 3),
         (6, 4), (6, 5), (6, 6), (6, 7), (6, 8), (7, -7), (7, -6), (7, -5), (7, -4), (7, -3), (7, -2), (7, -1), (7, 0),
         (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (8, -6), (8, -5), (8, -4), (8, -3), (8, -2), (8, -1),
         (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (9, -4), (9, -3), (9, -2), (9, -1), (9, 0), (9, 1),
         (9, 2), (9, 3), (9, 4), (10, 0)]
        ,
        [(-11, 0), (-10, -4), (-10, -3), (-10, -2), (-10, -1), (-10, 0), (-10, 1), (-10, 2), (-10, 3), (-10, 4),
         (-9, -6), (-9, -5), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 0), (-9, 1), (-9, 2), (-9, 3), (-9, 4),
         (-9, 5), (-9, 6), (-8, -7), (-8, -6), (-8, -5), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1),
         (-8, 2), (-8, 3), (-8, 4), (-8, 5), (-8, 6), (-8, 7), (-7, -8), (-7, -7), (-7, -6), (-7, -5), (-7, -4),
         (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2), (-7, 3), (-7, 4), (-7, 5), (-7, 6), (-7, 7), (-7, 8),
         (-6, -9), (-6, -8), (-6, -7), (-6, -6), (-6, -5), (-6, -4), (-6, -3), (-6, -2), (-6, -1), (-6, 0), (-6, 1),
         (-6, 2), (-6, 3), (-6, 4), (-6, 5), (-6, 6), (-6, 7), (-6, 8), (-6, 9), (-5, -9), (-5, -8), (-5, -7), (-5, -6),
         (-5, -5), (-5, -4), (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3), (-5, 4), (-5, 5),
         (-5, 6), (-5, 7), (-5, 8), (-5, 9), (-4, -10), (-4, -9), (-4, -8), (-4, -7), (-4, -6), (-4, -5), (-4, -4),
         (-4, -3), (-4, -2), (-4, -1), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5), (-4, 6), (-4, 7), (-4, 8), (-4, 9),
         (-4, 10), (-3, -10), (-3, -9), (-3, -8), (-3, -7), (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, 3), (-3, 4),
         (-3, 5), (-3, 6), (-3, 7), (-3, 8), (-3, 9), (-3, 10), (-2, -10), (-2, -9), (-2, -8), (-2, -7), (-2, -6),
         (-2, -5), (-2, -4), (-2, 4), (-2, 5), (-2, 6), (-2, 7), (-2, 8), (-2, 9), (-2, 10), (-1, -10), (-1, -9),
         (-1, -8), (-1, -7), (-1, -6), (-1, -5), (-1, -4), (-1, 4), (-1, 5), (-1, 6), (-1, 7), (-1, 8), (-1, 9),
         (-1, 10), (0, -11), (0, -10), (0, -9), (0, -8), (0, -7), (0, -6), (0, -5), (0, 5), (0, 6), (0, 7), (0, 8),
         (0, 9), (0, 10), (0, 11), (1, -10), (1, -9), (1, -8), (1, -7), (1, -6), (1, -5), (1, -4), (1, 4), (1, 5),
         (1, 6), (1, 7), (1, 8), (1, 9), (1, 10), (2, -10), (2, -9), (2, -8), (2, -7), (2, -6), (2, -5), (2, -4),
         (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (2, 10), (3, -10), (3, -9), (3, -8), (3, -7), (3, -6), (3, -5),
         (3, -4), (3, -3), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (3, 10), (4, -10), (4, -9), (4, -8),
         (4, -7), (4, -6), (4, -5), (4, -4), (4, -3), (4, -2), (4, -1), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6),
         (4, 7), (4, 8), (4, 9), (4, 10), (5, -9), (5, -8), (5, -7), (5, -6), (5, -5), (5, -4), (5, -3), (5, -2),
         (5, -1), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (5, 9), (6, -9), (6, -8),
         (6, -7), (6, -6), (6, -5), (6, -4), (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5),
         (6, 6), (6, 7), (6, 8), (6, 9), (7, -8), (7, -7), (7, -6), (7, -5), (7, -4), (7, -3), (7, -2), (7, -1), (7, 0),
         (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (7, 8), (8, -7), (8, -6), (8, -5), (8, -4), (8, -3),
         (8, -2), (8, -1), (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (9, -6), (9, -5), (9, -4),
         (9, -3), (9, -2), (9, -1), (9, 0), (9, 1), (9, 2), (9, 3), (9, 4), (9, 5), (9, 6), (10, -4), (10, -3),
         (10, -2), (10, -1), (10, 0), (10, 1), (10, 2), (10, 3), (10, 4), (11, 0)]
        ,
        [(-12, 0), (-11, -4), (-11, -3), (-11, -2), (-11, -1), (-11, 0), (-11, 1), (-11, 2), (-11, 3), (-11, 4),
         (-10, -6), (-10, -5), (-10, -4), (-10, -3), (-10, -2), (-10, -1), (-10, 0), (-10, 1), (-10, 2), (-10, 3),
         (-10, 4), (-10, 5), (-10, 6), (-9, -7), (-9, -6), (-9, -5), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 0),
         (-9, 1), (-9, 2), (-9, 3), (-9, 4), (-9, 5), (-9, 6), (-9, 7), (-8, -8), (-8, -7), (-8, -6), (-8, -5),
         (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1), (-8, 2), (-8, 3), (-8, 4), (-8, 5), (-8, 6), (-8, 7),
         (-8, 8), (-7, -9), (-7, -8), (-7, -7), (-7, -6), (-7, -5), (-7, -4), (-7, -3), (-7, -2), (-7, -1), (-7, 0),
         (-7, 1), (-7, 2), (-7, 3), (-7, 4), (-7, 5), (-7, 6), (-7, 7), (-7, 8), (-7, 9), (-6, -10), (-6, -9), (-6, -8),
         (-6, -7), (-6, -6), (-6, -5), (-6, -4), (-6, -3), (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3),
         (-6, 4), (-6, 5), (-6, 6), (-6, 7), (-6, 8), (-6, 9), (-6, 10), (-5, -10), (-5, -9), (-5, -8), (-5, -7),
         (-5, -6), (-5, -5), (-5, -4), (-5, -3), (-5, -2), (-5, -1), (-5, 0), (-5, 1), (-5, 2), (-5, 3), (-5, 4),
         (-5, 5), (-5, 6), (-5, 7), (-5, 8), (-5, 9), (-5, 10), (-4, -11), (-4, -10), (-4, -9), (-4, -8), (-4, -7),
         (-4, -6), (-4, -5), (-4, -4), (-4, -3), (-4, -2), (-4, -1), (-4, 1), (-4, 2), (-4, 3), (-4, 4), (-4, 5),
         (-4, 6), (-4, 7), (-4, 8), (-4, 9), (-4, 10), (-4, 11), (-3, -11), (-3, -10), (-3, -9), (-3, -8), (-3, -7),
         (-3, -6), (-3, -5), (-3, -4), (-3, -3), (-3, 3), (-3, 4), (-3, 5), (-3, 6), (-3, 7), (-3, 8), (-3, 9),
         (-3, 10), (-3, 11), (-2, -11), (-2, -10), (-2, -9), (-2, -8), (-2, -7), (-2, -6), (-2, -5), (-2, -4), (-2, 4),
         (-2, 5), (-2, 6), (-2, 7), (-2, 8), (-2, 9), (-2, 10), (-2, 11), (-1, -11), (-1, -10), (-1, -9), (-1, -8),
         (-1, -7), (-1, -6), (-1, -5), (-1, -4), (-1, 4), (-1, 5), (-1, 6), (-1, 7), (-1, 8), (-1, 9), (-1, 10),
         (-1, 11), (0, -12), (0, -11), (0, -10), (0, -9), (0, -8), (0, -7), (0, -6), (0, -5), (0, 5), (0, 6), (0, 7),
         (0, 8), (0, 9), (0, 10), (0, 11), (0, 12), (1, -11), (1, -10), (1, -9), (1, -8), (1, -7), (1, -6), (1, -5),
         (1, -4), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10), (1, 11), (2, -11), (2, -10), (2, -9),
         (2, -8), (2, -7), (2, -6), (2, -5), (2, -4), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (2, 10), (2, 11),
         (3, -11), (3, -10), (3, -9), (3, -8), (3, -7), (3, -6), (3, -5), (3, -4), (3, -3), (3, 3), (3, 4), (3, 5),
         (3, 6), (3, 7), (3, 8), (3, 9), (3, 10), (3, 11), (4, -11), (4, -10), (4, -9), (4, -8), (4, -7), (4, -6),
         (4, -5), (4, -4), (4, -3), (4, -2), (4, -1), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8),
         (4, 9), (4, 10), (4, 11), (5, -10), (5, -9), (5, -8), (5, -7), (5, -6), (5, -5), (5, -4), (5, -3), (5, -2),
         (5, -1), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (5, 9), (5, 10), (6, -10),
         (6, -9), (6, -8), (6, -7), (6, -6), (6, -5), (6, -4), (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2),
         (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8), (6, 9), (6, 10), (7, -9), (7, -8), (7, -7), (7, -6), (7, -5),
         (7, -4), (7, -3), (7, -2), (7, -1), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (7, 8),
         (7, 9), (8, -8), (8, -7), (8, -6), (8, -5), (8, -4), (8, -3), (8, -2), (8, -1), (8, 0), (8, 1), (8, 2), (8, 3),
         (8, 4), (8, 5), (8, 6), (8, 7), (8, 8), (9, -7), (9, -6), (9, -5), (9, -4), (9, -3), (9, -2), (9, -1), (9, 0),
         (9, 1), (9, 2), (9, 3), (9, 4), (9, 5), (9, 6), (9, 7), (10, -6), (10, -5), (10, -4), (10, -3), (10, -2),
         (10, -1), (10, 0), (10, 1), (10, 2), (10, 3), (10, 4), (10, 5), (10, 6), (11, -4), (11, -3), (11, -2),
         (11, -1), (11, 0), (11, 1), (11, 2), (11, 3), (11, 4), (12, 0)]

    ],
    [
        [],
        [],
        [],
        [],
        [],
        [],
        [(-6, 0), (-5, -3), (-5, -2), (-5, -1), (-5, 1), (-5, 2), (-5, 3), (-4, -4), (-4, 4), (-3, -5), (-3, 5),
         (-2, -5), (-2, 5), (-1, -5), (-1, 5), (0, -6), (0, 6), (1, -5), (1, 5), (2, -5), (2, 5), (3, -5), (3, 5),
         (4, -4), (4, 4), (5, -3), (5, -2), (5, -1), (5, 1), (5, 2), (5, 3), (6, 0)]
        ,
        [(-7, 0), (-6, -3), (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3), (-5, -4), (-5, -3), (-5, -2),
         (-5, -1), (-5, 1), (-5, 2), (-5, 3), (-5, 4), (-4, -5), (-4, -4), (-4, 4), (-4, 5), (-3, -6), (-3, -5),
         (-3, 5), (-3, 6), (-2, -6), (-2, -5), (-2, 5), (-2, 6), (-1, -6), (-1, -5), (-1, 5), (-1, 6), (0, -7), (0, -6),
         (0, 6), (0, 7), (1, -6), (1, -5), (1, 5), (1, 6), (2, -6), (2, -5), (2, 5), (2, 6), (3, -6), (3, -5), (3, 5),
         (3, 6), (4, -5), (4, -4), (4, 4), (4, 5), (5, -4), (5, -3), (5, -2), (5, -1), (5, 1), (5, 2), (5, 3), (5, 4),
         (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (7, 0)]
        ,
        [(-8, 0), (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2), (-7, 3), (-6, -5), (-6, -4), (-6, -3),
         (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3), (-6, 4), (-6, 5), (-5, -6), (-5, -5), (-5, -4),
         (-5, -3), (-5, -2), (-5, -1), (-5, 1), (-5, 2), (-5, 3), (-5, 4), (-5, 5), (-5, 6), (-4, -6), (-4, -5),
         (-4, -4), (-4, 4), (-4, 5), (-4, 6), (-3, -7), (-3, -6), (-3, -5), (-3, 5), (-3, 6), (-3, 7), (-2, -7),
         (-2, -6), (-2, -5), (-2, 5), (-2, 6), (-2, 7), (-1, -7), (-1, -6), (-1, -5), (-1, 5), (-1, 6), (-1, 7),
         (0, -8), (0, -7), (0, -6), (0, 6), (0, 7), (0, 8), (1, -7), (1, -6), (1, -5), (1, 5), (1, 6), (1, 7), (2, -7),
         (2, -6), (2, -5), (2, 5), (2, 6), (2, 7), (3, -7), (3, -6), (3, -5), (3, 5), (3, 6), (3, 7), (4, -6), (4, -5),
         (4, -4), (4, 4), (4, 5), (4, 6), (5, -6), (5, -5), (5, -4), (5, -3), (5, -2), (5, -1), (5, 1), (5, 2), (5, 3),
         (5, 4), (5, 5), (5, 6), (6, -5), (6, -4), (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4),
         (6, 5), (7, -3), (7, -2), (7, -1), (7, 0), (7, 1), (7, 2), (7, 3), (8, 0)]
        ,
        [(-9, 0), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1), (-8, 2), (-8, 3), (-8, 4), (-7, -5),
         (-7, -4), (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2), (-7, 3), (-7, 4), (-7, 5), (-6, -6),
         (-6, -5), (-6, -4), (-6, -3), (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3), (-6, 4), (-6, 5),
         (-6, 6), (-5, -7), (-5, -6), (-5, -5), (-5, -4), (-5, -3), (-5, -2), (-5, -1), (-5, 1), (-5, 2), (-5, 3),
         (-5, 4), (-5, 5), (-5, 6), (-5, 7), (-4, -8), (-4, -7), (-4, -6), (-4, -5), (-4, -4), (-4, 4), (-4, 5),
         (-4, 6), (-4, 7), (-4, 8), (-3, -8), (-3, -7), (-3, -6), (-3, -5), (-3, 5), (-3, 6), (-3, 7), (-3, 8),
         (-2, -8), (-2, -7), (-2, -6), (-2, -5), (-2, 5), (-2, 6), (-2, 7), (-2, 8), (-1, -8), (-1, -7), (-1, -6),
         (-1, -5), (-1, 5), (-1, 6), (-1, 7), (-1, 8), (0, -9), (0, -8), (0, -7), (0, -6), (0, 6), (0, 7), (0, 8),
         (0, 9), (1, -8), (1, -7), (1, -6), (1, -5), (1, 5), (1, 6), (1, 7), (1, 8), (2, -8), (2, -7), (2, -6), (2, -5),
         (2, 5), (2, 6), (2, 7), (2, 8), (3, -8), (3, -7), (3, -6), (3, -5), (3, 5), (3, 6), (3, 7), (3, 8), (4, -8),
         (4, -7), (4, -6), (4, -5), (4, -4), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (5, -7), (5, -6), (5, -5), (5, -4),
         (5, -3), (5, -2), (5, -1), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (6, -6), (6, -5), (6, -4),
         (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (7, -5), (7, -4), (7, -3),
         (7, -2), (7, -1), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (8, -4), (8, -3), (8, -2), (8, -1), (8, 0),
         (8, 1), (8, 2), (8, 3), (8, 4), (9, 0)]
        ,
        [(-10, 0), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 0), (-9, 1), (-9, 2), (-9, 3), (-9, 4), (-8, -6),
         (-8, -5), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1), (-8, 2), (-8, 3), (-8, 4), (-8, 5),
         (-8, 6), (-7, -7), (-7, -6), (-7, -5), (-7, -4), (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2),
         (-7, 3), (-7, 4), (-7, 5), (-7, 6), (-7, 7), (-6, -8), (-6, -7), (-6, -6), (-6, -5), (-6, -4), (-6, -3),
         (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3), (-6, 4), (-6, 5), (-6, 6), (-6, 7), (-6, 8), (-5, -8),
         (-5, -7), (-5, -6), (-5, -5), (-5, -4), (-5, -3), (-5, -2), (-5, -1), (-5, 1), (-5, 2), (-5, 3), (-5, 4),
         (-5, 5), (-5, 6), (-5, 7), (-5, 8), (-4, -9), (-4, -8), (-4, -7), (-4, -6), (-4, -5), (-4, -4), (-4, 4),
         (-4, 5), (-4, 6), (-4, 7), (-4, 8), (-4, 9), (-3, -9), (-3, -8), (-3, -7), (-3, -6), (-3, -5), (-3, 5),
         (-3, 6), (-3, 7), (-3, 8), (-3, 9), (-2, -9), (-2, -8), (-2, -7), (-2, -6), (-2, -5), (-2, 5), (-2, 6),
         (-2, 7), (-2, 8), (-2, 9), (-1, -9), (-1, -8), (-1, -7), (-1, -6), (-1, -5), (-1, 5), (-1, 6), (-1, 7),
         (-1, 8), (-1, 9), (0, -10), (0, -9), (0, -8), (0, -7), (0, -6), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10),
         (1, -9), (1, -8), (1, -7), (1, -6), (1, -5), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (2, -9), (2, -8), (2, -7),
         (2, -6), (2, -5), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (3, -9), (3, -8), (3, -7), (3, -6), (3, -5), (3, 5),
         (3, 6), (3, 7), (3, 8), (3, 9), (4, -9), (4, -8), (4, -7), (4, -6), (4, -5), (4, -4), (4, 4), (4, 5), (4, 6),
         (4, 7), (4, 8), (4, 9), (5, -8), (5, -7), (5, -6), (5, -5), (5, -4), (5, -3), (5, -2), (5, -1), (5, 1), (5, 2),
         (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (6, -8), (6, -7), (6, -6), (6, -5), (6, -4), (6, -3), (6, -2),
         (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8), (7, -7), (7, -6), (7, -5),
         (7, -4), (7, -3), (7, -2), (7, -1), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (8, -6),
         (8, -5), (8, -4), (8, -3), (8, -2), (8, -1), (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (9, -4),
         (9, -3), (9, -2), (9, -1), (9, 0), (9, 1), (9, 2), (9, 3), (9, 4), (10, 0)]
        ,
        [(-11, 0), (-10, -4), (-10, -3), (-10, -2), (-10, -1), (-10, 0), (-10, 1), (-10, 2), (-10, 3), (-10, 4),
         (-9, -6), (-9, -5), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 0), (-9, 1), (-9, 2), (-9, 3), (-9, 4),
         (-9, 5), (-9, 6), (-8, -7), (-8, -6), (-8, -5), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1),
         (-8, 2), (-8, 3), (-8, 4), (-8, 5), (-8, 6), (-8, 7), (-7, -8), (-7, -7), (-7, -6), (-7, -5), (-7, -4),
         (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2), (-7, 3), (-7, 4), (-7, 5), (-7, 6), (-7, 7), (-7, 8),
         (-6, -9), (-6, -8), (-6, -7), (-6, -6), (-6, -5), (-6, -4), (-6, -3), (-6, -2), (-6, -1), (-6, 0), (-6, 1),
         (-6, 2), (-6, 3), (-6, 4), (-6, 5), (-6, 6), (-6, 7), (-6, 8), (-6, 9), (-5, -9), (-5, -8), (-5, -7), (-5, -6),
         (-5, -5), (-5, -4), (-5, -3), (-5, -2), (-5, -1), (-5, 1), (-5, 2), (-5, 3), (-5, 4), (-5, 5), (-5, 6),
         (-5, 7), (-5, 8), (-5, 9), (-4, -10), (-4, -9), (-4, -8), (-4, -7), (-4, -6), (-4, -5), (-4, -4), (-4, 4),
         (-4, 5), (-4, 6), (-4, 7), (-4, 8), (-4, 9), (-4, 10), (-3, -10), (-3, -9), (-3, -8), (-3, -7), (-3, -6),
         (-3, -5), (-3, 5), (-3, 6), (-3, 7), (-3, 8), (-3, 9), (-3, 10), (-2, -10), (-2, -9), (-2, -8), (-2, -7),
         (-2, -6), (-2, -5), (-2, 5), (-2, 6), (-2, 7), (-2, 8), (-2, 9), (-2, 10), (-1, -10), (-1, -9), (-1, -8),
         (-1, -7), (-1, -6), (-1, -5), (-1, 5), (-1, 6), (-1, 7), (-1, 8), (-1, 9), (-1, 10), (0, -11), (0, -10),
         (0, -9), (0, -8), (0, -7), (0, -6), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10), (0, 11), (1, -10), (1, -9),
         (1, -8), (1, -7), (1, -6), (1, -5), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10), (2, -10), (2, -9),
         (2, -8), (2, -7), (2, -6), (2, -5), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (2, 10), (3, -10), (3, -9),
         (3, -8), (3, -7), (3, -6), (3, -5), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (3, 10), (4, -10), (4, -9),
         (4, -8), (4, -7), (4, -6), (4, -5), (4, -4), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9), (4, 10), (5, -9),
         (5, -8), (5, -7), (5, -6), (5, -5), (5, -4), (5, -3), (5, -2), (5, -1), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5),
         (5, 6), (5, 7), (5, 8), (5, 9), (6, -9), (6, -8), (6, -7), (6, -6), (6, -5), (6, -4), (6, -3), (6, -2),
         (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8), (6, 9), (7, -8), (7, -7),
         (7, -6), (7, -5), (7, -4), (7, -3), (7, -2), (7, -1), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6),
         (7, 7), (7, 8), (8, -7), (8, -6), (8, -5), (8, -4), (8, -3), (8, -2), (8, -1), (8, 0), (8, 1), (8, 2), (8, 3),
         (8, 4), (8, 5), (8, 6), (8, 7), (9, -6), (9, -5), (9, -4), (9, -3), (9, -2), (9, -1), (9, 0), (9, 1), (9, 2),
         (9, 3), (9, 4), (9, 5), (9, 6), (10, -4), (10, -3), (10, -2), (10, -1), (10, 0), (10, 1), (10, 2), (10, 3),
         (10, 4), (11, 0)]
        ,
        [(-12, 0), (-11, -4), (-11, -3), (-11, -2), (-11, -1), (-11, 0), (-11, 1), (-11, 2), (-11, 3), (-11, 4),
         (-10, -6), (-10, -5), (-10, -4), (-10, -3), (-10, -2), (-10, -1), (-10, 0), (-10, 1), (-10, 2), (-10, 3),
         (-10, 4), (-10, 5), (-10, 6), (-9, -7), (-9, -6), (-9, -5), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 0),
         (-9, 1), (-9, 2), (-9, 3), (-9, 4), (-9, 5), (-9, 6), (-9, 7), (-8, -8), (-8, -7), (-8, -6), (-8, -5),
         (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1), (-8, 2), (-8, 3), (-8, 4), (-8, 5), (-8, 6), (-8, 7),
         (-8, 8), (-7, -9), (-7, -8), (-7, -7), (-7, -6), (-7, -5), (-7, -4), (-7, -3), (-7, -2), (-7, -1), (-7, 0),
         (-7, 1), (-7, 2), (-7, 3), (-7, 4), (-7, 5), (-7, 6), (-7, 7), (-7, 8), (-7, 9), (-6, -10), (-6, -9), (-6, -8),
         (-6, -7), (-6, -6), (-6, -5), (-6, -4), (-6, -3), (-6, -2), (-6, -1), (-6, 0), (-6, 1), (-6, 2), (-6, 3),
         (-6, 4), (-6, 5), (-6, 6), (-6, 7), (-6, 8), (-6, 9), (-6, 10), (-5, -10), (-5, -9), (-5, -8), (-5, -7),
         (-5, -6), (-5, -5), (-5, -4), (-5, -3), (-5, -2), (-5, -1), (-5, 1), (-5, 2), (-5, 3), (-5, 4), (-5, 5),
         (-5, 6), (-5, 7), (-5, 8), (-5, 9), (-5, 10), (-4, -11), (-4, -10), (-4, -9), (-4, -8), (-4, -7), (-4, -6),
         (-4, -5), (-4, -4), (-4, 4), (-4, 5), (-4, 6), (-4, 7), (-4, 8), (-4, 9), (-4, 10), (-4, 11), (-3, -11),
         (-3, -10), (-3, -9), (-3, -8), (-3, -7), (-3, -6), (-3, -5), (-3, 5), (-3, 6), (-3, 7), (-3, 8), (-3, 9),
         (-3, 10), (-3, 11), (-2, -11), (-2, -10), (-2, -9), (-2, -8), (-2, -7), (-2, -6), (-2, -5), (-2, 5), (-2, 6),
         (-2, 7), (-2, 8), (-2, 9), (-2, 10), (-2, 11), (-1, -11), (-1, -10), (-1, -9), (-1, -8), (-1, -7), (-1, -6),
         (-1, -5), (-1, 5), (-1, 6), (-1, 7), (-1, 8), (-1, 9), (-1, 10), (-1, 11), (0, -12), (0, -11), (0, -10),
         (0, -9), (0, -8), (0, -7), (0, -6), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10), (0, 11), (0, 12), (1, -11),
         (1, -10), (1, -9), (1, -8), (1, -7), (1, -6), (1, -5), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10),
         (1, 11), (2, -11), (2, -10), (2, -9), (2, -8), (2, -7), (2, -6), (2, -5), (2, 5), (2, 6), (2, 7), (2, 8),
         (2, 9), (2, 10), (2, 11), (3, -11), (3, -10), (3, -9), (3, -8), (3, -7), (3, -6), (3, -5), (3, 5), (3, 6),
         (3, 7), (3, 8), (3, 9), (3, 10), (3, 11), (4, -11), (4, -10), (4, -9), (4, -8), (4, -7), (4, -6), (4, -5),
         (4, -4), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9), (4, 10), (4, 11), (5, -10), (5, -9), (5, -8), (5, -7),
         (5, -6), (5, -5), (5, -4), (5, -3), (5, -2), (5, -1), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7),
         (5, 8), (5, 9), (5, 10), (6, -10), (6, -9), (6, -8), (6, -7), (6, -6), (6, -5), (6, -4), (6, -3), (6, -2),
         (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8), (6, 9), (6, 10), (7, -9),
         (7, -8), (7, -7), (7, -6), (7, -5), (7, -4), (7, -3), (7, -2), (7, -1), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4),
         (7, 5), (7, 6), (7, 7), (7, 8), (7, 9), (8, -8), (8, -7), (8, -6), (8, -5), (8, -4), (8, -3), (8, -2), (8, -1),
         (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (8, 8), (9, -7), (9, -6), (9, -5), (9, -4),
         (9, -3), (9, -2), (9, -1), (9, 0), (9, 1), (9, 2), (9, 3), (9, 4), (9, 5), (9, 6), (9, 7), (10, -6), (10, -5),
         (10, -4), (10, -3), (10, -2), (10, -1), (10, 0), (10, 1), (10, 2), (10, 3), (10, 4), (10, 5), (10, 6),
         (11, -4), (11, -3), (11, -2), (11, -1), (11, 0), (11, 1), (11, 2), (11, 3), (11, 4), (12, 0)]

    ],
    [
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [(-7, 0), (-6, -3), (-6, -2), (-6, -1), (-6, 1), (-6, 2), (-6, 3), (-5, -4), (-5, 4), (-4, -5), (-4, 5),
         (-3, -6), (-3, 6), (-2, -6), (-2, 6), (-1, -6), (-1, 6), (0, -7), (0, 7), (1, -6), (1, 6), (2, -6), (2, 6),
         (3, -6), (3, 6), (4, -5), (4, 5), (5, -4), (5, 4), (6, -3), (6, -2), (6, -1), (6, 1), (6, 2), (6, 3), (7, 0)]
        ,
        [(-8, 0), (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2), (-7, 3), (-6, -5), (-6, -4), (-6, -3),
         (-6, -2), (-6, -1), (-6, 1), (-6, 2), (-6, 3), (-6, 4), (-6, 5), (-5, -6), (-5, -5), (-5, -4), (-5, 4),
         (-5, 5), (-5, 6), (-4, -6), (-4, -5), (-4, 5), (-4, 6), (-3, -7), (-3, -6), (-3, 6), (-3, 7), (-2, -7),
         (-2, -6), (-2, 6), (-2, 7), (-1, -7), (-1, -6), (-1, 6), (-1, 7), (0, -8), (0, -7), (0, 7), (0, 8), (1, -7),
         (1, -6), (1, 6), (1, 7), (2, -7), (2, -6), (2, 6), (2, 7), (3, -7), (3, -6), (3, 6), (3, 7), (4, -6), (4, -5),
         (4, 5), (4, 6), (5, -6), (5, -5), (5, -4), (5, 4), (5, 5), (5, 6), (6, -5), (6, -4), (6, -3), (6, -2), (6, -1),
         (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (7, -3), (7, -2), (7, -1), (7, 0), (7, 1), (7, 2), (7, 3), (8, 0)]
        ,
        [(-9, 0), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1), (-8, 2), (-8, 3), (-8, 4), (-7, -5),
         (-7, -4), (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2), (-7, 3), (-7, 4), (-7, 5), (-6, -6),
         (-6, -5), (-6, -4), (-6, -3), (-6, -2), (-6, -1), (-6, 1), (-6, 2), (-6, 3), (-6, 4), (-6, 5), (-6, 6),
         (-5, -7), (-5, -6), (-5, -5), (-5, -4), (-5, 4), (-5, 5), (-5, 6), (-5, 7), (-4, -8), (-4, -7), (-4, -6),
         (-4, -5), (-4, 5), (-4, 6), (-4, 7), (-4, 8), (-3, -8), (-3, -7), (-3, -6), (-3, 6), (-3, 7), (-3, 8),
         (-2, -8), (-2, -7), (-2, -6), (-2, 6), (-2, 7), (-2, 8), (-1, -8), (-1, -7), (-1, -6), (-1, 6), (-1, 7),
         (-1, 8), (0, -9), (0, -8), (0, -7), (0, 7), (0, 8), (0, 9), (1, -8), (1, -7), (1, -6), (1, 6), (1, 7), (1, 8),
         (2, -8), (2, -7), (2, -6), (2, 6), (2, 7), (2, 8), (3, -8), (3, -7), (3, -6), (3, 6), (3, 7), (3, 8), (4, -8),
         (4, -7), (4, -6), (4, -5), (4, 5), (4, 6), (4, 7), (4, 8), (5, -7), (5, -6), (5, -5), (5, -4), (5, 4), (5, 5),
         (5, 6), (5, 7), (6, -6), (6, -5), (6, -4), (6, -3), (6, -2), (6, -1), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5),
         (6, 6), (7, -5), (7, -4), (7, -3), (7, -2), (7, -1), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (8, -4),
         (8, -3), (8, -2), (8, -1), (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (9, 0)]
        ,
        [(-10, 0), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 0), (-9, 1), (-9, 2), (-9, 3), (-9, 4), (-8, -6),
         (-8, -5), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1), (-8, 2), (-8, 3), (-8, 4), (-8, 5),
         (-8, 6), (-7, -7), (-7, -6), (-7, -5), (-7, -4), (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2),
         (-7, 3), (-7, 4), (-7, 5), (-7, 6), (-7, 7), (-6, -8), (-6, -7), (-6, -6), (-6, -5), (-6, -4), (-6, -3),
         (-6, -2), (-6, -1), (-6, 1), (-6, 2), (-6, 3), (-6, 4), (-6, 5), (-6, 6), (-6, 7), (-6, 8), (-5, -8), (-5, -7),
         (-5, -6), (-5, -5), (-5, -4), (-5, 4), (-5, 5), (-5, 6), (-5, 7), (-5, 8), (-4, -9), (-4, -8), (-4, -7),
         (-4, -6), (-4, -5), (-4, 5), (-4, 6), (-4, 7), (-4, 8), (-4, 9), (-3, -9), (-3, -8), (-3, -7), (-3, -6),
         (-3, 6), (-3, 7), (-3, 8), (-3, 9), (-2, -9), (-2, -8), (-2, -7), (-2, -6), (-2, 6), (-2, 7), (-2, 8), (-2, 9),
         (-1, -9), (-1, -8), (-1, -7), (-1, -6), (-1, 6), (-1, 7), (-1, 8), (-1, 9), (0, -10), (0, -9), (0, -8),
         (0, -7), (0, 7), (0, 8), (0, 9), (0, 10), (1, -9), (1, -8), (1, -7), (1, -6), (1, 6), (1, 7), (1, 8), (1, 9),
         (2, -9), (2, -8), (2, -7), (2, -6), (2, 6), (2, 7), (2, 8), (2, 9), (3, -9), (3, -8), (3, -7), (3, -6), (3, 6),
         (3, 7), (3, 8), (3, 9), (4, -9), (4, -8), (4, -7), (4, -6), (4, -5), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9),
         (5, -8), (5, -7), (5, -6), (5, -5), (5, -4), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (6, -8), (6, -7), (6, -6),
         (6, -5), (6, -4), (6, -3), (6, -2), (6, -1), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8),
         (7, -7), (7, -6), (7, -5), (7, -4), (7, -3), (7, -2), (7, -1), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5),
         (7, 6), (7, 7), (8, -6), (8, -5), (8, -4), (8, -3), (8, -2), (8, -1), (8, 0), (8, 1), (8, 2), (8, 3), (8, 4),
         (8, 5), (8, 6), (9, -4), (9, -3), (9, -2), (9, -1), (9, 0), (9, 1), (9, 2), (9, 3), (9, 4), (10, 0)]
        ,
        [(-11, 0), (-10, -4), (-10, -3), (-10, -2), (-10, -1), (-10, 0), (-10, 1), (-10, 2), (-10, 3), (-10, 4),
         (-9, -6), (-9, -5), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 0), (-9, 1), (-9, 2), (-9, 3), (-9, 4),
         (-9, 5), (-9, 6), (-8, -7), (-8, -6), (-8, -5), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1),
         (-8, 2), (-8, 3), (-8, 4), (-8, 5), (-8, 6), (-8, 7), (-7, -8), (-7, -7), (-7, -6), (-7, -5), (-7, -4),
         (-7, -3), (-7, -2), (-7, -1), (-7, 0), (-7, 1), (-7, 2), (-7, 3), (-7, 4), (-7, 5), (-7, 6), (-7, 7), (-7, 8),
         (-6, -9), (-6, -8), (-6, -7), (-6, -6), (-6, -5), (-6, -4), (-6, -3), (-6, -2), (-6, -1), (-6, 1), (-6, 2),
         (-6, 3), (-6, 4), (-6, 5), (-6, 6), (-6, 7), (-6, 8), (-6, 9), (-5, -9), (-5, -8), (-5, -7), (-5, -6),
         (-5, -5), (-5, -4), (-5, 4), (-5, 5), (-5, 6), (-5, 7), (-5, 8), (-5, 9), (-4, -10), (-4, -9), (-4, -8),
         (-4, -7), (-4, -6), (-4, -5), (-4, 5), (-4, 6), (-4, 7), (-4, 8), (-4, 9), (-4, 10), (-3, -10), (-3, -9),
         (-3, -8), (-3, -7), (-3, -6), (-3, 6), (-3, 7), (-3, 8), (-3, 9), (-3, 10), (-2, -10), (-2, -9), (-2, -8),
         (-2, -7), (-2, -6), (-2, 6), (-2, 7), (-2, 8), (-2, 9), (-2, 10), (-1, -10), (-1, -9), (-1, -8), (-1, -7),
         (-1, -6), (-1, 6), (-1, 7), (-1, 8), (-1, 9), (-1, 10), (0, -11), (0, -10), (0, -9), (0, -8), (0, -7), (0, 7),
         (0, 8), (0, 9), (0, 10), (0, 11), (1, -10), (1, -9), (1, -8), (1, -7), (1, -6), (1, 6), (1, 7), (1, 8), (1, 9),
         (1, 10), (2, -10), (2, -9), (2, -8), (2, -7), (2, -6), (2, 6), (2, 7), (2, 8), (2, 9), (2, 10), (3, -10),
         (3, -9), (3, -8), (3, -7), (3, -6), (3, 6), (3, 7), (3, 8), (3, 9), (3, 10), (4, -10), (4, -9), (4, -8),
         (4, -7), (4, -6), (4, -5), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9), (4, 10), (5, -9), (5, -8), (5, -7), (5, -6),
         (5, -5), (5, -4), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (5, 9), (6, -9), (6, -8), (6, -7), (6, -6), (6, -5),
         (6, -4), (6, -3), (6, -2), (6, -1), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8), (6, 9),
         (7, -8), (7, -7), (7, -6), (7, -5), (7, -4), (7, -3), (7, -2), (7, -1), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4),
         (7, 5), (7, 6), (7, 7), (7, 8), (8, -7), (8, -6), (8, -5), (8, -4), (8, -3), (8, -2), (8, -1), (8, 0), (8, 1),
         (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (9, -6), (9, -5), (9, -4), (9, -3), (9, -2), (9, -1), (9, 0),
         (9, 1), (9, 2), (9, 3), (9, 4), (9, 5), (9, 6), (10, -4), (10, -3), (10, -2), (10, -1), (10, 0), (10, 1),
         (10, 2), (10, 3), (10, 4), (11, 0)]
        ,
        [(-12, 0), (-11, -4), (-11, -3), (-11, -2), (-11, -1), (-11, 0), (-11, 1), (-11, 2), (-11, 3), (-11, 4),
         (-10, -6), (-10, -5), (-10, -4), (-10, -3), (-10, -2), (-10, -1), (-10, 0), (-10, 1), (-10, 2), (-10, 3),
         (-10, 4), (-10, 5), (-10, 6), (-9, -7), (-9, -6), (-9, -5), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 0),
         (-9, 1), (-9, 2), (-9, 3), (-9, 4), (-9, 5), (-9, 6), (-9, 7), (-8, -8), (-8, -7), (-8, -6), (-8, -5),
         (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1), (-8, 2), (-8, 3), (-8, 4), (-8, 5), (-8, 6), (-8, 7),
         (-8, 8), (-7, -9), (-7, -8), (-7, -7), (-7, -6), (-7, -5), (-7, -4), (-7, -3), (-7, -2), (-7, -1), (-7, 0),
         (-7, 1), (-7, 2), (-7, 3), (-7, 4), (-7, 5), (-7, 6), (-7, 7), (-7, 8), (-7, 9), (-6, -10), (-6, -9), (-6, -8),
         (-6, -7), (-6, -6), (-6, -5), (-6, -4), (-6, -3), (-6, -2), (-6, -1), (-6, 1), (-6, 2), (-6, 3), (-6, 4),
         (-6, 5), (-6, 6), (-6, 7), (-6, 8), (-6, 9), (-6, 10), (-5, -10), (-5, -9), (-5, -8), (-5, -7), (-5, -6),
         (-5, -5), (-5, -4), (-5, 4), (-5, 5), (-5, 6), (-5, 7), (-5, 8), (-5, 9), (-5, 10), (-4, -11), (-4, -10),
         (-4, -9), (-4, -8), (-4, -7), (-4, -6), (-4, -5), (-4, 5), (-4, 6), (-4, 7), (-4, 8), (-4, 9), (-4, 10),
         (-4, 11), (-3, -11), (-3, -10), (-3, -9), (-3, -8), (-3, -7), (-3, -6), (-3, 6), (-3, 7), (-3, 8), (-3, 9),
         (-3, 10), (-3, 11), (-2, -11), (-2, -10), (-2, -9), (-2, -8), (-2, -7), (-2, -6), (-2, 6), (-2, 7), (-2, 8),
         (-2, 9), (-2, 10), (-2, 11), (-1, -11), (-1, -10), (-1, -9), (-1, -8), (-1, -7), (-1, -6), (-1, 6), (-1, 7),
         (-1, 8), (-1, 9), (-1, 10), (-1, 11), (0, -12), (0, -11), (0, -10), (0, -9), (0, -8), (0, -7), (0, 7), (0, 8),
         (0, 9), (0, 10), (0, 11), (0, 12), (1, -11), (1, -10), (1, -9), (1, -8), (1, -7), (1, -6), (1, 6), (1, 7),
         (1, 8), (1, 9), (1, 10), (1, 11), (2, -11), (2, -10), (2, -9), (2, -8), (2, -7), (2, -6), (2, 6), (2, 7),
         (2, 8), (2, 9), (2, 10), (2, 11), (3, -11), (3, -10), (3, -9), (3, -8), (3, -7), (3, -6), (3, 6), (3, 7),
         (3, 8), (3, 9), (3, 10), (3, 11), (4, -11), (4, -10), (4, -9), (4, -8), (4, -7), (4, -6), (4, -5), (4, 5),
         (4, 6), (4, 7), (4, 8), (4, 9), (4, 10), (4, 11), (5, -10), (5, -9), (5, -8), (5, -7), (5, -6), (5, -5),
         (5, -4), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (5, 9), (5, 10), (6, -10), (6, -9), (6, -8), (6, -7), (6, -6),
         (6, -5), (6, -4), (6, -3), (6, -2), (6, -1), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8),
         (6, 9), (6, 10), (7, -9), (7, -8), (7, -7), (7, -6), (7, -5), (7, -4), (7, -3), (7, -2), (7, -1), (7, 0),
         (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (7, 8), (7, 9), (8, -8), (8, -7), (8, -6), (8, -5),
         (8, -4), (8, -3), (8, -2), (8, -1), (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (8, 8),
         (9, -7), (9, -6), (9, -5), (9, -4), (9, -3), (9, -2), (9, -1), (9, 0), (9, 1), (9, 2), (9, 3), (9, 4), (9, 5),
         (9, 6), (9, 7), (10, -6), (10, -5), (10, -4), (10, -3), (10, -2), (10, -1), (10, 0), (10, 1), (10, 2), (10, 3),
         (10, 4), (10, 5), (10, 6), (11, -4), (11, -3), (11, -2), (11, -1), (11, 0), (11, 1), (11, 2), (11, 3), (11, 4),
         (12, 0)]

    ],
    [
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [(-8, 0), (-7, -3), (-7, -2), (-7, -1), (-7, 1), (-7, 2), (-7, 3), (-6, -5), (-6, -4), (-6, 4), (-6, 5),
         (-5, -6), (-5, -5), (-5, 5), (-5, 6), (-4, -6), (-4, 6), (-3, -7), (-3, 7), (-2, -7), (-2, 7), (-1, -7),
         (-1, 7), (0, -8), (0, 8), (1, -7), (1, 7), (2, -7), (2, 7), (3, -7), (3, 7), (4, -6), (4, 6), (5, -6), (5, -5),
         (5, 5), (5, 6), (6, -5), (6, -4), (6, 4), (6, 5), (7, -3), (7, -2), (7, -1), (7, 1), (7, 2), (7, 3), (8, 0)]
        ,
        [(-9, 0), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1), (-8, 2), (-8, 3), (-8, 4), (-7, -5),
         (-7, -4), (-7, -3), (-7, -2), (-7, -1), (-7, 1), (-7, 2), (-7, 3), (-7, 4), (-7, 5), (-6, -6), (-6, -5),
         (-6, -4), (-6, 4), (-6, 5), (-6, 6), (-5, -7), (-5, -6), (-5, -5), (-5, 5), (-5, 6), (-5, 7), (-4, -8),
         (-4, -7), (-4, -6), (-4, 6), (-4, 7), (-4, 8), (-3, -8), (-3, -7), (-3, 7), (-3, 8), (-2, -8), (-2, -7),
         (-2, 7), (-2, 8), (-1, -8), (-1, -7), (-1, 7), (-1, 8), (0, -9), (0, -8), (0, 8), (0, 9), (1, -8), (1, -7),
         (1, 7), (1, 8), (2, -8), (2, -7), (2, 7), (2, 8), (3, -8), (3, -7), (3, 7), (3, 8), (4, -8), (4, -7), (4, -6),
         (4, 6), (4, 7), (4, 8), (5, -7), (5, -6), (5, -5), (5, 5), (5, 6), (5, 7), (6, -6), (6, -5), (6, -4), (6, 4),
         (6, 5), (6, 6), (7, -5), (7, -4), (7, -3), (7, -2), (7, -1), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (8, -4),
         (8, -3), (8, -2), (8, -1), (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (9, 0)]
        ,
        [(-10, 0), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 0), (-9, 1), (-9, 2), (-9, 3), (-9, 4), (-8, -6),
         (-8, -5), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1), (-8, 2), (-8, 3), (-8, 4), (-8, 5),
         (-8, 6), (-7, -7), (-7, -6), (-7, -5), (-7, -4), (-7, -3), (-7, -2), (-7, -1), (-7, 1), (-7, 2), (-7, 3),
         (-7, 4), (-7, 5), (-7, 6), (-7, 7), (-6, -8), (-6, -7), (-6, -6), (-6, -5), (-6, -4), (-6, 4), (-6, 5),
         (-6, 6), (-6, 7), (-6, 8), (-5, -8), (-5, -7), (-5, -6), (-5, -5), (-5, 5), (-5, 6), (-5, 7), (-5, 8),
         (-4, -9), (-4, -8), (-4, -7), (-4, -6), (-4, 6), (-4, 7), (-4, 8), (-4, 9), (-3, -9), (-3, -8), (-3, -7),
         (-3, 7), (-3, 8), (-3, 9), (-2, -9), (-2, -8), (-2, -7), (-2, 7), (-2, 8), (-2, 9), (-1, -9), (-1, -8),
         (-1, -7), (-1, 7), (-1, 8), (-1, 9), (0, -10), (0, -9), (0, -8), (0, 8), (0, 9), (0, 10), (1, -9), (1, -8),
         (1, -7), (1, 7), (1, 8), (1, 9), (2, -9), (2, -8), (2, -7), (2, 7), (2, 8), (2, 9), (3, -9), (3, -8), (3, -7),
         (3, 7), (3, 8), (3, 9), (4, -9), (4, -8), (4, -7), (4, -6), (4, 6), (4, 7), (4, 8), (4, 9), (5, -8), (5, -7),
         (5, -6), (5, -5), (5, 5), (5, 6), (5, 7), (5, 8), (6, -8), (6, -7), (6, -6), (6, -5), (6, -4), (6, 4), (6, 5),
         (6, 6), (6, 7), (6, 8), (7, -7), (7, -6), (7, -5), (7, -4), (7, -3), (7, -2), (7, -1), (7, 1), (7, 2), (7, 3),
         (7, 4), (7, 5), (7, 6), (7, 7), (8, -6), (8, -5), (8, -4), (8, -3), (8, -2), (8, -1), (8, 0), (8, 1), (8, 2),
         (8, 3), (8, 4), (8, 5), (8, 6), (9, -4), (9, -3), (9, -2), (9, -1), (9, 0), (9, 1), (9, 2), (9, 3), (9, 4),
         (10, 0)]
        ,
        [(-11, 0), (-10, -4), (-10, -3), (-10, -2), (-10, -1), (-10, 0), (-10, 1), (-10, 2), (-10, 3), (-10, 4),
         (-9, -6), (-9, -5), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 0), (-9, 1), (-9, 2), (-9, 3), (-9, 4),
         (-9, 5), (-9, 6), (-8, -7), (-8, -6), (-8, -5), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1),
         (-8, 2), (-8, 3), (-8, 4), (-8, 5), (-8, 6), (-8, 7), (-7, -8), (-7, -7), (-7, -6), (-7, -5), (-7, -4),
         (-7, -3), (-7, -2), (-7, -1), (-7, 1), (-7, 2), (-7, 3), (-7, 4), (-7, 5), (-7, 6), (-7, 7), (-7, 8), (-6, -9),
         (-6, -8), (-6, -7), (-6, -6), (-6, -5), (-6, -4), (-6, 4), (-6, 5), (-6, 6), (-6, 7), (-6, 8), (-6, 9),
         (-5, -9), (-5, -8), (-5, -7), (-5, -6), (-5, -5), (-5, 5), (-5, 6), (-5, 7), (-5, 8), (-5, 9), (-4, -10),
         (-4, -9), (-4, -8), (-4, -7), (-4, -6), (-4, 6), (-4, 7), (-4, 8), (-4, 9), (-4, 10), (-3, -10), (-3, -9),
         (-3, -8), (-3, -7), (-3, 7), (-3, 8), (-3, 9), (-3, 10), (-2, -10), (-2, -9), (-2, -8), (-2, -7), (-2, 7),
         (-2, 8), (-2, 9), (-2, 10), (-1, -10), (-1, -9), (-1, -8), (-1, -7), (-1, 7), (-1, 8), (-1, 9), (-1, 10),
         (0, -11), (0, -10), (0, -9), (0, -8), (0, 8), (0, 9), (0, 10), (0, 11), (1, -10), (1, -9), (1, -8), (1, -7),
         (1, 7), (1, 8), (1, 9), (1, 10), (2, -10), (2, -9), (2, -8), (2, -7), (2, 7), (2, 8), (2, 9), (2, 10),
         (3, -10), (3, -9), (3, -8), (3, -7), (3, 7), (3, 8), (3, 9), (3, 10), (4, -10), (4, -9), (4, -8), (4, -7),
         (4, -6), (4, 6), (4, 7), (4, 8), (4, 9), (4, 10), (5, -9), (5, -8), (5, -7), (5, -6), (5, -5), (5, 5), (5, 6),
         (5, 7), (5, 8), (5, 9), (6, -9), (6, -8), (6, -7), (6, -6), (6, -5), (6, -4), (6, 4), (6, 5), (6, 6), (6, 7),
         (6, 8), (6, 9), (7, -8), (7, -7), (7, -6), (7, -5), (7, -4), (7, -3), (7, -2), (7, -1), (7, 1), (7, 2), (7, 3),
         (7, 4), (7, 5), (7, 6), (7, 7), (7, 8), (8, -7), (8, -6), (8, -5), (8, -4), (8, -3), (8, -2), (8, -1), (8, 0),
         (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (9, -6), (9, -5), (9, -4), (9, -3), (9, -2), (9, -1),
         (9, 0), (9, 1), (9, 2), (9, 3), (9, 4), (9, 5), (9, 6), (10, -4), (10, -3), (10, -2), (10, -1), (10, 0),
         (10, 1), (10, 2), (10, 3), (10, 4), (11, 0)]
        ,
        [(-12, 0), (-11, -4), (-11, -3), (-11, -2), (-11, -1), (-11, 0), (-11, 1), (-11, 2), (-11, 3), (-11, 4),
         (-10, -6), (-10, -5), (-10, -4), (-10, -3), (-10, -2), (-10, -1), (-10, 0), (-10, 1), (-10, 2), (-10, 3),
         (-10, 4), (-10, 5), (-10, 6), (-9, -7), (-9, -6), (-9, -5), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 0),
         (-9, 1), (-9, 2), (-9, 3), (-9, 4), (-9, 5), (-9, 6), (-9, 7), (-8, -8), (-8, -7), (-8, -6), (-8, -5),
         (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 0), (-8, 1), (-8, 2), (-8, 3), (-8, 4), (-8, 5), (-8, 6), (-8, 7),
         (-8, 8), (-7, -9), (-7, -8), (-7, -7), (-7, -6), (-7, -5), (-7, -4), (-7, -3), (-7, -2), (-7, -1), (-7, 1),
         (-7, 2), (-7, 3), (-7, 4), (-7, 5), (-7, 6), (-7, 7), (-7, 8), (-7, 9), (-6, -10), (-6, -9), (-6, -8),
         (-6, -7), (-6, -6), (-6, -5), (-6, -4), (-6, 4), (-6, 5), (-6, 6), (-6, 7), (-6, 8), (-6, 9), (-6, 10),
         (-5, -10), (-5, -9), (-5, -8), (-5, -7), (-5, -6), (-5, -5), (-5, 5), (-5, 6), (-5, 7), (-5, 8), (-5, 9),
         (-5, 10), (-4, -11), (-4, -10), (-4, -9), (-4, -8), (-4, -7), (-4, -6), (-4, 6), (-4, 7), (-4, 8), (-4, 9),
         (-4, 10), (-4, 11), (-3, -11), (-3, -10), (-3, -9), (-3, -8), (-3, -7), (-3, 7), (-3, 8), (-3, 9), (-3, 10),
         (-3, 11), (-2, -11), (-2, -10), (-2, -9), (-2, -8), (-2, -7), (-2, 7), (-2, 8), (-2, 9), (-2, 10), (-2, 11),
         (-1, -11), (-1, -10), (-1, -9), (-1, -8), (-1, -7), (-1, 7), (-1, 8), (-1, 9), (-1, 10), (-1, 11), (0, -12),
         (0, -11), (0, -10), (0, -9), (0, -8), (0, 8), (0, 9), (0, 10), (0, 11), (0, 12), (1, -11), (1, -10), (1, -9),
         (1, -8), (1, -7), (1, 7), (1, 8), (1, 9), (1, 10), (1, 11), (2, -11), (2, -10), (2, -9), (2, -8), (2, -7),
         (2, 7), (2, 8), (2, 9), (2, 10), (2, 11), (3, -11), (3, -10), (3, -9), (3, -8), (3, -7), (3, 7), (3, 8),
         (3, 9), (3, 10), (3, 11), (4, -11), (4, -10), (4, -9), (4, -8), (4, -7), (4, -6), (4, 6), (4, 7), (4, 8),
         (4, 9), (4, 10), (4, 11), (5, -10), (5, -9), (5, -8), (5, -7), (5, -6), (5, -5), (5, 5), (5, 6), (5, 7),
         (5, 8), (5, 9), (5, 10), (6, -10), (6, -9), (6, -8), (6, -7), (6, -6), (6, -5), (6, -4), (6, 4), (6, 5),
         (6, 6), (6, 7), (6, 8), (6, 9), (6, 10), (7, -9), (7, -8), (7, -7), (7, -6), (7, -5), (7, -4), (7, -3),
         (7, -2), (7, -1), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (7, 8), (7, 9), (8, -8), (8, -7),
         (8, -6), (8, -5), (8, -4), (8, -3), (8, -2), (8, -1), (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6),
         (8, 7), (8, 8), (9, -7), (9, -6), (9, -5), (9, -4), (9, -3), (9, -2), (9, -1), (9, 0), (9, 1), (9, 2), (9, 3),
         (9, 4), (9, 5), (9, 6), (9, 7), (10, -6), (10, -5), (10, -4), (10, -3), (10, -2), (10, -1), (10, 0), (10, 1),
         (10, 2), (10, 3), (10, 4), (10, 5), (10, 6), (11, -4), (11, -3), (11, -2), (11, -1), (11, 0), (11, 1), (11, 2),
         (11, 3), (11, 4), (12, 0)]

    ],
    [
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [(-9, 0), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 1), (-8, 2), (-8, 3), (-8, 4), (-7, -5), (-7, -4),
         (-7, 4), (-7, 5), (-6, -6), (-6, 6), (-5, -7), (-5, 7), (-4, -8), (-4, -7), (-4, 7), (-4, 8), (-3, -8),
         (-3, 8), (-2, -8), (-2, 8), (-1, -8), (-1, 8), (0, -9), (0, 9), (1, -8), (1, 8), (2, -8), (2, 8), (3, -8),
         (3, 8), (4, -8), (4, -7), (4, 7), (4, 8), (5, -7), (5, 7), (6, -6), (6, 6), (7, -5), (7, -4), (7, 4), (7, 5),
         (8, -4), (8, -3), (8, -2), (8, -1), (8, 1), (8, 2), (8, 3), (8, 4), (9, 0)]
        ,
        [(-10, 0), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 0), (-9, 1), (-9, 2), (-9, 3), (-9, 4), (-8, -6),
         (-8, -5), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 1), (-8, 2), (-8, 3), (-8, 4), (-8, 5), (-8, 6),
         (-7, -7), (-7, -6), (-7, -5), (-7, -4), (-7, 4), (-7, 5), (-7, 6), (-7, 7), (-6, -8), (-6, -7), (-6, -6),
         (-6, 6), (-6, 7), (-6, 8), (-5, -8), (-5, -7), (-5, 7), (-5, 8), (-4, -9), (-4, -8), (-4, -7), (-4, 7),
         (-4, 8), (-4, 9), (-3, -9), (-3, -8), (-3, 8), (-3, 9), (-2, -9), (-2, -8), (-2, 8), (-2, 9), (-1, -9),
         (-1, -8), (-1, 8), (-1, 9), (0, -10), (0, -9), (0, 9), (0, 10), (1, -9), (1, -8), (1, 8), (1, 9), (2, -9),
         (2, -8), (2, 8), (2, 9), (3, -9), (3, -8), (3, 8), (3, 9), (4, -9), (4, -8), (4, -7), (4, 7), (4, 8), (4, 9),
         (5, -8), (5, -7), (5, 7), (5, 8), (6, -8), (6, -7), (6, -6), (6, 6), (6, 7), (6, 8), (7, -7), (7, -6), (7, -5),
         (7, -4), (7, 4), (7, 5), (7, 6), (7, 7), (8, -6), (8, -5), (8, -4), (8, -3), (8, -2), (8, -1), (8, 1), (8, 2),
         (8, 3), (8, 4), (8, 5), (8, 6), (9, -4), (9, -3), (9, -2), (9, -1), (9, 0), (9, 1), (9, 2), (9, 3), (9, 4),
         (10, 0)]
        ,
        [(-11, 0), (-10, -4), (-10, -3), (-10, -2), (-10, -1), (-10, 0), (-10, 1), (-10, 2), (-10, 3), (-10, 4),
         (-9, -6), (-9, -5), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 0), (-9, 1), (-9, 2), (-9, 3), (-9, 4),
         (-9, 5), (-9, 6), (-8, -7), (-8, -6), (-8, -5), (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 1), (-8, 2),
         (-8, 3), (-8, 4), (-8, 5), (-8, 6), (-8, 7), (-7, -8), (-7, -7), (-7, -6), (-7, -5), (-7, -4), (-7, 4),
         (-7, 5), (-7, 6), (-7, 7), (-7, 8), (-6, -9), (-6, -8), (-6, -7), (-6, -6), (-6, 6), (-6, 7), (-6, 8), (-6, 9),
         (-5, -9), (-5, -8), (-5, -7), (-5, 7), (-5, 8), (-5, 9), (-4, -10), (-4, -9), (-4, -8), (-4, -7), (-4, 7),
         (-4, 8), (-4, 9), (-4, 10), (-3, -10), (-3, -9), (-3, -8), (-3, 8), (-3, 9), (-3, 10), (-2, -10), (-2, -9),
         (-2, -8), (-2, 8), (-2, 9), (-2, 10), (-1, -10), (-1, -9), (-1, -8), (-1, 8), (-1, 9), (-1, 10), (0, -11),
         (0, -10), (0, -9), (0, 9), (0, 10), (0, 11), (1, -10), (1, -9), (1, -8), (1, 8), (1, 9), (1, 10), (2, -10),
         (2, -9), (2, -8), (2, 8), (2, 9), (2, 10), (3, -10), (3, -9), (3, -8), (3, 8), (3, 9), (3, 10), (4, -10),
         (4, -9), (4, -8), (4, -7), (4, 7), (4, 8), (4, 9), (4, 10), (5, -9), (5, -8), (5, -7), (5, 7), (5, 8), (5, 9),
         (6, -9), (6, -8), (6, -7), (6, -6), (6, 6), (6, 7), (6, 8), (6, 9), (7, -8), (7, -7), (7, -6), (7, -5),
         (7, -4), (7, 4), (7, 5), (7, 6), (7, 7), (7, 8), (8, -7), (8, -6), (8, -5), (8, -4), (8, -3), (8, -2), (8, -1),
         (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (9, -6), (9, -5), (9, -4), (9, -3), (9, -2), (9, -1),
         (9, 0), (9, 1), (9, 2), (9, 3), (9, 4), (9, 5), (9, 6), (10, -4), (10, -3), (10, -2), (10, -1), (10, 0),
         (10, 1), (10, 2), (10, 3), (10, 4), (11, 0)]
        ,
        [(-12, 0), (-11, -4), (-11, -3), (-11, -2), (-11, -1), (-11, 0), (-11, 1), (-11, 2), (-11, 3), (-11, 4),
         (-10, -6), (-10, -5), (-10, -4), (-10, -3), (-10, -2), (-10, -1), (-10, 0), (-10, 1), (-10, 2), (-10, 3),
         (-10, 4), (-10, 5), (-10, 6), (-9, -7), (-9, -6), (-9, -5), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 0),
         (-9, 1), (-9, 2), (-9, 3), (-9, 4), (-9, 5), (-9, 6), (-9, 7), (-8, -8), (-8, -7), (-8, -6), (-8, -5),
         (-8, -4), (-8, -3), (-8, -2), (-8, -1), (-8, 1), (-8, 2), (-8, 3), (-8, 4), (-8, 5), (-8, 6), (-8, 7), (-8, 8),
         (-7, -9), (-7, -8), (-7, -7), (-7, -6), (-7, -5), (-7, -4), (-7, 4), (-7, 5), (-7, 6), (-7, 7), (-7, 8),
         (-7, 9), (-6, -10), (-6, -9), (-6, -8), (-6, -7), (-6, -6), (-6, 6), (-6, 7), (-6, 8), (-6, 9), (-6, 10),
         (-5, -10), (-5, -9), (-5, -8), (-5, -7), (-5, 7), (-5, 8), (-5, 9), (-5, 10), (-4, -11), (-4, -10), (-4, -9),
         (-4, -8), (-4, -7), (-4, 7), (-4, 8), (-4, 9), (-4, 10), (-4, 11), (-3, -11), (-3, -10), (-3, -9), (-3, -8),
         (-3, 8), (-3, 9), (-3, 10), (-3, 11), (-2, -11), (-2, -10), (-2, -9), (-2, -8), (-2, 8), (-2, 9), (-2, 10),
         (-2, 11), (-1, -11), (-1, -10), (-1, -9), (-1, -8), (-1, 8), (-1, 9), (-1, 10), (-1, 11), (0, -12), (0, -11),
         (0, -10), (0, -9), (0, 9), (0, 10), (0, 11), (0, 12), (1, -11), (1, -10), (1, -9), (1, -8), (1, 8), (1, 9),
         (1, 10), (1, 11), (2, -11), (2, -10), (2, -9), (2, -8), (2, 8), (2, 9), (2, 10), (2, 11), (3, -11), (3, -10),
         (3, -9), (3, -8), (3, 8), (3, 9), (3, 10), (3, 11), (4, -11), (4, -10), (4, -9), (4, -8), (4, -7), (4, 7),
         (4, 8), (4, 9), (4, 10), (4, 11), (5, -10), (5, -9), (5, -8), (5, -7), (5, 7), (5, 8), (5, 9), (5, 10),
         (6, -10), (6, -9), (6, -8), (6, -7), (6, -6), (6, 6), (6, 7), (6, 8), (6, 9), (6, 10), (7, -9), (7, -8),
         (7, -7), (7, -6), (7, -5), (7, -4), (7, 4), (7, 5), (7, 6), (7, 7), (7, 8), (7, 9), (8, -8), (8, -7), (8, -6),
         (8, -5), (8, -4), (8, -3), (8, -2), (8, -1), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (8, 8),
         (9, -7), (9, -6), (9, -5), (9, -4), (9, -3), (9, -2), (9, -1), (9, 0), (9, 1), (9, 2), (9, 3), (9, 4), (9, 5),
         (9, 6), (9, 7), (10, -6), (10, -5), (10, -4), (10, -3), (10, -2), (10, -1), (10, 0), (10, 1), (10, 2), (10, 3),
         (10, 4), (10, 5), (10, 6), (11, -4), (11, -3), (11, -2), (11, -1), (11, 0), (11, 1), (11, 2), (11, 3), (11, 4),
         (12, 0)]

    ],
    [
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [(-10, 0), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 1), (-9, 2), (-9, 3), (-9, 4), (-8, -6), (-8, -5),
         (-8, 5), (-8, 6), (-7, -7), (-7, -6), (-7, 6), (-7, 7), (-6, -8), (-6, -7), (-6, 7), (-6, 8), (-5, -8),
         (-5, 8), (-4, -9), (-4, 9), (-3, -9), (-3, 9), (-2, -9), (-2, 9), (-1, -9), (-1, 9), (0, -10), (0, 10),
         (1, -9), (1, 9), (2, -9), (2, 9), (3, -9), (3, 9), (4, -9), (4, 9), (5, -8), (5, 8), (6, -8), (6, -7), (6, 7),
         (6, 8), (7, -7), (7, -6), (7, 6), (7, 7), (8, -6), (8, -5), (8, 5), (8, 6), (9, -4), (9, -3), (9, -2), (9, -1),
         (9, 1), (9, 2), (9, 3), (9, 4), (10, 0)]
        ,
        [(-11, 0), (-10, -4), (-10, -3), (-10, -2), (-10, -1), (-10, 0), (-10, 1), (-10, 2), (-10, 3), (-10, 4),
         (-9, -6), (-9, -5), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 1), (-9, 2), (-9, 3), (-9, 4), (-9, 5),
         (-9, 6), (-8, -7), (-8, -6), (-8, -5), (-8, 5), (-8, 6), (-8, 7), (-7, -8), (-7, -7), (-7, -6), (-7, 6),
         (-7, 7), (-7, 8), (-6, -9), (-6, -8), (-6, -7), (-6, 7), (-6, 8), (-6, 9), (-5, -9), (-5, -8), (-5, 8),
         (-5, 9), (-4, -10), (-4, -9), (-4, 9), (-4, 10), (-3, -10), (-3, -9), (-3, 9), (-3, 10), (-2, -10), (-2, -9),
         (-2, 9), (-2, 10), (-1, -10), (-1, -9), (-1, 9), (-1, 10), (0, -11), (0, -10), (0, 10), (0, 11), (1, -10),
         (1, -9), (1, 9), (1, 10), (2, -10), (2, -9), (2, 9), (2, 10), (3, -10), (3, -9), (3, 9), (3, 10), (4, -10),
         (4, -9), (4, 9), (4, 10), (5, -9), (5, -8), (5, 8), (5, 9), (6, -9), (6, -8), (6, -7), (6, 7), (6, 8), (6, 9),
         (7, -8), (7, -7), (7, -6), (7, 6), (7, 7), (7, 8), (8, -7), (8, -6), (8, -5), (8, 5), (8, 6), (8, 7), (9, -6),
         (9, -5), (9, -4), (9, -3), (9, -2), (9, -1), (9, 1), (9, 2), (9, 3), (9, 4), (9, 5), (9, 6), (10, -4),
         (10, -3), (10, -2), (10, -1), (10, 0), (10, 1), (10, 2), (10, 3), (10, 4), (11, 0)]
        ,
        [(-12, 0), (-11, -4), (-11, -3), (-11, -2), (-11, -1), (-11, 0), (-11, 1), (-11, 2), (-11, 3), (-11, 4),
         (-10, -6), (-10, -5), (-10, -4), (-10, -3), (-10, -2), (-10, -1), (-10, 0), (-10, 1), (-10, 2), (-10, 3),
         (-10, 4), (-10, 5), (-10, 6), (-9, -7), (-9, -6), (-9, -5), (-9, -4), (-9, -3), (-9, -2), (-9, -1), (-9, 1),
         (-9, 2), (-9, 3), (-9, 4), (-9, 5), (-9, 6), (-9, 7), (-8, -8), (-8, -7), (-8, -6), (-8, -5), (-8, 5), (-8, 6),
         (-8, 7), (-8, 8), (-7, -9), (-7, -8), (-7, -7), (-7, -6), (-7, 6), (-7, 7), (-7, 8), (-7, 9), (-6, -10),
         (-6, -9), (-6, -8), (-6, -7), (-6, 7), (-6, 8), (-6, 9), (-6, 10), (-5, -10), (-5, -9), (-5, -8), (-5, 8),
         (-5, 9), (-5, 10), (-4, -11), (-4, -10), (-4, -9), (-4, 9), (-4, 10), (-4, 11), (-3, -11), (-3, -10), (-3, -9),
         (-3, 9), (-3, 10), (-3, 11), (-2, -11), (-2, -10), (-2, -9), (-2, 9), (-2, 10), (-2, 11), (-1, -11), (-1, -10),
         (-1, -9), (-1, 9), (-1, 10), (-1, 11), (0, -12), (0, -11), (0, -10), (0, 10), (0, 11), (0, 12), (1, -11),
         (1, -10), (1, -9), (1, 9), (1, 10), (1, 11), (2, -11), (2, -10), (2, -9), (2, 9), (2, 10), (2, 11), (3, -11),
         (3, -10), (3, -9), (3, 9), (3, 10), (3, 11), (4, -11), (4, -10), (4, -9), (4, 9), (4, 10), (4, 11), (5, -10),
         (5, -9), (5, -8), (5, 8), (5, 9), (5, 10), (6, -10), (6, -9), (6, -8), (6, -7), (6, 7), (6, 8), (6, 9),
         (6, 10), (7, -9), (7, -8), (7, -7), (7, -6), (7, 6), (7, 7), (7, 8), (7, 9), (8, -8), (8, -7), (8, -6),
         (8, -5), (8, 5), (8, 6), (8, 7), (8, 8), (9, -7), (9, -6), (9, -5), (9, -4), (9, -3), (9, -2), (9, -1), (9, 1),
         (9, 2), (9, 3), (9, 4), (9, 5), (9, 6), (9, 7), (10, -6), (10, -5), (10, -4), (10, -3), (10, -2), (10, -1),
         (10, 0), (10, 1), (10, 2), (10, 3), (10, 4), (10, 5), (10, 6), (11, -4), (11, -3), (11, -2), (11, -1), (11, 0),
         (11, 1), (11, 2), (11, 3), (11, 4), (12, 0)]

    ],
    [
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [(-11, 0), (-10, -4), (-10, -3), (-10, -2), (-10, -1), (-10, 1), (-10, 2), (-10, 3), (-10, 4), (-9, -6),
         (-9, -5), (-9, 5), (-9, 6), (-8, -7), (-8, 7), (-7, -8), (-7, 8), (-6, -9), (-6, 9), (-5, -9), (-5, 9),
         (-4, -10), (-4, 10), (-3, -10), (-3, 10), (-2, -10), (-2, 10), (-1, -10), (-1, 10), (0, -11), (0, 11),
         (1, -10), (1, 10), (2, -10), (2, 10), (3, -10), (3, 10), (4, -10), (4, 10), (5, -9), (5, 9), (6, -9), (6, 9),
         (7, -8), (7, 8), (8, -7), (8, 7), (9, -6), (9, -5), (9, 5), (9, 6), (10, -4), (10, -3), (10, -2), (10, -1),
         (10, 1), (10, 2), (10, 3), (10, 4), (11, 0)]
        ,
        [(-12, 0), (-11, -4), (-11, -3), (-11, -2), (-11, -1), (-11, 0), (-11, 1), (-11, 2), (-11, 3), (-11, 4),
         (-10, -6), (-10, -5), (-10, -4), (-10, -3), (-10, -2), (-10, -1), (-10, 1), (-10, 2), (-10, 3), (-10, 4),
         (-10, 5), (-10, 6), (-9, -7), (-9, -6), (-9, -5), (-9, 5), (-9, 6), (-9, 7), (-8, -8), (-8, -7), (-8, 7),
         (-8, 8), (-7, -9), (-7, -8), (-7, 8), (-7, 9), (-6, -10), (-6, -9), (-6, 9), (-6, 10), (-5, -10), (-5, -9),
         (-5, 9), (-5, 10), (-4, -11), (-4, -10), (-4, 10), (-4, 11), (-3, -11), (-3, -10), (-3, 10), (-3, 11),
         (-2, -11), (-2, -10), (-2, 10), (-2, 11), (-1, -11), (-1, -10), (-1, 10), (-1, 11), (0, -12), (0, -11),
         (0, 11), (0, 12), (1, -11), (1, -10), (1, 10), (1, 11), (2, -11), (2, -10), (2, 10), (2, 11), (3, -11),
         (3, -10), (3, 10), (3, 11), (4, -11), (4, -10), (4, 10), (4, 11), (5, -10), (5, -9), (5, 9), (5, 10), (6, -10),
         (6, -9), (6, 9), (6, 10), (7, -9), (7, -8), (7, 8), (7, 9), (8, -8), (8, -7), (8, 7), (8, 8), (9, -7), (9, -6),
         (9, -5), (9, 5), (9, 6), (9, 7), (10, -6), (10, -5), (10, -4), (10, -3), (10, -2), (10, -1), (10, 1), (10, 2),
         (10, 3), (10, 4), (10, 5), (10, 6), (11, -4), (11, -3), (11, -2), (11, -1), (11, 0), (11, 1), (11, 2), (11, 3),
         (11, 4), (12, 0)]

    ],
    [
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [(-12, 0), (-11, -4), (-11, -3), (-11, -2), (-11, -1), (-11, 1), (-11, 2), (-11, 3), (-11, 4), (-10, -6),
         (-10, -5), (-10, 5), (-10, 6), (-9, -7), (-9, 7), (-8, -8), (-8, 8), (-7, -9), (-7, 9), (-6, -10), (-6, 10),
         (-5, -10), (-5, 10), (-4, -11), (-4, 11), (-3, -11), (-3, 11), (-2, -11), (-2, 11), (-1, -11), (-1, 11),
         (0, -12), (0, 12), (1, -11), (1, 11), (2, -11), (2, 11), (3, -11), (3, 11), (4, -11), (4, 11), (5, -10),
         (5, 10), (6, -10), (6, 10), (7, -9), (7, 9), (8, -8), (8, 8), (9, -7), (9, 7), (10, -6), (10, -5), (10, 5),
         (10, 6), (11, -4), (11, -3), (11, -2), (11, -1), (11, 1), (11, 2), (11, 3), (11, 4), (12, 0)]

    ],
    [
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        []
    ]
]


def tiles_in_range(r_squared):
    """
    tiles in range squared
    :param r: r squared
    :return: list of tiles in range
    """
    r = int(math.sqrt(r_squared))
    if r > 0 and r <= len(RANGES):
        return RANGES[r]
    else:
        return []


def ring(r_min_sq, r_max_sq):
    """
    tiles in the ring between 2 ranges
    :param r: r squared
    :return: list of tiles in the ring
    """
    r_min = int(math.sqrt(r_min_sq))
    r_max = int(math.sqrt(r_max_sq))
    if r_min > 0 and r_min <= len(RINGS) and r_max > 0 and r_max <= len(RINGS):
        return RINGS[r_min][r_max]
    else:
        return []


#
#
# from battlecode import BCAbstractRobot, SPECS
# import battlecode as bc
# import random
# import time

# from bots.first_bot.utils import *


DIRECTIONS = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]

WALKING_DIRECTIONS = [(-2, 0), (-1, -1), (-1, 0), (-1, 1), (0, -2), (0, -1), (0, 0), (0, 1), (0, 2), (1, -1), (1, 0),
                      (1, 1),
                      (2, 0)]

EXTENDED_WALKING_DIRECTIONS = [(-3, 0), (-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2), (-1, -2), (-1, -1), (-1, 0),
                               (-1, 1), (-1, 2),
                               (0, -3), (0, -2), (0, -1), (0, 0), (0, 1), (0, 2), (0, 3), (1, -2), (1, -1), (1, 0),
                               (1, 1), (1, 2), (2, -2),
                               (2, -1), (2, 0), (2, 1), (2, 2), (3, 0)]


# rotate_arr = [
#     (0, 1),
#     (1, 1),
#     (1, 0),
#     (1, -1),
#     (0, -1),
#     (-1, -1),
#     (-1, 0),
#     (-1, 1)
# ]


# Adjacent tiles
def adjacent_tiles(self, x, y):
    map_size = len(self.passable_map[0])
    adjacent = [(x + dx, y + dy) for dx, dy in DIRECTIONS
                if ((x + dx) >= 0) and
                ((x + dx) < map_size) and
                ((y + dy) >= 0) and
                ((y + dy) < map_size)]
    return adjacent


# Adjacent tiles
def walking_tiles(self, x, y):
    map_size = len(self.passable_map[0])
    adjacent = [(x + dx, y + dy) for dx, dy in WALKING_DIRECTIONS
                if ((x + dx) >= 0) and
                ((x + dx) < map_size) and
                ((y + dy) >= 0) and
                ((y + dy) < map_size)]
    return adjacent


# Adjacent tiles
def extended_walking_tiles(self, x, y):
    map_size = len(self.passable_map[0])
    adjacent = [(x + dx, y + dy) for dx, dy in EXTENDED_WALKING_DIRECTIONS
                if ((x + dx) >= 0) and
                ((x + dx) < map_size) and
                ((y + dy) >= 0) and
                ((y + dy) < map_size)]
    return adjacent


# Passable adjacent tiles
def passable_adjacent_tiles(self, x, y):
    adjacents = adjacent_tiles(self, x, y)
    passable_adjacents = [(ax, ay) for ax, ay in adjacents if is_not_occupied(self, ax, ay)]
    return passable_adjacents


# Passable adjacent tiles
def passable_movement_tiles(self, x, y):
    if self.me.unit == SPECS["CRUSADER"]:
        adjacents = extended_walking_tiles(self, x, y)
    else:
        adjacents = walking_tiles(self, x, y)
    passable_adjacents = [(ax, ay) for ax, ay in adjacents if is_not_occupied(self, ax, ay)]
    return passable_adjacents


# Passable adjacent tiles FASTER VERSION
def walkable_adjacent_tiles(self, x, y):
    adjacents = walking_tiles(self, x, y)
    passable_adjacents = [(ax, ay) for ax, ay in adjacents if is_walkable(self, ax, ay)]
    return passable_adjacents


# TODO test
# tiles within range
def in_range_tiles(loc, r):
    """

    :param self: robot object
    :param x:
    :param y:
    :param r: radius squared
    :return:
    """
    x, y = loc
    tiles = [(x + t[0], y + t[1]) for t in tiles_in_range(r)]
    return tiles


def movable_tiles(self):
    # TODO do it
    return


def my_loc(self):
    """
    my location
    :param self: robot_object
    :return: x, y
    """
    return self.me.x, self.me.y


# def locate(robot):
#     """
#     Location of a robot class
#     :param robot:
#     :return:
#     """
#     return robot.x, robot.y

def difference_to(origin, destination):
    """

    :param origin: location
    :param destination:
    :return: (destination - origin) vector
    """
    if origin is None or destination is None:
        return (0, 0)

    dx = destination[0] - origin[0]
    dy = destination[1] - origin[1]

    return (dx, dy)


def add_dir(loc, dir):
    """

    :param loc: tuple
    :param dir: tuple
    :return:  loc + dir
    """
    return (loc[0] + dir[0], loc[1] + dir[1])


def direction_to(origin, destination):
    """

    :param origin: location
    :param destination:
    :return: direction
    """
    if origin is None or destination is None:
        return (0, 0)

    dx = destination[0] - origin[0]
    dy = destination[1] - origin[1]

    if dx < 0:
        dx = -1
    elif dx > 0:
        dx = 1
    if dy < 0:
        dy = -1
    elif dy > 0:
        dy = 1

    return (dx, dy)


def distance(origin, destination):
    """

    :param origin: location
    :param destination:
    :return: distance squared
    """
    if origin is None or destination is None:
        return -1

    dx = destination[0] - origin[0]
    dy = destination[1] - origin[1]

    return (dx ** 2 + dy ** 2)


def man_distance(origin, destination):
    """ manhattan distance
    :param origin: location
    :param destination:
    :return: manhattan distance
    """
    if origin is None or destination is None:
        return -1

    dx = destination[0] - origin[0]
    dy = destination[1] - origin[1]
    return (abs(dx) + abs(dy))


def jump_directions(bc, dir):
    """
    gets the possible moves apart from the ones 1 tile away
    :param bc: battlecode object
    :param dir: direction to search
    :return: list of extended directions within move range
    """
    jumps = []

    if bc.me.unit == SPECS['CRUSADER']:
        if dir[1] != 0:
            jumps.append((dir[0], 2 * dir[1]))
        if dir[0] != 0:
            jumps.append((2 * dir[0], dir[1]))
        if dir[0] == 0:
            jumps.append((dir[0], 3 * dir[1]))
        if dir[1] == 0:
            jumps.append((3 * dir[0], dir[1]))
        return jumps

    if dir[0] == 0:
        jumps.append((dir[0], 2 * dir[1]))
    if dir[1] == 0:
        jumps.append((2 * dir[0], dir[1]))
    return jumps


"""
A* in progress

# from:
https://www.redblobgames.com/pathfinding/a-star/implementation.html


"""


def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)


class PriorityQueue:

    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        self.elements.append((priority, item))

    # TODO test
    def get(self):
        """ HANDLE WITH CARE, this can break in so many ways"""
        # first = sorted(self.elements)[0]
        first = sorted_tuples(self.elements)[0]
        self.elements.remove(first)
        return first[1]


def reconstruct_path(came_from, start, goal):
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from[current]
    # path.append(start) # optional
    path.reverse()  # optional
    return path


"""

EXAMPLEFUNKY METHODS

"""
rotate_arr = [
    (0, 1),
    (1, 1),
    (1, 0),
    (1, -1),
    (0, -1),
    (-1, -1),
    (-1, 0),
    (-1, 1)
]


def get_list_index(lst, tup):
    # only works for 2-tuples
    for i in range(len(lst)):
        if lst[i][0] == tup[0] and lst[i][1] == tup[1]:
            return i


def rotate(orig_dir, amount):
    direction = rotate_arr[(get_list_index(rotate_arr, orig_dir) + amount) % 8]
    return direction


"""
###################
"""


# BFS's etcs...


class Navigation(object):
    trajectory = []
    trajectory_step = 0
    expected_cost = {}
    dead_ends = []
    visited = []
    frontier = None
    cost_so_far = {}
    came_from = {}
    bugging = False

    def __init__(self, destination=None):
        self.destination = destination

    def goto(self, bc_object, target):
        """
        :param bc_object: battlecode object
        :param target: tuple target location
        :return:
        """
        if target is None:
            return (0, 0)

        # bc.log('entering goto')
        loc = (bc_object.me.x, bc_object.me.y)
        # bc.log('line 1')
        goal_dir = direction_to(loc, target)
        bc_object.log('Goal dir: {}'.format(goal_dir))
        # bc.log('loc: {}'.format(loc))
        if goal_dir[0] == goal_dir[1] == 0:  # goal_dir == (0, 0):
            # bc.log('goal dir is 0,0')
            return (0, 0)

        # bc.log('line 5')
        # self.log("MOVING FROM " + str(my_coord) + " TO " + str(nav.dir_to_coord[goal_dir]))
        i = 0
        # bc.log(loc)
        # bc.log(goal_dir)
        while is_occupied(bc_object, loc[0] + goal_dir[0], loc[1] + goal_dir[1]) \
                and i < 6:

            # or apply_dir(loc, goal_dir) in already_been: # doesn't work because `in` doesn't work :(
            # alternate checking either side of the goal dir, by increasing amounts (but not past directly backwards)
            if i > 0:
                i = -i
            else:
                i = -i + 1
            goal_dir = rotate(goal_dir, i)
        # bc.log('line final')
        return goal_dir

    def go_to(self, bc_object, target):
        """
        :param bc_object: battlecode object
        :param target: tuple target location
        :return:
        """
        if target is None:
            return (0, 0)

        # bc.log('entering goto')
        loc = (bc_object.me.x, bc_object.me.y)
        # bc.log('line 1')
        goal_dir = direction_to(loc, target)
        bc_object.log('Goal dir: {}'.format(goal_dir))
        # bc.log('loc: {}'.format(loc))
        if goal_dir[0] == goal_dir[1] == 0:  # goal_dir == (0, 0):
            # bc.log('goal dir is 0,0')
            return (0, 0)

        # bc.log('line 5')
        # self.log("MOVING FROM " + str(my_coord) + " TO " + str(nav.dir_to_coord[goal_dir]))
        i = 0
        # bc.log(loc)
        # bc.log(goal_dir)
        while is_occupied(bc_object, loc[0] + goal_dir[0], loc[1] + goal_dir[1]) \
                and i < 4:

            # or apply_dir(loc, goal_dir) in already_been: # doesn't work because `in` doesn't work :(
            # alternate checking either side of the goal dir, by increasing amounts (but not past directly backwards)
            if i > 0:
                i = -i
            else:
                i = -i + 1
            goal_dir = rotate(goal_dir, i)
        # bc.log('line final')
        return goal_dir

    def pseudo_bug(self, bc, target):
        """

        :param bc: battlecode object
        :param target: tuple target location
        :return:
        """
        if target is None:
            bc.log('target is none')
            return (0, 0)

        # bc.log('entering goto')
        loc = locate(bc.me)

        if len(self.trajectory) > 0:

            bc.log('already have a trajectory')
            bc.log('trying to go towards trajectory')
            bc.log(self.trajectory[0])

            bc.log('trying to jump next in trajectory')
            siguiente = self.trajectory[1 % len(self.trajectory)]
            bc.log(siguiente)
            if can_move(bc, siguiente[0], siguiente[1]):
                bc.log('next_tile: jumping in trajectory')
                bc.stuck = 0
                step = difference_to(loc, siguiente)
                self.trajectory.remove(self.trajectory[1 % len(self.trajectory)])
                self.trajectory.remove(self.trajectory[0])
                return step

            siguiente = self.trajectory[0]
            if can_move(bc, siguiente[0], siguiente[1]):
                bc.log('next_tile: moving in trajectory')
                bc.stuck = 0
                step = direction_to(loc, self.trajectory[0])
                self.trajectory.remove(self.trajectory[0])
                # self.trajectory_step = (self.trajectory_step + 1) % len(self.trajectory)
                return step

            bc.log('trying to :goto: next in trajectory')
            siguiente = self.trajectory[1 % len(self.trajectory)]
            goal_dir = self.go_to(bc, siguiente)
            if can_move(bc, *add_dir(loc, goal_dir)):
                bc.stuck += 1
                bc.log('moving in goal dir')
                return goal_dir  # Move in direction

        else:  # Trajectory < 0

            # Try to move in the direction
            goal_dir = direction_to(loc, target)
            bc.log('Goal dir: {}'.format(goal_dir))

            if goal_dir[0] == goal_dir[1] == 0:  # goal_dir == (0, 0):
                bc.stuck = 0
                return (0, 0)

            if can_move(bc, *add_dir(loc, goal_dir)):
                bc.log('moving in goal dir')
                return goal_dir  # Move in direction

            # If cannot move:
            # Try to jump further
            bc.log('trying to jump')
            jump_dirs = jump_directions(bc, goal_dir)
            for dir in jump_dirs:
                if can_move(bc, *add_dir(loc, dir)):
                    bc.log('jumping in dir: {}'.format(dir))
                    return dir

            # Proper pathfind it
            bc.log('unable to jump, a-star this mofo')

            # Create the trajectory with a* to the target or to a close point
            next_tiles, cost_left = self.fine_create_trajectory(bc, loc, target)
            # self.came_from,
            # self.cost_so_far)
            # next_tile, cost_left = {}, {}
            t_end = bc.me.time
            bc.log('a* with {}ms remaining'.format(t_end))

            # CALLS ITSELF AGAIN TO MOVE IN THE TRAJECTORY
            return self.pseudo_bug(bc, target)
            # # Debug
            # bc.log('trajectory')
            # bc.log(next_tiles)
            # bc.log('expected_cost')
            # bc.log(cost_left)

        # bc.stuck += 1
        bc.log('exit at the end')
        return (0, 0)

    def next_tile(self, bc):
        return self.pseudo_bug(bc, self.destination)

    def set_destination(self, destination):
        if self.destination is None:
            self.destination = destination
        if destination[0] != self.destination[0] or destination[1] != self.destination[1]:
            self.visited = []
            self.trajectory = []
            self.destination = destination

    def create_trajectory(self, bc, start, goal):
        # , came_from={}, cost_so_far={}):

        for_hits = 0
        # prev_time = time.time()

        # If we dont have a came from and cost so far
        # if not bool(came_from) and not (bool(cost_so_far)):
        bc.log('starting a*')
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0
        self.frontier = PriorityQueue()
        self.frontier.put(start, 0)

        # else:
        #     bc.log('continuing a*')
        # # Debug
        # # bc.log('preloop in {}ms'.format(prev_time-time.time()))
        # bc.log('preloop ')
        # bc.log('frontier')
        # bc.log(frontier.elements)
        # bc.log('came from')
        # bc.log(came_from)
        # bc.log('cost so far')
        # bc.log(cost_so_far)

        HITS = 50
        if bc.me.time > 1000:
            HITS = 150
        elif bc.me.time < 400:
            HITS = 20
        if bc.me.time < 200:
            HITS = 5

        while not self.frontier.empty() and for_hits < HITS:
            # Debug
            # while_loop_time = time.time()

            current = self.frontier.get()

            # # Debug
            # bc.log('current:')
            # bc.log(current)

            if current[0] == goal[0] and current[1] == goal[1]:
                bc.log('found')
                self.trajectory = reconstruct_path(came_from, start, goal)
                self.came_from = came_from
                self.cost_so_far = cost_so_far
                bc.log('n of hits: {}'.format(for_hits))
                return came_from, cost_so_far

            # # Debug
            # bc.log('walkable_adjacent_tiles:')
            # bc.log(walkable_adjacent_tiles(bc, *current))

            for next in walkable_adjacent_tiles(bc, *current):

                # # Debug
                # bc.log('next:')
                # bc.log(next)

                # for_loop_time = time.time()
                new_cost = cost_so_far[current] + distance(current, next)

                # # Debug
                # bc.log('new_cost:')
                # bc.log(new_cost)

                # # Debug
                # bc.log('if current not in cost_so_far:')
                # bc.log(current not in cost_so_far)

                # # Debug
                # bc.log('if next not in cost_so_far:')
                # bc.log(next not in cost_so_far)

                # # Debug
                # bc.log('new_cost < cost_so_far[next]')
                # bc.log(new_cost < cost_so_far[next])

                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost

                    # # Debug
                    # bc.log('cost so far')
                    # bc.log(cost_so_far)

                    priority = new_cost + heuristic(goal, next)

                    # # Debug
                    # bc.log('priority')
                    # bc.log(priority)

                    self.frontier.put(next, priority)

                    # # Debug
                    # bc.log('frontier')
                    # bc.log(frontier.elements)

                    came_from[next] = current

                    # # Debug
                    # bc.log('came from')
                    # bc.log(came_from)

                    for_hits += 1
                # bc.log('1 hit :for: in {}ms'.format(for_loop_time - time.time()))

            # bc.log('1 hit :while: in {}ms'.format(while_loop_time - time.time()))
        bc.log('n of hits: {}'.format(for_hits))

        bc.log('could not find it')
        bc.log('pathing to the latest point')

        current = self.frontier.get()
        bc.log('pathing towards {}'.format(current))
        self.trajectory = reconstruct_path(came_from, start, current)

        self.came_from = came_from
        self.cost_so_far = cost_so_far

        return came_from, cost_so_far

    def fine_create_trajectory(self, bc, start, goal):
        """ use only for short distances or in combat """

        for_hits = 0
        # prev_time = time.time()

        # If we dont have a came from and cost so far
        # if not bool(came_from) and not (bool(cost_so_far)):
        bc.log('starting fine a*')
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0
        self.frontier = PriorityQueue()
        self.frontier.put(start, 0)

        # else:
        #     bc.log('continuing a*')
        # # Debug
        # # bc.log('preloop in {}ms'.format(prev_time-time.time()))
        # bc.log('preloop ')
        # bc.log('frontier')
        # bc.log(frontier.elements)
        # bc.log('came from')
        # bc.log(came_from)
        # bc.log('cost so far')
        # bc.log(cost_so_far)

        HITS = 50
        if bc.me.time > 1000:
            HITS = 80
        elif bc.me.time < 400:
            HITS = 20
        if bc.me.time < 200:
            HITS = 5

        while not self.frontier.empty() and for_hits < HITS:
            # Debug
            # while_loop_time = time.time()

            current = self.frontier.get()

            # # Debug
            # bc.log('current:')
            # bc.log(current)

            if current[0] == goal[0] and current[1] == goal[1]:
                bc.log('found')
                self.trajectory = reconstruct_path(came_from, start, goal)
                self.came_from = came_from
                self.cost_so_far = cost_so_far
                bc.log('n of hits: {}'.format(for_hits))
                return came_from, cost_so_far

            # # Debug
            # bc.log('walkable_adjacent_tiles:')
            # bc.log(walkable_adjacent_tiles(bc, *current))

            for next in passable_movement_tiles(bc, *current):

                # # Debug
                # bc.log('next:')
                # bc.log(next)

                # for_loop_time = time.time()
                new_cost = cost_so_far[current] + distance(current, next)

                # # Debug
                # bc.log('new_cost:')
                # bc.log(new_cost)

                # # Debug
                # bc.log('if current not in cost_so_far:')
                # bc.log(current not in cost_so_far)

                # # Debug
                # bc.log('if next not in cost_so_far:')
                # bc.log(next not in cost_so_far)

                # # Debug
                # bc.log('new_cost < cost_so_far[next]')
                # bc.log(new_cost < cost_so_far[next])

                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost

                    # # Debug
                    # bc.log('cost so far')
                    # bc.log(cost_so_far)

                    priority = new_cost + heuristic(goal, next)

                    # # Debug
                    # bc.log('priority')
                    # bc.log(priority)

                    self.frontier.put(next, priority)

                    # # Debug
                    # bc.log('frontier')
                    # bc.log(frontier.elements)

                    came_from[next] = current

                    # # Debug
                    # bc.log('came from')
                    # bc.log(came_from)

                    for_hits += 1
                # bc.log('1 hit :for: in {}ms'.format(for_loop_time - time.time()))

            # bc.log('1 hit :while: in {}ms'.format(while_loop_time - time.time()))
        bc.log('n of hits: {}'.format(for_hits))

        bc.log('could not find it')
        bc.log('pathing to the latest point')

        current = self.frontier.get()
        bc.log('pathing towards {}'.format(current))
        self.trajectory = reconstruct_path(came_from, start, current)

        self.came_from = came_from
        self.cost_so_far = cost_so_far

        return came_from, cost_so_far


#
#
# from battlecode import BCAbstractRobot, SPECS
# import battlecode as bc
# from bots.first_bot.utils import *

C2T = {
    0: 'YOUR_MINE_IS',
    1: 'GO_MINE_BUILD_CHURCH',
    2: 'SCOUT_RUSH',
    3: 'FAVORABLE_FIGHT_AT',
    4: 'UNFAVORABLE_FIGHT_AT',
    5: 'not_implemented_yet',
    6: 'not_implemented_yet',
    7: 'not_implemented_yet',
    8: 'not_implemented_yet',
    9: 'not_implemented_yet',
    10: 'not_implemented_yet',
    11: 'not_implemented_yet',
    12: 'not_implemented_yet',
    13: 'not_implemented_yet',
    14: 'not_implemented_yet',
    15: 'not_implemented_yet',
    16: 'not_implemented_yet'
}

T2C = {
    'YOUR_MINE_IS': 0,
    'GO_MINE_BUILD_CHURCH': 1,
    'SCOUT_RUSH': 2,
    'FAVORABLE_FIGHT_AT': 3,
    'UNFAVORABLE_FIGHT_AT': 4,
    # 'not_implemented_yet':5 ,
    # 'not_implemented_yet':6 ,
    # 'not_implemented_yet':7 ,
    # 'not_implemented_yet':8 ,
    # 'not_implemented_yet':9 ,
    # 'not_implemented_yet':10 ,
    # 'not_implemented_yet':11 ,
    # 'not_implemented_yet':12 ,
    # 'not_implemented_yet':13 ,
    # 'not_implemented_yet':14 ,
    # 'not_implemented_yet':15 ,
    # 'not_implemented_yet':16
}

# For CASTLE TALK 2 ^ 8 - 1
M2T = {
    0: 'CASTLE_AT',
    1: 'CHURCH_AT',
    2: 'HELLO_CHURCH',
    3: 'TARGET_DONE',
    4: 'not_implemented_yet',
    5: 'not_implemented_yet',
    6: 'not_implemented_yet',
    7: 'not_implemented_yet'
}

# For CASTLE TALK 2 ^ 8 - 1
T2M = {
    'CASTLE_AT': 0,
    'CHURCH_AT': 1,
    'HELLO_CHURCH': 2,
    'TARGET_DONE': 3,
    # 'not_implemented_yet':4 ,
    # 'not_implemented_yet':5 ,
    # 'not_implemented_yet':6 ,
    # 'not_implemented_yet':7 ,
    'null': 256
}

#
#
# from .tools import *
# from .ranges import *
# from .utils import *
# from .navigation import *
# from .preprocessing import *
# from .monitoring import *
# from .combat import *
# from .message_meanings import *
# from .communication import *

#
#
TYPES = ["CASTLE", "CHURCH", "PILGRIM", "CRUSADER", "PROPHET", "PREACHER"]


def first_turn_monitor(self):
    # self.log('Map size {}x{}'.format(self.game_info['map_size'],
    #                                  self.game_info['map_size']))
    # self.log('# TODO first_turn_monitor')
    pass


def unit_monitor(self):
    #  Unit type, id
    #  Turn, Turns alive
    #  Total consumption

    message = '- \n' \
              ' Type: {unit_type}, id: {id} \n' \
              ' turn: {turn}, alive: {alive} \n' \
              ' time left: {time} \n' \
              ' my position: {position} \n' \
              ' my goal: {goal} \n' \
              '- \n'.format(
        unit_type=TYPES[self.me['unit']],
        id=self.me['id'],
        turn=self.me['turn'],
        alive=self.step,
        time=self.me.time,
        position=(self.me.x, self.me.y),
        goal=self.destination
    )
    self.log(message)

    return


# TODO specific monitors for each units
# Carrying materials
#
#
# from battlecode import BCAbstractRobot, SPECS
# import battlecode as bc
# from bots.first_bot.utils import *


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
                        or r.unit == SPECS['CASTLE'] \
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
                        or r.unit == SPECS['CASTLE'] \
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

        return (len(self.my_military) - len(self.enemy_military) > 0)

    def heavily_outgunned(self, bc):

        return (len(self.my_military) - len(self.enemy_military) < -4)

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
#
# import numpy as np
# from battlecode import BCAbstractRobot, SPECS
# import battlecode as bc
# import random

# from bots.first_bot.utils import *


def is_occupied(bc, x, y):
    """
    Check if that tile is occupied, impassable or outside the map
    :param bc: battlecode object
    :param x: x position
    :param y: y position
    :return: True if occupied False if not occupied
    """
    map_size = len(bc.passable_map)
    if (x >= 0) and (y >= 0) and (x <= map_size) and (y <= map_size):
        # It is inside the map
        if bc.passable_map[y][x] > 0:
            # It is passable
            for robot in bc.vision_list:
                if (robot['x'] == x) and (robot['y'] == y) and (robot['id'] != bc.me.id):
                    # It is occupied by a robot
                    return True
            else:
                # It is NOT occupied by a robot
                return False
    return True


def is_walkable(bc, x, y):
    """
    Check if that tile is impassable or outside the map
    :param bc: battlecode object
    :param x: x position
    :param y: y position
    :return: True if occupied False if not occupied
    """
    map_size = len(bc.passable_map)
    if (x >= 0) and (y >= 0) and (x <= map_size) and (y <= map_size):
        # It is inside the map
        if bc.passable_map[y][x] > 0:
            # It is passable
            return True
    return False


def is_not_walkable(bc, x, y):
    """
    Check if that tile is not impassable or inside the map
    :param bc: battlecode object
    :param x: x position
    :param y: y position
    :return: True if NOT occupied False if occupied
    """
    return not is_walkable(bc, x, y)


def is_not_occupied(bc, x, y):
    """
    Check if that tile is not occupied, not impassable or inside the map
    :param bc: battlecode object
    :param x: x position
    :param y: y position
    :return: True if NOT occupied False if occupied
    """
    return not is_occupied(bc, x, y)


def is_in_range(robot, x, y, range_squared):
    """
    Check if a target is within SQUARED range of the robot
    :param robot: robot object eg bc.me
    :param x: target_x
    :param y: target_y
    :param range_squared: true range**2
    :return: True if it is in range, False if not
    """
    my_x = robot.x
    my_y = robot.y
    dx = my_x - x
    dy = my_y - y

    return (dx ** 2 + dy ** 2) <= range_squared


def inside_range(loc1, loc2, range_squared):
    """
    Check if a target is within SQUARED range of the robot
    :param robot: robot object eg bc.me
    :param x: target_x
    :param y: target_y
    :param range_squared: true range**2
    :return: True if it is in range, False if not
    """
    x, y = loc2
    my_x, my_y = loc1

    dx = my_x - x
    dy = my_y - y

    return (dx ** 2 + dy ** 2) <= range_squared


def can_build(bc, unit_name, x, y):
    """
    Helper method for building units
    :param bc: battlecode object
    :param unit_name: name of the unit to build e.g. PILGRIM
    :param x: x position to build
    :param y: y position to build
    :return: True if you have materials to build unit
    """
    karb = bc.karbonite
    fuel = bc.fuel
    # self.log('Karb: {}, Fuel: {}'.format(karb,fuel))
    unit_specs = SPECS['UNITS'][SPECS[unit_name]]
    karb_cost = unit_specs['CONSTRUCTION_KARBONITE']
    fuel_cost = unit_specs['CONSTRUCTION_FUEL']
    # self.log('Karb_c: {}, Fuel_c: {}'.format(karb_cost, fuel_cost))

    valid_cost = (karb >= karb_cost) and (fuel >= fuel_cost)
    # bc.log('cost_ok: {}'.format(valid_cost))

    if valid_cost:
        # Enough Karb and Fuel
        # Check if occupied
        occupied = is_not_occupied(bc, x, y)
        # bc.log('is not occupied?: {}'.format(occupied))
        return occupied

    # Not enough currency
    return valid_cost


def can_mine(bc, x, y):
    """ bc is the battlecode object"""
    # Find if x,y can be mined and if you have enough capacity
    unit_specs = SPECS['UNITS'][bc.me.unit]
    fuel_capacity = unit_specs['FUEL_CAPACITY']
    karb_capacity = unit_specs['KARBONITE_CAPACITY']

    if bc.fuel_map[y][x]:
        return not (bc.me.fuel == fuel_capacity)
    if bc.karbonite_map[y][x]:
        return not (bc.me.karbonite == karb_capacity)
    return False


# # You cannot check other's unit karb and fuel
def can_give(bc, loc):
    """ bc is the battlecode object"""
    dx, dy = difference_to(locate(bc.me), loc)
    # Too far
    if abs(dx) + abs(dy) > 2:
        return False

    # Find if dx,dy can be given materials
    unit_specs = SPECS['UNITS'][bc.me.unit]
    fuel_capacity = unit_specs['FUEL_CAPACITY']
    karb_capacity = unit_specs['KARBONITE_CAPACITY']
    loc = (bc.me.x, bc.me.y)
    my_team = bc.me.team
    # Si tienes algun material
    if bc.me.karbonite > 0 or bc.me.fuel > 0:
        # Si hay un robot en dx, dy
        for robot in bc.vision_list:
            if bc.is_visible(robot):
                if robot.team == my_team and \
                        robot.x == loc[0] + dx and \
                        robot.y == loc[1] + dy:
                    return True
    # Return true

    return False


# def can_give(bc, castle):
#     """ bc is the battlecode object"""
#     # Find if dx,dy can be given materials
#     x, y = bc.me.x, bc.me.y
#     t_x, t_y = castle.x, castle.y
#     # Si tienes algun material
#     if bc.me.karbonite > 0 or bc.me.fuel > 0:
#         # Is adjacent?
#         return (x - t_x) ** 2 < 2 and (y - t_y) ** 2 < 2
#
#     return False


def can_move(bc, x, y):
    """
    Check if the robot can move to that tile by fuel, range and occupied.
    :param bc: battlecode object
    :param x:
    :param y:
    :return: True if yes False if No
    """
    my_x = bc.me.x
    my_y = bc.me.y
    dx = x - my_x
    dy = y - my_y

    # Enough Fuel?
    fuel = bc.fuel
    unit_specs = SPECS['UNITS'][bc.me.unit]
    fuel_cost = unit_specs['FUEL_PER_MOVE'] * (dx ** 2 + dy ** 2)
    if fuel < fuel_cost:
        bc.log('Not enough Fuel to move')
        return False

    # Is it in range?
    if not is_in_range(bc.me, x, y, unit_specs['SPEED']):
        # Not in range
        return False

    # Is it occupied?
    occupied = is_not_occupied(bc, x, y)
    return occupied


def can_attack(bc, x, y):
    """
    Check if the robot can attack the tile
    :param bc: battlecode object
    :param x:
    :param y:
    :return: True if yes, False if no
    """
    # Enough Fuel?
    fuel = bc.fuel
    unit_specs = SPECS['UNITS'][bc.me.unit]
    fuel_cost = unit_specs['ATTACK_FUEL_COST']
    if fuel < fuel_cost:
        bc.log('Not enough Fuel to attack')
        return False

    # Is it in range?
    in_range = False
    if is_in_range(bc.me, x, y, unit_specs['ATTACK_RADIUS'][1]):
        # Check outside small range, then inside big one
        in_range = not is_in_range(bc.me, x, y, unit_specs['ATTACK_RADIUS'][0])
    return in_range


def team(robot):
    return robot['team']


def locate(robot):
    return (robot.x, robot.y)


def full_of_karb(self):
    unit_specs = SPECS['UNITS'][self.me.unit]
    return self.me.karbonite == unit_specs['KARBONITE_CAPACITY']


def full_of_fuel(self):
    unit_specs = SPECS['UNITS'][self.me.unit]
    return self.me.fuel == unit_specs['FUEL_CAPACITY']


# TODO test
def is_a_mine(bc, location):
    """ True if location (tuple) is a mine """
    return (loc_in_list(location, bc.map_process.karb_mines) or
            loc_in_list(location, bc.map_process.fuel_mines))


def is_attackable(bc_object, robot):
    """ Check if you can attack the robot included fuel cost etc."""
    return can_attack(bc_object, robot.x, robot.y)


def am_i_attackable(bc_object, robot):
    """ can I get attacked by robot """
    # is it an attacking unit
    u_specs = SPECS['UNITS'][robot.unit]
    if u_specs['ATTACK_DAMAGE'] is not None:
        # Within attack range
        return is_in_range(bc_object.me, robot.x, robot.y, u_specs['ATTACK_RADIUS'][1]) \
               and not is_in_range(bc_object.me, robot.x, robot.y, u_specs['ATTACK_RADIUS'][0])
    return False


def can_be_attacked(loc, robot):
    """ can I get attacked by robot """
    # is it an attacking unit
    u_specs = SPECS['UNITS'][robot.unit]
    if u_specs['ATTACK_DAMAGE'] is not None:
        # Within attack range
        return inside_range(loc, locate(robot), u_specs['ATTACK_RADIUS'][1]) \
               and not inside_range(loc, locate(robot), u_specs['ATTACK_RADIUS'][0])
    return False


def is_attackable_unit(robot_1, robot_2):
    """ check if robot 1 can attack robot 2"""
    unit_specs_1 = SPECS['UNITS'][robot_1.unit]
    if robot_1 and robot_2:
        # is it an attacking unit ?
        if unit_specs_1['ATTACK_DAMAGE'] is not None:
            # Within attack range ?
            return is_in_range(robot_1, robot_2.x, robot_2.y, unit_specs_1['ATTACK_RADIUS'][1]) \
                   and not is_in_range(robot_1, robot_2.x, robot_2.y, unit_specs_1['ATTACK_RADIUS'][0])


def im_at(bc, location):
    """
    Check if you are at specified position
    :param bc: battlecode object
    :param location: tuple of (x, y)
    :return: True if standing at that position
    """
    if location is None:
        bc.log('im_at: location passed was None')
        return False  # Default true to push for next castle?

    return bc.me.x == location[0] and bc.me.y == location[1]


def is_adjacent(origin, destination):
    return distance(origin, destination) < 3


# TODO test
def closest(bc, origin, tiles):
    if origin is None:
        origin = locate(bc.me)

    """ from a list of tiles choose the one that is closest """
    d_tiles = [(distance(origin, tile), tile) for tile in tiles]
    return sorted_tuples(d_tiles)[0][1]


# TODO test
def closest_passable(bc, origin, tiles):
    """ from a list of tiles choose the one that is closest """
    if origin is None:
        origin = locate(bc.me)

    d_tiles = [(distance(origin, tile), tile) for tile in tiles if is_not_occupied(bc, *tile)]
    # bc.log(sorted_tuples(d_tiles))
    if len(d_tiles) > 0:
        return sorted_tuples(d_tiles)[0][1]
    else:
        return None


# EXAMPLEFUNKY CODE

def reflect(bc, loc, horizontal=True):
    # bc.log('        horizontal: {}'.format(horizontal))
    if loc is None:
        return None
    map_size = len(bc.passable_map)
    v_reflec = [loc[0], map_size - loc[1]]
    h_reflec = [map_size - loc[0], loc[1]]
    # bc.log('        v_reflec: {}'.format(v_reflec))
    # bc.log('        h_reflec: {}'.format(h_reflec))
    if horizontal:
        return h_reflec
    else:
        return v_reflec


# EXAMPLEFUNKY CODE
def loc_in_list(elemento, lista):
    """
    Equivalent to [if elemento in lista:]
    :param elemento:
    :param lista:
    :return:
    """
    if elemento is None:
        return False
    if len(lista) < 1:
        return False
    for e in lista:
        if e[0] == elemento[0] and e[1] == elemento[1]:
            return True
    return False


#
#
# from battlecode import BCAbstractRobot, SPECS
# import battlecode as bc
# from bots.first_bot.utils import *


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

    # Church comm flags
    sent_first_church = False
    first_turn_churches = {}
    churches_coords = []

    # Targets done flags
    sent_first_target = False
    first_turn_targets = {}
    target_coords = []

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

    # TODO test it didnt break
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
                    castle_cord = tuple((self.first_turn_coords[id], coord))
                    if not loc_in_list(castle_cord, self.castle_coords):
                        self.castle_coords.append(tuple(castle_cord))
                #  If map is vertically reflected :
                else:
                    bc.log('vertical map')
                    castle_cord = tuple((coord, self.first_turn_coords[id]))
                    if not loc_in_list(castle_cord, self.castle_coords):
                        self.castle_coords.append(tuple(castle_cord))

                # bc.log('first turn coords: {}'.format(self.first_turn_coords))
                bc.log('recieved coords: {}'.format(castle_cord))

        return

    def get_code_castletalk(self, mssg):
        coord = mssg % 64
        code = int((mssg - coord) / 64)
        return code, coord

    def code_castletalk(self, code, coord):
        mssg = (coord % 64) + ((code % 8) * 64)
        return mssg

    # TODO test it
    def issue_church(self, bc, church_loc):
        """ notify the castles you will build a church in church_loc """
        bc.log('issuing a church')
        if not self.sent_first_church:
            # Send first part
            mssg = self.code_castletalk(T2M['CHURCH_AT'], church_loc[0])
            self.sent_first_church = True
        else:
            # Send second part
            mssg = self.code_castletalk(T2M['CHURCH_AT'], church_loc[1])
            self.sent_first_church = False
        bc.log('sending: {} by castletalk'.format(mssg))
        self.send_castle_talk(bc, mssg)

    # TODO test
    def churches_being_built(self, bc):
        """ check if there is going to be any church built soon """

        # Check if any pilgrim is going to build a church
        for robot in bc.get_visible_robots():
            mssg, id = self.receive_castle_talk(robot)
            if mssg == 0:
                # bc.log('not valid coord_1')
                continue
            code, coord = self.get_code_castletalk(mssg)
            if code != T2M['CHURCH_AT']:
                continue
            if id not in self.first_turn_coords:
                bc.log('receiving first part')
                bc.log('coord_1: {}'.format(coord))
                self.first_turn_coords[id] = coord
            # Yes:when called again
            else:
                bc.log('receiving second part')
                church_cord = (self.first_turn_coords[id], coord)
                # bc.log('first turn coords: {}'.format(self.first_turn_coords))
                bc.log('recieved church coords: {}'.format(church_cord))
                self.churches_coords.append(church_cord)
                # NEW CHURCH
                # Plan for it with the build order
                bc.log('save resources for the new church')
                bc.build_order.save_for_church(bc)

        pass

    def hello_church(self, bc):
        mssg = self.code_castletalk(T2M['HELLO_CHURCH'], 0)
        self.send_castle_talk(bc, mssg)

    def is_there_new_churches(self, bc):
        for robot in self.signaling:
            mssg, id = self.receive_castle_talk(robot)
            if mssg == 0:
                # bc.log('not valid coord_1')
                continue
            code, coord = self.get_code_castletalk(mssg)
            if code != T2M['HELLO_CHURCH']:
                continue
            bc.log('receiving a new church')
            bc.build_order.church_built(bc)
            # Recalculate mines of this castle taking into account the church
            bc.log('replan mines for the new church')
            bc.map_process.my_churches = self.churches_coords
            bc.map_process.filter_mines_for_church(bc, self.churches_coords.pop())

    def receive_target(self, bc):
        bc.log('Receiving target')
        # find the castle siganl and receive it
        for robot in self.signaling:
            if robot.unit == SPECS['CASTLE'] or robot.unit == SPECS['CHURCH']:
                # bc.log('robot {}, message {}'.format(robot, robot.signal))
                code, mine = self.receive_loc(bc, robot, robot.signal)
                bc.log('    target: {}, code: {}'.format(mine, code))
                if code == T2C['YOUR_MINE_IS']:
                    # Debug
                    bc.log('    target received correctly')
                    if not is_a_mine(bc, mine):
                        bc.log('    It is not a mine')
                        bc.church_spot = (-1, -1)  # Hacky way to avoid checking for church if you are scouting
                    return mine
                else:
                    bc.log('    not appropriate code')
        else:
            bc.log('    no castle found')
        bc.log('    couldnt find mine')
        return locate(bc.me)

    def notify_target_done(self, bc, target):
        """ notify the castles you will build a church in church_loc """
        bc.log('notify_target_done')
        if not self.sent_first_target:
            # Send first part
            mssg = self.code_castletalk(T2M['TARGET_DONE'], target[0])
            self.sent_first_target = True
        else:
            # Send second part
            mssg = self.code_castletalk(T2M['TARGET_DONE'], target[1])
            self.sent_first_target = False
        bc.log('sending: {} by castletalk'.format(mssg))
        self.send_castle_talk(bc, mssg)

    # TODO test
    def check_if_targets_done(self, bc):
        """ check if there is going to be any church built soon """
        bc.log('Check if target done')

        # Check if any pilgrim is going to build a church
        for robot in bc.get_visible_robots():
            mssg, id = self.receive_castle_talk(robot)
            if mssg == 0:
                # bc.log('not valid coord_1')
                continue
            code, coord = self.get_code_castletalk(mssg)
            if code != T2M['TARGET_DONE']:
                continue
            bc.log('    One robot trying to signal something')
            if id not in self.first_turn_targets:
                bc.log('    receiving first part')
                bc.log('    coord_1: {}'.format(coord))
                self.first_turn_targets[id] = coord
            # Yes:when called again
            else:
                bc.log('    receiving second part')
                target_cord = (self.first_turn_targets[id], coord)
                # bc.log('first turn coords: {}'.format(self.first_turn_coords))
                bc.log('    recieved target coords: {}'.format(target_cord))

                # REACTION TO THE TARGET DONE

                bc.log('    enemy_castles: {}'.format(bc.map_process.enemy_castles))
                bc.log('    target_cord: {}'.format(target_cord))
                # if in castles
                # if loc_in_list(target_cord, bc.map_process.enemy_castles):
                bc.log('    removing castle')
                # bc.map_process.enemy_castles.remove(target_cord)
                bc.map_process.enemy_castles = [c for c in bc.map_process.enemy_castles if c != target_cord]
                # remove it
                bc.log('    enemy_castles: {}'.format(bc.map_process.enemy_castles))
                # give closer of castles
                # next_target = closest(bc, bc.map_process.enemy_castles)
                next_target = bc.map_process.closest_enemy_castle(bc)
                bc.log('    next_target: {}'.format(next_target))
                # TODO finish it SEND THE NEW TARGET

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
#
# from battlecode import BCAbstractRobot, SPECS
# import battlecode as bc
# import random

# from bots.first_bot.utils import *

# TODO implement game logic
"""
TODO: here I will include when to go with each strat. with flags

for ECON: big_map, no castle is closer than 31 f.e.
            {build pilgrim with destiny to middle mine and save_for_church = True}
            {check if other castles are going for eco and mark it too.}

for RUSH: castle closer than 31, less than 7 mines of one resource
        {create phrophet, phrophet, crusader (maybe?) and give them the rush target}
        {check if other castles in rush so that chuch comes later}

for FAKE_RUSH:  no castle is closer than 35, but not further than 45 and 1 or 2 castles
                {creathe phrophet, pilgrim and save for church}
                {check if other castles are going for FAKE_RUSH and mark it too.}

GENERALLY create pilgrims for each of the mines you have assigned

Create pilgrims for karbonite first except if RUSH then go for fuel

if BEING_ATTACKED create counter phrophet: crusader, crusader: preacher, preacher: phrophets

if no pilgrims left to mine start creating a PHROPHETS for ARCHER LATTICE

"""

RUSH_DISTANCE = 26
ECON_DISTANCE = 34
SMALL_MAP = 37
BIG_MAP = 58


# TODO
class Tactics(object):
    ECON = True  # True by default
    RUSH = False
    FAKE_RUSH = False
    close_castle = False
    fuel_scarce = False
    karb_scarce = False

    def __init__(self, bc):
        # bc.log('Tactics initialized')
        pass

    def game_type_1(self, bc):
        """ to be called in the first turn """
        bc.log('Deciding game type')
        # if small map, RUSH
        if bc.map_process.map_size < SMALL_MAP:  # SMALL MAP
            bc.log('    small map, RUSH')
            self.ECON = False
            self.RUSH = True

        # if map big, ECON
        if bc.map_process.map_size > BIG_MAP:  # SMALL MAP
            bc.log('    map big, ECON')
            self.ECON = True
            self.RUSH = False

        # if 3 castles, ECON
        bc.map_process.get_n_castles(bc)
        if bc.map_process.n_castles > 2:
            bc.log('    3 castles, ECON')
            self.ECON = True
            self.RUSH = False

        # else FAKE_RUSH
        if bc.map_process.n_castles < 3:
            bc.log('    < 3 castles, FAKERUSH')
            self.ECON = True
            self.RUSH = False
            self.FAKE_RUSH = True

        # if close castle, RUSH
        if self.distance_of_castles(bc, locate(bc.me)) < RUSH_DISTANCE:
            bc.log('    close castle, RUSH')
            self.close_castle = True
            self.ECON = False
            self.RUSH = True

        # if far castle, ECON
        if self.distance_of_castles(bc, locate(bc.me)) > ECON_DISTANCE:
            bc.log('    far castle, ECON')
            self.close_castle = False
            self.ECON = True
            self.RUSH = False

        # if karb resource scarce, RUSH karb
        if len(bc.map_process.karb_mines) < 8:
            bc.log('    karb resource scarce, RUSH karb')
            self.karb_scarce = True
            self.ECON = False
            self.RUSH = True
        # if fuel resource scarce, RUSH fuel
        if len(bc.map_process.fuel_mines) < 9:
            bc.log('    fuel resource scarce, RUSH fuel')
            self.fuel_scarce = True
            self.ECON = False
            self.RUSH = True
        # Do not rush if other castle is already rushing
        if self.other_castle_is_rushing(bc):
            bc.log('    not rush if other castle is already rushing')
            self.ECON = True
            self.RUSH = False

    def distance_of_castles(self, bc, loc):
        """ returns straight line distance """
        horizontal = bc.map_process.is_horizontal_reflect()
        x, y = loc
        map_size = bc.map_process.map_size
        d = map_size
        if horizontal:
            d = abs(map_size - 2 * x)
        else:
            d = abs(map_size - 2 * y)
        return d

    # TODO test
    def get_rush_targets(self, bc):
        """
         returns a castle or a mine
        :param bc: object
        :return:  list of targets for spawning the bots
        """

        targets = []
        rush_target = None

        if self.fuel_scarce:
            rush_target = bc.map_process.fuel_rush_mine(bc)
        if self.karb_scarce:
            rush_target = bc.map_process.karb_rush_mine(bc)
        if self.close_castle:
            rush_target = bc.map_process.closest_e_castle_for_units(bc)
        if rush_target is None:
            rush_target = bc.map_process.closest_e_castle_for_units(bc)

        targets.append(rush_target)
        targets.append(rush_target)
        targets.append(rush_target)
        targets.append('m')
        targets.append(rush_target)

        return targets

    def other_castle_is_rushing(self, bc):
        """ looks if there is other castle which is first in queue and is rushing too """
        # Only for castles
        if bc.me.unit != SPECS["CASTLE"]:
            return False

        for r in bc.get_visible_robots():
            c_talk = r.castle_talk
            if c_talk == 0:
                continue

            if abs(bc.map_process.map_size - (2 * (c_talk % 64))) < RUSH_DISTANCE \
                    or bc.map_process.map_size < SMALL_MAP:
                bc.log('    other castle is already rushing')
                return True

        bc.log('    no castles rushing')
        return False

    def under_attack(self, bc):
        """
        Checks the messages and vision to see if we are being attacked
        :param bc:
        :return: True or False
        """
        # TODO implement it
        return False

    def counter_unit(self, bc):
        """
        Returns the most effective unit against the attack received
        :param bc:
        :return: unit name
        """
        # TODO implement it
        unit_types = ["CRUSADER", "PROPHET", "PREACHER"]
        return "PREACHER"

    def lategame_unit(self, bc):
        """
        Returns the most effective unit for lategame according to gametype
        :param bc:
        :return: unit name
        """
        # TODO implement it
        unit_types = ["CRUSADER", "PROPHET", "PREACHER"]
        return "PROPHET"

    def lategame_target(self, bc):
        """
        Returns the most effective target location for lategame according to gametype
        :param bc:
        :return: tuple with a location
        """
        # TODO implement it
        rush_target = bc.map_process.closest_e_castle_for_units(bc)

        return rush_target


#
#

# from .build_orders import *
# from .game_tactics import *

#
#
# from battlecode import BCAbstractRobot, SPECS
# import battlecode as bc
# from bots.first_bot.utils import *

FIRST_BUILD_ORDER = ["PILGRIM", "CRUSADER", "CRUSADER",
                     "PILGRIM", "CRUSADER", "CRUSADER",
                     "PILGRIM", "PILGRIM", "CRUSADER"]

ECON_BUILD_ORDER = ["PILGRIM", "PILGRIM", "PILGRIM", "PILGRIM", "PILGRIM"]

ECON_TARGET_ORDER = ["m", "m", "m", "m", "m"]

RUSH_BUILD_ORDER = ["PILGRIM", "PROPHET", "PROPHET", "PILGRIM", "PREACHER"]

BUILD_ORDER = ECON_BUILD_ORDER


def naive_build(bc, unit_name):
    """
    tries to build around
    :param bc: battlecode object
    :param unit_name: name of the unit to build e.g. PILGRIM
    :return: True if you have materials to build unit
    """
    my_x = bc.me.x
    my_y = bc.me.y
    choices = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
    for dx, dy in choices:
        if can_build(bc, unit_name, my_x + dx, my_y + dy):
            bc.log("Building a {} at [{}, {}]".format(unit_name, bc.me['x'] + dx, bc.me['y'] + dy))
            return bc.build_unit(SPECS[unit_name], dx, dy)
    return None


def dir_build(bc, unit_name, target):
    """
    tries to build around
    :param bc: battlecode object
    :param unit_name: name of the unit to build e.g. PILGRIM
    :return: True if you have materials to build unit
    """
    my_x, my_y = locate(bc.me)
    dir = bc.nav.goto(bc, target)
    if dir is None:
        return naive_build(bc, unit_name)
    dx, dy = dir
    if dx == dy == 0:
        return naive_build(bc, unit_name)
    if can_build(bc, unit_name, my_x + dx, my_y + dy):
        bc.log("Building a {} at [{}, {}]".format(unit_name, bc.me['x'] + dx, bc.me['y'] + dy))
        return bc.build_unit(SPECS[unit_name], dx, dy)
    return None


#

"""
BuilOrderManager: here I will include what to build for each strat. with flags

for ECON: build pilgrim with destiny to middle mine and save_for_church = True
          check if other castles are going for eco and mark it too.

for RUSH: create phrophet, phrophet, crusader (maybe?) and give them the rush target
          check if other castles in rush so that chuch comes later
          
for FAKE_RUSH: creathe phrophet, pilgrim and save for church
                check if other castles are going for FAKE_RUSH and mark it too.

GENERALLY create pilgrims for each of the mines you have assigned

Create pilgrims for karbonite first except if RUSH then go for fuel

if BEING_ATTACKED create counter phrophet: crusader, crusader: preacher, preacher: phrophets

if no pilgrims left to mine start creating a PHROPHETS for ARCHER LATTICE

"""


# TODO test
class BuildOrderManager(object):
    """building logic object"""

    # Reserve materials
    reserve_karb = 0
    reserve_fuel = 0
    issued_churches = 0

    # Tasks
    pilgrim_tasks = {}

    # build steps
    build_step = 0
    mine_step = 0
    build_order = []
    target_order = []

    # Unit counters
    total_units = 0
    pilgrims_built = 0
    total_crusaders = 0
    crusaders_built = 0
    total_prophets = 0
    prophets_built = 0
    total_preacher = 0
    preacher_built = 0

    def __init__(self, build_order=ECON_BUILD_ORDER):
        self.build_order = build_order
        self.build_step = 0

    # TODO test
    def turn_build(self, bc):
        """
        Chooses what to build, returns an order or None
        :param bc:
        :return: order or None to return from robot
        """
        """
        PRIORITY CASES
            Type of Game Build order
            Def from rush
            Def pilgrim
            Pilgrims for my mines
            Defensive lattice

        """

        bc.log('            karb: {}'.format(bc.karbonite))
        bc.log('            fuel: {}'.format(bc.fuel))
        bc.log('    reserve_karb: {}'.format(self.reserve_karb))
        bc.log('    reserve_fuel: {}'.format(self.reserve_fuel))

        if bc.karbonite < self.reserve_karb and bc.fuel < self.reserve_fuel:
            return None

        order = None
        # #
        # Type of Game Build order
        if self.build_step < 5 and bc.me.unit == SPECS["CASTLE"]:
            bc.log('First turns build orders')
            self.build_order_from_gametype(bc)
            unit = self.current_order()
            bc.log('    build order {}'.format(self.build_order))
            bc.log('    trying to build {}'.format(unit))
            if self.enough_for_pilgrim(bc, unit):
                # bc.log('enough pela')
                target = self.current_target(bc)
                bc.log('    target: {}'.format(target))
                order = dir_build(bc, unit, target)
                if order is not None and target is not None:
                    bc.comms.send_loc(bc, target, 2,
                                      code=T2C['YOUR_MINE_IS'])  # SEND THE unit THE LOCATION TO ITS target
                    self.built_correctly(bc)
                    return order
                else:
                    bc.log('    all directions occupied')
            else:
                bc.log('    not enough from what we saved')
        # Def from rush
        # Def pilgrim
        if len(bc.combat.enemy_military) > 0:
            bc.log('We are under attack')
            unit = bc.tactics.counter_unit(bc)
            target = locate(bc.combat.closest_visible_enemy(bc))
            order = dir_build(bc, unit, target)
            bc.log('    unit: {}, target: {}'.format(unit, target))
            if order is not None:
                bc.comms.send_loc(bc, target, 2,
                                  code=T2C['YOUR_MINE_IS'])  # SEND THE unit THE LOCATION TO ITS target
                self.built_correctly(bc)
                return order
            else:
                bc.log('    could not build deffensive units')

        # TODO if missing pilgrims:
        # Pilgrims for my mines
        unit = "PILGRIM"
        if self.enough_for_pilgrim(bc, unit):
            target = bc.map_process.next_mine(bc)
            bc.log('    target: {}'.format(target))
            if target is not None:
                order = dir_build(bc, unit, target)
                bc.log('unit: {}, target: {}'.format(unit, target))
                if order is not None:
                    bc.comms.send_loc(bc, target, 2,
                                      code=T2C['YOUR_MINE_IS'])  # SEND THE unit THE LOCATION TO ITS target
                    self.built_correctly(bc)
                    return order
                else:
                    bc.log('    order was None')
            else:
                bc.log('    no more pilgrims left to build')
        else:
            bc.log('    not enough to build pilgrims')
        # Defensive lattice
        # Offensive lattice?
        unit = bc.tactics.lategame_unit(bc)
        target = bc.tactics.lategame_target(bc)
        if self.enough_for_pilgrim(bc, unit):
            if target is not None:
                order = dir_build(bc, unit, target)
                bc.log('unit: {}, target: {}'.format(unit, target))
                if order is not None:
                    bc.comms.send_loc(bc, target, 2,
                                      code=T2C['YOUR_MINE_IS'])  # SEND THE unit THE LOCATION TO ITS target
                    self.built_correctly(bc)
                    return order
                else:
                    bc.log('could not build')

        # Finally return whatever you chose, probably None
        bc.log('not building this time')
        return order
        #

    def build_order_from_gametype(self, bc):
        if bc.tactics.RUSH:
            self.build_order = RUSH_BUILD_ORDER
            self.target_order = bc.tactics.get_rush_targets(bc)
            return
        if bc.tactics.ECON:
            self.build_order = ECON_BUILD_ORDER
            self.target_order = ECON_TARGET_ORDER
            return
        if bc.tactics.FAKE_RUSH:
            self.build_order = ECON_BUILD_ORDER
            self.target_order = ECON_TARGET_ORDER
            return

        # ECON by default
        self.build_order = ECON_BUILD_ORDER
        self.target_order = ECON_TARGET_ORDER
        return

    def check_pilgrims_alive(self):
        # We assign each pilgrim to a task, and we have to check if they are doing it
        # TODO implement check_pilgrims_alive
        pass

    # TODO test
    def current_order(self):
        if self.build_step < len(self.build_order):
            return self.build_order[self.build_step]
        else:
            return None

    def current_target(self, bc):

        if self.build_order[self.build_step] == "PILGRIM":
            target = bc.map_process.next_mine(bc)
        else:
            target = bc.map_process.closest_e_castle_for_units(bc)
        bc.log('Current Target:')
        bc.log('    build step: {}'.format(self.build_step))
        bc.log('    target : {}'.format(target))
        return target

        # bc.log('Current Target:')
        # bc.log('    build step: {}'.format(self.build_step))
        # bc.log('    target order: {}'.format(self.target_order))
        # if self.build_step < len(self.target_order):
        #     target = self.target_order[self.build_step]
        #     bc.log('    target {}'.format(target))
        #     if target == 'm':
        #         target = bc.map_process.next_mine(bc)
        #         bc.log('        target {}'.format(target))
        #     return target
        # else:
        #     return None

    def built_correctly(self, bc):
        """ build confirmation, increase the build step index"""
        # bc.log('built correctly')
        self.build_step += 1

    # TODO test
    def save_for_church(self, bc):
        bc.log('saving for church')
        self.issued_churches += 1
        if self.issued_churches % 2 == 1:  # Only increase the savings for each odd(impar) church
            self.reserve_karb += 50
            self.reserve_fuel += 200

    # TODO test
    def church_built(self, bc):
        bc.log('church built')
        # if self.issued_churches % 2 == 1:  # Only decrease the savings for each odd(impar) church
        self.reserve_karb -= 50
        self.reserve_fuel -= 200
        self.issued_churches -= 1
        self.reserve_karb = max(self.reserve_karb, 0)
        self.reserve_fuel = max(self.reserve_fuel, 0)

    def enough_for_unit(self, bc, unit):
        """ returns True if you have enough materials """
        if unit is None:
            return False
        unit_k_cost = SPECS['UNITS'][SPECS[unit]]['CONSTRUCTION_KARBONITE']
        unit_f_cost = SPECS['UNITS'][SPECS[unit]]['CONSTRUCTION_FUEL']

        return bc.karbonite >= self.reserve_karb + unit_k_cost \
               and bc.fuel >= self.reserve_fuel + unit_f_cost

    def enough_for_pilgrim(self, bc, unit):
        """ returns True if you have enough materials """
        if unit is None:
            return False
        unit_k_cost = SPECS['UNITS'][SPECS[unit]]['CONSTRUCTION_KARBONITE']
        unit_f_cost = SPECS['UNITS'][SPECS[unit]]['CONSTRUCTION_FUEL']

        # return bc.karbonite >= self.reserve_karb + unit_k_cost \
        #        and bc.fuel >= self.reserve_fuel + unit_f_cost
        return True


#
#
# from battlecode import BCAbstractRobot, SPECS
# import battlecode as bc
# import random
# from ..utils import *


def first_turn_crusader(self):
    # Find your closest mine
    attack_loc = None
    attack_loc = self.comms.receive_target(self)
    self.log('My attack_loc in: {}'.format(attack_loc))

    #  set the objective to the mine

    self.nav.set_destination(attack_loc)
    self.destination = attack_loc

    self.spawn_loc = locate(self.me)


def crusade(self):
    """"""
    """
    ATTACKING BUSSINESS

    """

    # ATTACK IF THERE IS A TARGET
    # TODO change targeting to avoid preachers, attack prophets

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
#
# from battlecode import BCAbstractRobot, SPECS
# import battlecode as bc
# import random

# from ..utils import *


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
#
# from battlecode import BCAbstractRobot, SPECS
# import battlecode as bc
# import random

# from bots.first_bot.utils import *
# from ..tactics import *


def first_turn_castle(self):
    self.build_order = BuildOrderManager(BUILD_ORDER)

    # Debug
    self.map_process.log_lists(self)


def second_third_turns_castles(self):
    self.comms.send_initial_castle_location(self)
    self.comms.receive_initial_castle_location(self)
    # self.log('second_third_turns_castles:')


def castle(self):
    # Shenanigans to get castle locations
    if self.step < 3:
        second_third_turns_castles(self)
    # Part 2 of map processing
    if self.step == 3:
        self.map_process.get_initial_game_info_2(self)

        # Debug
        self.map_process.log_lists(self)

    # COMMUNICATION
    # Check to manage economy
    self.comms.churches_being_built(self)
    self.comms.is_there_new_churches(self)
    self.comms.check_if_targets_done(self)

    # Combat Routines
    target = self.combat.lowest_health_enemy()
    if target is not None:
        self.log('attack target: {}'.format(target))
        if can_attack(self, *locate(target)):
            self.log('attack:')
            self.log(locate(target))
            return self.attack(*difference_to(locate(self.me), locate(target)))

    # Select what to build
    order = self.build_order.turn_build(self)
    if order is not None:
        # self.log('built correctly')
        return order
    else:
        # self.log("Not building this time")
        pass


#
#
# from battlecode import BCAbstractRobot, SPECS
# import battlecode as bc
# import random

# from ..utils import *


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
            if self.destination is None:
                self.destination = self.map_process.closest_e_castle_for_units(self)
                self.map_preprocess.get_initial_game_info(self)
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

            if self.destination is None:
                self.destination = self.map_process.closest_e_castle_for_units(self)
                self.map_preprocess.get_initial_game_info(self)
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

    if distance(locate(self.me), self.destination) < 13 ** 2 and not self.on_ring:
        new_objective = closest_passable(self, locate(self.me), ring(9, 11))
        self.log('going to ring')
        self.nav.set_destination(new_objective)
        self.on_ring = True

    # MUVEMENTO
    # TODO move where you want to go
    # TODO if rush, aggressive pathfind
    # TODO
    moving_dir = self.nav.next_tile(self)
    self.log('moving dir: {}'.format(moving_dir))  # Move to closest non-occupied mine
    if moving_dir is None:
        self.log('movingdir is none')
        return
    if moving_dir[0] == moving_dir[1] == 0:  # moving_dir == (0,0)
        if im_at(self, self.destination):  # Am I at my destination?
            self.log('no castle here, so next castle')
        else:
            self.log('stuck')
    else:
        return self.move(*moving_dir)


#
#
# from battlecode import BCAbstractRobot, SPECS
# import battlecode as bc
# import random

# from bots.first_bot.utils import *
# from ..tactics import *


def first_turn_church(self):
    self.build_order = BuildOrderManager(BUILD_ORDER)

    self.map_process.filter_mines_for_church(self)
    self.comms.hello_church(self)

    # Debug
    self.map_process.log_lists(self)


def church(self):
    self.log("church health: " + self.me['health'])
    # Select what to build
    order = self.build_order.turn_build(self)
    if order is not None:
        # self.log('built correctly')
        return order
    else:
        # self.log("Not building this time")
        pass


#
#

# from .castle import *
# from .church import *
# from .pilgrim import *
# from .crusader import *
# from .preacher import *
# from .prophet import *

#
#
# from battlecode import BCAbstractRobot, SPECS
# import battlecode as bc
# import random

# from ..utils import *


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
            if self.destination is None:
                self.destination = self.map_process.closest_e_castle_for_units(self)
                self.map_preprocess.get_initial_game_info(self)
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

            if self.destination is None:
                self.destination = self.map_process.closest_e_castle_for_units(self)
                self.map_preprocess.get_initial_game_info(self)
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

    if distance(locate(self.me), self.destination) < 13 ** 2 and not self.on_ring:
        new_objective = closest_passable(self, locate(self.me), ring(9, 11))
        self.log('going to ring')
        self.nav.set_destination(new_objective)
        self.on_ring = True

    # MUVEMENTO
    # TODO move where you want to go
    # TODO if rush, aggressive pathfind
    # TODO
    moving_dir = self.nav.next_tile(self)
    self.log('moving dir: {}'.format(moving_dir))  # Move to closest non-occupied mine
    if moving_dir is None:
        self.log('movingdir is none')
        return
    if moving_dir[0] == moving_dir[1] == 0:  # moving_dir == (0,0)
        if im_at(self, self.destination):  # Am I at my destination?
            self.log('no castle here, so next castle')
        else:
            self.log('stuck')
    else:
        return self.move(*moving_dir)


#
# from battlecode import BCAbstractRobot, SPECS

# from .units import *
# from bots.first_bot.units.castle import *
# from bots.first_bot.units.church import *
# from bots.first_bot.units.pilgrim import *
# from bots.first_bot.units.crusader import *
# from bots.first_bot.units.preacher import *
# from bots.first_bot.units.prophet import *
# from .tactics import *

__pragma__('iconv')
__pragma__('tconv')
__pragma__('opov')


# don't try to use global variables!!
class MyRobot(BCAbstractRobot):
    # Lists and maps
    vision_list = []
    vision_map = []
    passable_map = []
    karbonite_map = []
    fuel_map = []

    # Unit Variables
    # useful_locations
    destination = None
    spawn_loc = None
    church_spot = None
    on_ring = False
    scouting = False

    # Game info blob
    game_info = None

    # Personal stats
    fuel_consumed = 0
    step = -1
    stuck = 0

    # Helper Objects
    build_order = None
    nav = None
    combat = None
    map_process = None
    comms = None

    def turn(self):
        """

        :return: action
        """
        self.step += 1

        """
    
            FIRST TURN PREPROCESS HERE   
    
            GENERAL FIRST TURN
    
    
        """
        if self.step == 0:  # First Turn shenanigans
            self.passable_map = self.get_passable_map()
            self.karbonite_map = self.get_karbonite_map()
            self.fuel_map = self.get_fuel_map()

            first_turn_monitor(self)  # Log firs turn info

            # Helper objects
            self.comms = Communications(self)
            self.map_process = MapPreprocess()
            self.nav = Navigation()
            self.combat = CombatManager(self)
            self.tactics = Tactics(self)
            self.map_process.get_initial_game_info(self)
            self.tactics.game_type_1(self)

        """
        GENERAL PRE-TURN HERE

        """
        self.vision_map = self.get_visible_robot_map()
        self.vision_list = self.get_visible_robots()
        self.comms.turn(self)  # Turn routine for communications
        self.combat.turn(self)  # Turn routine for classifying vision robots
        unit_monitor(self)

        """

            SPECIFIC FIRST TURN

        """
        if self.step == 0:  # First Turn shenanigans
            if self.me['unit'] == SPECS['CASTLE']:
                first_turn_castle(self)
            elif self.me['unit'] == SPECS['CHURCH']:
                first_turn_church(self)
            elif self.me['unit'] == SPECS['PILGRIM']:
                first_turn_pilgrim(self)
            elif self.me['unit'] == SPECS['CRUSADER']:
                first_turn_crusader(self)
            elif self.me['unit'] == SPECS['PROPHET']:
                first_turn_prophet(self)
            elif self.me['unit'] == SPECS['PREACHER']:
                first_turn_preacher(self)

        """

        SPECIFIC ACTIONS HERE

        """
        if self.me['unit'] == SPECS['CASTLE']:
            return castle(self)
        elif self.me['unit'] == SPECS['CHURCH']:
            return church(self)
        elif self.me['unit'] == SPECS['PILGRIM']:
            return pilgrim(self)
        elif self.me['unit'] == SPECS['CRUSADER']:
            return crusade(self)
        elif self.me['unit'] == SPECS['PROPHET']:
            return prophet(self)
        elif self.me['unit'] == SPECS['PREACHER']:
            return preacher(self)

        """
        ########################################################################
        """


robot = MyRobot()

#
#

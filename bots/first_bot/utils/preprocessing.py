#
from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import random

from bots.first_bot.utils import *


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
        my_loc = locate(bc.me)
        # Remove my loc from castle locs
        my_castles = [castle for castle in self.my_castles if castle != my_loc]
        # filter distances if d other castles < my dist
        for castle in my_castles:
            for d, mine in self.k_distances:
                if man_distance(castle, mine) < d:
                    self.karb_mines.remove(mine)
            for d, mine in self.f_distances:
                if man_distance(castle, mine) < d:
                    self.fuel_mines.remove(mine)

    def next_mine(self, bc):
        """ Chooses the next mine to send the pilgrim
        If RUSH choose first 2 fuel then karb
        If ECON go for first 2 karb then fuel
        """
        mine_type = ''
        mine = None

        # CHOOSE
        if self.mine_index % 2 == 0:  # Here we go for karb or fuel
            mine_type = 'k'
        else:
            mine_type = 'f'

        # For the first 3 mines
        if self.mine_index < 4:
            if bc.tactics.RUSH:
                bc.log('rush custom mine')
                rush_build = ['s', 'f', 'f']
                mine_type = rush_build[self.mine_index]

            if bc.tactics.ECON:
                bc.log('econ custom mine')
                econ_build = ['k', 'k', 'f']
                mine_type = econ_build[self.mine_index]

        # BUILD
        if mine_type == 'k':  # Here we go for karb
            mine = self.next_karb_mine(bc)
            if mine is None:
                mine = self.next_fuel_mine(bc)
        elif mine_type == 'f':  # Here we go fuel
            mine = self.next_fuel_mine(bc)
            if mine is None:
                mine = self.next_karb_mine(bc)
        else:
            mine = None

        self.mine_index += 1
        return mine

    def next_karb_mine(self, bc):
        if self.index_karb_mine > len(self.karb_mines):
            bc.log(' no karb mines left for this castle ')
            mine = None
            return mine
        mine = self.karb_mines[self.index_karb_mine]
        bc.log('karb mine is {} with k_index {}'.format(mine, self.index_karb_mine))
        self.index_karb_mine = (self.index_karb_mine + 1)
        return mine

    def next_fuel_mine(self, bc):
        if self.index_fuel_mine > len(self.fuel_mines):
            bc.log(' no fuel mines left for this castle ')
            mine = None
            return mine
        mine = self.fuel_mines[self.index_fuel_mine]
        bc.log('fuel mine is {} with f_index {}'.format(mine, self.index_fuel_mine))
        self.index_fuel_mine = (self.index_fuel_mine + 1)
        return mine

    # TODO test
    def closest_enemy_castle(self, bc):
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


    def get_church_spot(self, bc, loc):
        """ This will get all mines close to the loc and get adjacents and rate them"""
        bc.log('Choosing Ground for the holy land (get church spot)')
        candidates = {}
        max_points = 0
        chosen_spot = None

        close_k_mines = [mine for mine in self.karb_mines if man_distance(loc, mine) < 5]
        close_f_mines = [mine for mine in self.fuel_mines if man_distance(loc, mine) < 5]
        mines = close_f_mines
        mines.append(close_k_mines)
        bc.log('Church mines')

        for mine in mines:
            spots = walkable_adjacent_tiles(bc, *mine)
            for spot in spots:
                if loc_in_list(spot, mines):
                    continue  # Better not build in a mine

                # May break
                if not candidates.__contains__(spot):
                    candidates[spot] = 1
                else:
                    candidates[spot] += 1

        # May break
        for spot in candidates.keys():
            points = candidates[spot]
            if points > max_points:
                max_points = points
                chosen_spot = spot

        return chosen_spot

    # TODO do and test
    # Assign all mines to that church or only its own?????

    # Restructure my mines when there is a church
    def filter_mines_bc_church(self, bc, church):
        """

        :param bc:
        :param church: church location
        :return: None
        """
        my_loc = locate(bc.me)
        # add the church
        all_deposits = self.my_castles
        all_deposits.append(church)
        # Remove my loc from castle locs
        my_castles = [castle for castle in all_deposits if castle != my_loc]
        # filter distances if d other castles < my dist
        for castle in my_castles:
            for d, mine in self.k_distances:
                if man_distance(castle, mine) < d:
                    self.karb_mines.remove(mine)
            for d, mine in self.f_distances:
                if man_distance(castle, mine) < d:
                    self.fuel_mines.remove(mine)



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

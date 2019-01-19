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
        my_loc = locate(bc.me)
        self.k_distances = [(man_distance(my_loc, mine), mine) for mine in self.karb_mines]
        self.karb_mines = [mine for _, mine in sorted(self.k_distances)]
        self.f_distances = [(man_distance(my_loc, mine), mine) for mine in self.fuel_mines]
        self.fuel_mines = [mine for _, mine in sorted(self.f_distances)]

    def filter_mines_by_distance(self, bc):
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

    # TODO test
    def next_mine(self, bc):
        # TODO by now only karb mine
        mine = self.karb_mines[self.index_karb_mine]
        bc.log('mine is {} with index {}'.format(mine, self.index_karb_mine))
        self.index_karb_mine += 1  # TODO problem to know when to stop
        return mine

    def log_lists(self, bc):
        bc.log('map_size: {}'.format(self.map_size))
        bc.log('n_castles: {}'.format(self.n_castles))
        bc.log('passable_size: {}'.format(self.passable_tiles))
        bc.log('passable_pct: {}%'.format(int(self.passable_pct * 100)))
        bc.log('horizontal reflect: {}'.format(self.horizontal_reflection))
        bc.log('n_karb_mines: {}'.format(len(self.karb_mines)))
        bc.log('karb_mines: {}'.format(self.karb_mines))
        bc.log('n_fuel_mines: {}'.format(len(self.fuel_mines)))
        bc.log('my castles: {}'.format(self.my_castles))
        bc.log('enemy_castles: {}'.format(self.enemy_castles))

#

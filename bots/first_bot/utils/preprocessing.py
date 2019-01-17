#
from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import random

from ..utils import *




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


# TODO test use cases
def find_all(self, mapa, location):
    """
    Method used to find the all mines, for example
    :param self: battlecode object
    :param mapa: map the format bc uses it map[y][x]
    :param location: (tuple) the position in a tuple (x, y)
    :return: (tuple) closest location (x, y)
    """
    # TODO mark the distance at which they are
    target = []
    visited = []
    q = []
    i_q = 0
    current = location
    q.append(current)
    while i_q < len(q):
        visited.append(current)
        if mapa[current[1]][current[0]]:
            # Found one
            target.append(current)
        for x, y in passable_adjacent_tiles(self, current[0], current[1]):
            newc = (x, y)
            if not loc_in_list(newc, visited):
                # Not visited
                q.append(newc)

        current = q[i_q]  # Equivalent to pop
        i_q += 1
    return target


# TODO create a method to gather info of the map, size, type, n_castles etc..


class MapPreprocess(object):
    """
    extract the features of the type of game and aids with the targeting
    """
    map_size = -1
    passable_tiles = 0
    passable_pct = -1
    horizontal_reflection = True
    my_castles = []
    enemy_castles = []
    karb_mines = []
    fuel_mines = []
    conectedness = []

    def get_initial_game_info(self, bc):

        self.map_size = len(bc.passable_map[0])
        self.find_all_mines(bc)
        self.horizontal_reflection = self.is_horizontal_reflect()

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

    def reflect_enemy_castles(self, bc):
        # TODO do not use yet, until you know the location of castles
        """ call after horizontal reflection is known, and castles known"""
        for castle in self.my_castles:
            self.enemy_castles.append(reflect(bc, castle, self.horizontal_reflection))

    def log_lists(self, bc):
        bc.log('map_size: {}'.format(self.map_size))
        bc.log('passable_size: {}'.format(self.passable_tiles))
        bc.log('passable_pct: {0:.2f}'.format(self.passable_pct))
        bc.log('horizontal reflect: {}'.format(self.horizontal_reflection))
        bc.log('n_karb_mines: {}'.format(len(self.karb_mines)))
        bc.log('karb_mines: {}'.format(self.karb_mines))
        bc.log('n_fuel_mines: {}'.format(len(self.fuel_mines)))
        bc.log('fuel_mines: {}'.format(self.fuel_mines))







#

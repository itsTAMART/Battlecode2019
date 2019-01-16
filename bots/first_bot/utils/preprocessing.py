#
from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import random

from ..utils import *


# EXAMPLEFUNKY CODE
# TODO continue Here
def reflect(full_map, loc, horizontal=True):
    map_size = [len(full_map), len(full_map[0])]
    v_reflec = (map_size[1] - loc[0], loc[1])
    h_reflec = (loc[0], map_size[0] - loc[1])
    if horizontal:
        return h_reflec if full_map[h_reflec[1]][h_reflec[0]] else v_reflec
    else:
        return v_reflec if full_map[v_reflec[1]][v_reflec[0]] else h_reflec


def loc_in_list(elemento, lista):
    """
    Equivalent to [if elemento in lista:]
    :param elemento:
    :param lista:
    :return:
    """
    if len(lista) < 1:
        return False
    for e in lista:
        if e[0] == elemento[0] and e[1] == elemento[1]:
            return True
    return False


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
def get_initial_game_info(self):
    info = {
        'map_size': len(self.passable_map[0])
    }

    return info

#

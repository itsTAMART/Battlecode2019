#
from bots.first_bot.utils import *

DIRECTIONS = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]


# Adjacent tiles
def adjacent_tiles(self, x, y):
    map_size = len(self.passable_map[0])
    adjacents = [(x + dx, y + dy) for dx, dy in DIRECTIONS
                 if ((x + dx) >= 0) and
                 ((x + dx) < map_size) and
                 ((y + dy) >= 0) and
                 ((y + dy) < map_size)]
    return adjacents


# Passable adjacent tiles
def passable_adjacent_tiles(self, x, y):
    adjacents = adjacent_tiles(self, x, y)
    passable_adjacents = [(ax, ay) for ax, ay in adjacents if is_not_occupied(self, ax, ay)]
    return passable_adjacents


# tiles within range
def in_range_tiles(self, x, y, r):
    """

    :param self: robot object
    :param x:
    :param y:
    :param r: radius squared
    :return:
    """
    # TODO just do it (LEFT HERE)
    return


def movable_tiles(self):
    # TODO do it
    return


# BFS's etcs...

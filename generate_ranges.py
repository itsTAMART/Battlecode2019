"""
 RANGES

	Script to precompute the distance ranges, so the bot doesn't have to do it on the game

"""

import itertools as IT


def distance(destination):
    """

    :param origin: location
    :param destination:
    :return: distance squared
    """

    dx = destination[0]
    dy = destination[1]

    return (dx ** 2 + dy ** 2)


# max range in game is 100(10**2) vision radius
# so lets create till 11 radius


radii = list(range(0, 13))


def ranges(radii):
    for r in radii:
        two_rad = list(range(-r, r + 1))
        tiles = IT.product(two_rad, repeat=2)
        tiles = [tile for tile in tiles if distance(tile) <= r ** 2]
        print('RANGE_{} = {}'.format(r ** 2, tiles))


ranges(radii)

print('RANGES = [[(0, 0)],')
for r in radii:
    print('RANGE_{},'.format(r ** 2))

print(']')

"""

#####################################################
"""

import math

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


def tiles_in_range(r_squared):
    """
    tiles in range
    :param r: r squared
    :return: list of tiles
    """
    r = int(math.sqrt(r_squared))
    if r >= 0 and r <= len(RANGES):
        return RANGES[r]
    else:
        return None


def ring(r_min, r_max):
    range_min = tiles_in_range(r_min)
    return [tile for tile in tiles_in_range(r_max) if (tile not in range_min)]


radii = list(range(0, 13))

print('RINGS = [')
for r_min in radii:
    print('[')
    for r_max in radii:
        if r_min < r_max:
            print(ring(r_min ** 2, r_max ** 2))
            print(', ')
        else:
            print('[], ')

    print('],')
print(']')

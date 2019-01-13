#
from bots.first_bot.utils import *


DIRECTIONS = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]


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


# TODO test
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


def my_loc(self):
    """
    my location
    :param self: robot_object
    :return: x, y
    """
    return self.me.x, self.me.y


def locate(robot):
    """
    Location of a robot class
    :param robot:
    :return:
    """
    return robot.x, robot.y


def direction_to(origin, destination):
    """

    :param origin: location
    :param destination:
    :return: direction
    """
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


def goto(self, target):
    self.log('entering goto')
    loc = (self.me.x, self.me.y)
    self.log('line 1')
    goal_dir = direction_to(loc, target)
    self.log('Goal dir: {}'.format(goal_dir))
    self.log('loc: {}'.format(loc))
    if goal_dir is (0, 0):
        self.log('goal dir is 0,0')
        return (0, 0)
    self.log('line 5')
    # self.log("MOVING FROM " + str(my_coord) + " TO " + str(nav.dir_to_coord[goal_dir]))
    i = 0
    while is_occupied(self, loc[0] + goal_dir[0], loc[1] + goal_dir[1]) and i < 4:
        # TODO make it able to bug
        # or apply_dir(loc, goal_dir) in already_been: # doesn't work because `in` doesn't work :(
        # alternate checking either side of the goal dir, by increasing amounts (but not past directly backwards)
        if i > 0:
            i = -i
        else:
            i = -i + 1
        goal_dir = rotate(goal_dir, i)
    self.log('line final')
    return goal_dir


"""
###################
"""

# BFS's etcs...


class Navigation(object):
    trajectory = []

    visited = []

    def __init__(self, robot_object, destination=None):
        self.destination = destination
        self.origin = (robot_object.me.x, robot_object.me.y)
        # self.passable_map = robot_object.passable_map

    def next_tile(self, robot_object):
        # Move in the target direction
        # If cannot move more, bug the walls
        # TODO change it
        return goto(robot_object, self.destination)

    def set_destination(self, destination):
        self.visited = []
        self.trajectory = []
        self.destination = destination

    def recalculate(self):
        # TODO
        return

#

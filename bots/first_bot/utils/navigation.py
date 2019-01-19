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
    # TODO just do it
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
    dx = destination[0] - origin[0]
    dy = destination[1] - origin[1]

    return (dx, dy)


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
    dx = destination[0] - origin[0]
    dy = destination[1] - origin[1]

    return (dx ** 2 + dy ** 2)


def man_distance(origin, destination):
    """ manhattan distance
    :param origin: location
    :param destination:
    :return: manhattan distance
    """
    dx = destination[0] - origin[0]
    dy = destination[1] - origin[1]
    return (abs(dx) + abs(dy))


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


def goto(bc_object, target):
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
    while is_occupied(bc_object, loc[0] + goal_dir[0], loc[1] + goal_dir[1]) and i < 4:
        # TODO make it able to bug
        # or apply_dir(loc, goal_dir) in already_been: # doesn't work because `in` doesn't work :(
        # alternate checking either side of the goal dir, by increasing amounts (but not past directly backwards)
        if i > 0:
            i = -i
        else:
            i = -i + 1
        goal_dir = rotate(goal_dir, i)
    # bc.log('line final')
    return goal_dir


"""
###################
"""

# BFS's etcs...


class Navigation(object):
    trajectory = []

    visited = []

    def __init__(self, destination=None):
        self.destination = destination
        # self.origin = (robot_object.me.x, robot_object.me.y)
        # self.passable_map = robot_object.passable_map

    def next_tile(self, robot_object):
        # Move in the target direction
        # If cannot move more, bug the walls
        # TODO improve it

        return goto(robot_object, self.destination)

    def set_destination(self, destination):
        self.visited = []
        self.trajectory = []
        self.destination = destination

#

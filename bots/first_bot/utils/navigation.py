#
from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import random
# import time

from bots.first_bot.utils import *


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

from:
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

        HITS = 40
        if bc.me.time > 1000:
            HITS = 70
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

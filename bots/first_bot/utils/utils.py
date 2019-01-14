#
import numpy as np
from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import random


# TODO test
def is_occupied(bc, x, y):
    """
    Check if that tile is occupied, impassable or outside the map
    :param bc: battlecode object
    :param x: x position
    :param y: y position
    :return: True if occupied False if not occupied
    """
    map_size = bc.game_info['map_size']
    if (x >= 0) and (y >= 0) and (x <= map_size) and (y <= map_size):
        # It is inside the map
        if bc.passable_map[y][x] > 0:
            # It is passable
            for robot in bc.vision_list:
                if (robot['x'] == x) and (robot['y'] == y):
                    # It is occupied by a robot
                    return True
            else:
                # It is NOT occupied by a robot
                return False
    return True


# TODO test
def is_not_occupied(bc, x, y):
    """
    Check if that tile is not occupied, not impassable or inside the map
    :param bc: battlecode object
    :param x: x position
    :param y: y position
    :return: True if NOT occupied False if occupied
    """
    return not is_occupied(bc, x, y)


# TODO test
def is_in_range(bc, x, y, range_squared):
    """
    Check if a target is within SQUARED range of the robot
    :param bc: battlecode object
    :param x: target_x
    :param y: target_y
    :param range: true range**2
    :return: True if it is in range, False if not
    """
    my_x = bc.me.x
    my_y = bc.me.y
    dx = my_x - x
    dy = my_y - y

    return (dx ** 2 + dy ** 2) <= range_squared


# TODO test
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
    bc.log('cost_ok: {}'.format(valid_cost))

    if valid_cost:
        # Enough Karb and Fuel
        # Check if occupied
        occupied = is_not_occupied(bc, x, y)
        bc.log('is not occupied?: {}'.format(occupied))
        return occupied

    # Not enough currency
    return valid_cost


# TODO test
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


def can_give(bc, dx, dy):
    """ bc is the battlecode object"""
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
            if robot.team == my_team and \
                    robot.x == loc[0] + dx and \
                    robot.y == loc[1] + dy:
                # Si tiene capacidad restante
                if robot.karbonite < karb_capacity and \
                        robot.fuel < fuel_capacity:
                    return True
    # Return true

    return False


# TODO test
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
    dx = my_x - x
    dy = my_y - y

    # Enough Fuel?
    fuel = bc.fuel
    unit_specs = SPECS['UNITS'][bc.me.unit]
    fuel_cost = unit_specs['FUEL_PER_MOVE'] * (dx ** 2 + dy ** 2)
    if fuel < fuel_cost:
        bc.log('Not enough Fuel to move')
        return False

    # Is it in range?
    if not is_in_range(bc, x, y, unit_specs['SPEED']):
        # Not in range
        return False

    # Is it occupied?
    occupied = is_not_occupied(bc, x, y)
    return occupied


# TODO test
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
    if not is_in_range(bc, x, y, unit_specs['ATTACK_RADIUS'][0]):
        # Check outside small range, then inside big one
        in_range = is_in_range(bc, x, y, unit_specs['ATTACK_RADIUS'][1])

    return in_range


# TODO test
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


def fast_distance(a, b):
    """
    Fast computation of distance using sqrt_einsum(self, x,y)
    :param a: points a as rows
    :param b: points b as rows
    :return: distance between a and b points
    """
    a_min_b = a - b
    return np.sqrt(np.einsum('ij,ij->i', a_min_b, a_min_b))

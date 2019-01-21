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
    map_size = len(bc.passable_map)
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


def is_walkable(bc, x, y):
    """
    Check if that tile is impassable or outside the map
    :param bc: battlecode object
    :param x: x position
    :param y: y position
    :return: True if occupied False if not occupied
    """
    map_size = len(bc.passable_map)
    if (x >= 0) and (y >= 0) and (x <= map_size) and (y <= map_size):
        # It is inside the map
        if bc.passable_map[y][x] > 0:
            # It is passable
            return True
    return False


def is_not_walkable(bc, x, y):
    """
    Check if that tile is not impassable or inside the map
    :param bc: battlecode object
    :param x: x position
    :param y: y position
    :return: True if NOT occupied False if occupied
    """
    return not is_walkable(bc, x, y)

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
def is_in_range(robot, x, y, range_squared):
    """
    Check if a target is within SQUARED range of the robot
    :param robot: robot object eg bc.me
    :param x: target_x
    :param y: target_y
    :param range_squared: true range**2
    :return: True if it is in range, False if not
    """
    my_x = robot.x
    my_y = robot.y
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
    # bc.log('cost_ok: {}'.format(valid_cost))

    if valid_cost:
        # Enough Karb and Fuel
        # Check if occupied
        occupied = is_not_occupied(bc, x, y)
        # bc.log('is not occupied?: {}'.format(occupied))
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


# # You cannot check other's unit karb and fuel
# def can_give(bc, dx, dy):
#     """ bc is the battlecode object"""
#     # Find if dx,dy can be given materials
#     unit_specs = SPECS['UNITS'][bc.me.unit]
#     fuel_capacity = unit_specs['FUEL_CAPACITY']
#     karb_capacity = unit_specs['KARBONITE_CAPACITY']
#     loc = (bc.me.x, bc.me.y)
#     my_team = bc.me.team
#     # Si tienes algun material
#     if bc.me.karbonite > 0 or bc.me.fuel > 0:
#         # Si hay un robot en dx, dy
#         for robot in bc.vision_list:
#             if robot.team == my_team and \
#                     robot.x == loc[0] + dx and \
#                     robot.y == loc[1] + dy:
#                 # Si tiene capacidad restante
#                 if robot.karbonite < karb_capacity and \
#                         robot.fuel < fuel_capacity:
#                     return True
#     # Return true
#
#     return False


def can_give(bc, castle):
    """ bc is the battlecode object"""
    # Find if dx,dy can be given materials
    x, y = bc.me.x, bc.me.y
    t_x, t_y = castle.x, castle.y
    # Si tienes algun material
    if bc.me.karbonite > 0 or bc.me.fuel > 0:
        # Is adjacent?
        return (x - t_x) ** 2 < 2 and (y - t_y) ** 2 < 2

    return False


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
    if not is_in_range(bc.me, x, y, unit_specs['SPEED']):
        # Not in range
        return False

    # Is it occupied?
    occupied = is_not_occupied(bc, x, y)
    return occupied


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
    if is_in_range(bc.me, x, y, unit_specs['ATTACK_RADIUS'][1]):
        # Check outside small range, then inside big one
        in_range = not is_in_range(bc.me, x, y, unit_specs['ATTACK_RADIUS'][0])
    return in_range


def team(robot):
    return robot['team']


def locate(robot):
    return (robot.x, robot.y)


def full_of_karb(self):
    unit_specs = SPECS['UNITS'][self.me.unit]
    return self.me.karbonite == unit_specs['KARBONITE_CAPACITY']


def is_attackable(bc_object, robot):
    """ Check if you can attack the robot included fuel cost etc."""
    return can_attack(bc_object, robot.x, robot.y)


def am_i_attackable(bc_object, robot):
    """ can I get attacked by robot """
    # is it an attacking unit
    u_specs = SPECS['UNITS'][robot.unit]
    if u_specs['ATTACK_DAMAGE'] is not None:
        # Within attack range
        return is_in_range(bc_object.me, robot.x, robot.y, u_specs['ATTACK_RADIUS'][1]) \
               and not is_in_range(bc_object.me, robot.x, robot.y, u_specs['ATTACK_RADIUS'][0])
    return False


def is_attackable_unit(robot_1, robot_2):
    """ check if robot 1 can attack robot 2"""
    unit_specs_1 = SPECS['UNITS'][robot_1.unit]
    if robot_1 and robot_2:
        # is it an attacking unit ?
        if unit_specs_1['ATTACK_DAMAGE'] is not None:
            # Within attack range ?
            return is_in_range(robot_1, robot_2.x, robot_2.y, unit_specs_1['ATTACK_RADIUS'][1]) \
                   and not is_in_range(robot_1, robot_2.x, robot_2.y, unit_specs_1['ATTACK_RADIUS'][0])


def im_at(bc, location):
    """
    Check if you are at specified position
    :param bc: battlecode object
    :param location: tuple of (x, y)
    :return: True if standing at that position
    """
    if location is None:
        bc.log('im_at: location passed was None')
        return False  # Default true to push for next castle?

    return bc.me.x == location[0] and bc.me.y == location[1]


# EXAMPLEFUNKY CODE

def reflect(bc, loc, horizontal=True):
    map_size = len(bc.passable_map)
    v_reflec = [map_size - loc[0], loc[1]]
    h_reflec = [loc[0], map_size - loc[1]]
    if horizontal:
        return h_reflec
    else:
        return v_reflec


# EXAMPLEFUNKY CODE
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

#

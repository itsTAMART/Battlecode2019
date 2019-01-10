import numpy as np
from battlecode import BCAbstractRobot, SPECS


def can_build(self, unit_name):
    """
    Helper method for building units
    :param self:
    :param unit_name: name of the unit to build e.g. PILGRIM
    :return: True if you have materials to build unit
    """
    karb = self.karbonite
    fuel = self.fuel
    # self.log('Karb: {}, Fuel: {}'.format(karb,fuel))
    unit_specs = SPECS['UNITS'][SPECS[unit_name]]
    karb_cost = unit_specs['CONSTRUCTION_KARBONITE']
    fuel_cost = unit_specs['CONSTRUCTION_FUEL']
    # self.log('Karb_c: {}, Fuel_c: {}'.format(karb_cost, fuel_cost))
    # TODO check adjacent tiles
    result = (karb >= karb_cost) and (fuel >= fuel_cost)
    self.log('result: {}'.format(result))
    return result


def can_move(self):
    fuel = self.fuel

    unit_specs = SPECS['UNITS'][SPECS[self.me.unit]]
    fuel_cost = unit_specs['FUEL_PER_MOVE']  # TODO multiply by the distance
    if fuel < fuel_cost:
        self.log('Not enough Fuel to move')
        return False

    # TODO check if it is occupied
    return False


def can_attack(self):
    fuel = self.fuel

    unit_specs = SPECS['UNITS'][SPECS[self.me.unit]]
    fuel_cost = unit_specs['ATTACK_FUEL_COST']
    if fuel < fuel_cost:
        self.log('Not enough Fuel to attack')
        return False

    # TODO check if it is in range
    return False


def fast_distance(a, b):
    """
    Fast computation of distance using sqrt_einsum(self, x,y)
    :param a: points a as rows
    :param b: points b as rows
    :return: distance between a and b points
    """
    a_min_b = a - b
    return np.sqrt(np.einsum('ij,ij->i', a_min_b, a_min_b))

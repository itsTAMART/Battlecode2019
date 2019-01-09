import numpy as np


def can_build(name='PILGRIM', karbonite=0, fuel=0):
    """
    Helper method for building units
    :param name:
    :param karbonite:
    :param fuel:
    :return: True if you have mateials to build unit
    """
    if name == 'CHURCH':
        return karbonite >= 50 & fuel >= 200

    elif name == 'PILGRIM':
        return karbonite >= 10 & fuel >= 50

    elif name == 'CRUSADER':
        return karbonite >= 20 & fuel >= 50

    elif name == 'PROPHET':
        return karbonite >= 25 & fuel >= 50

    elif name == 'PREACHER':
        return karbonite >= 30 & fuel >= 50
    else:
        print('{} not known'.format(name))
        return False

    return False


def can_move():
    # TODO
    return False


def can_attack():
    # TODO
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

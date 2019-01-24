#
from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import random

from bots.first_bot.utils import *

# TODO implement game logic
"""
TODO: here I will include when to go with each strat. with flags

for ECON: big_map, no castle is closer than 31 f.e.
            {build pilgrim with destiny to middle mine and save_for_church = True}
            {check if other castles are going for eco and mark it too.}

for RUSH: castle closer than 31, less than 7 mines of one resource
        {create phrophet, phrophet, crusader (maybe?) and give them the rush target}
        {check if other castles in rush so that chuch comes later}

for FAKE_RUSH:  no castle is closer than 35, but not further than 45 and 1 or 2 castles
                {creathe phrophet, pilgrim and save for church}
                {check if other castles are going for FAKE_RUSH and mark it too.}

GENERALLY create pilgrims for each of the mines you have assigned

Create pilgrims for karbonite first except if RUSH then go for fuel

if BEING_ATTACKED create counter phrophet: crusader, crusader: preacher, preacher: phrophets

if no pilgrims left to mine start creating a PHROPHETS for ARCHER LATTICE

"""


# TODO
class Tactics(object):
    ECON = True  # True by default
    RUSH = False
    FAKE_RUSH = False

    fuel_scarce = False
    karb_scarce = False

    def __init__(self, bc):
        bc.log('Tactics initialized')

    def game_type(self):
        # TODO implement it
        pass

    def get_rush_targets(self, bc):
        """
         returns a castle or a mine
        :param bc: object
        :return:  list of targets for spawning the bots
        """
        # TODO implement it
        return []

    def under_attack(self, bc):
        """
        Checks the messages and vision to see if we are being attacked
        :param bc:
        :return: True or False
        """
        # TODO implement it
        return False

    def counter_unit(self, bc):
        """
        Returns the most effective unit against the attack received
        :param bc:
        :return: unit name
        """
        # TODO implement it
        unit_types = ["CRUSADER", "PROPHET", "PREACHER"]
        return "CRUSADER"

    def lategame_unit(self, bc):
        """
        Returns the most effective unit for lategame according to gametype
        :param bc:
        :return: unit name
        """
        # TODO implement it
        unit_types = ["CRUSADER", "PROPHET", "PREACHER"]
        return "CRUSADER"

    def lategame_target(self, bc):
        """
        Returns the most effective target location for lategame according to gametype
        :param bc:
        :return: tuple with a location
        """
        # TODO implement it
        return None


#

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
    close_castle = False
    fuel_scarce = False
    karb_scarce = False

    def __init__(self, bc):
        # bc.log('Tactics initialized')
        pass

    def game_type_1(self, bc):
        """ to be called in the first turn """
        bc.log('Deciding game type')
        # if small map, RUSH
        if bc.map_process.map_size < 40:  # SMALL MAP
            bc.log('    small map, RUSH')
            self.ECON = False
            self.RUSH = True

        # if map big, ECON
        if bc.map_process.map_size > 58:  # SMALL MAP
            bc.log('    map big, ECON')
            self.ECON = True
            self.RUSH = False

        # if 3 castles, ECON
        bc.map_process.get_n_castles(bc)
        if bc.map_process.n_castles > 2:
            bc.log('    s3 castles, ECON')
            self.ECON = True
            self.RUSH = False

        # else FAKE_RUSH
        if bc.map_process.n_castles < 3:
            bc.log('    <= 2 castles, FAKERUSH')
            self.ECON = False
            self.RUSH = True
            self.FAKE_RUSH = True

        # if close castle, RUSH
        if self.distance_of_castles(bc, locate(bc.me)) < 26:
            self.close_castle = True
            self.ECON = False
            self.RUSH = True

        # if karb resource scarce, RUSH karb
        if len(bc.map_process.karb_mines) < 7:
            bc.log('    karb resource scarce, RUSH karb')
            self.karb_scarce = True
            self.ECON = False
            self.RUSH = True
        # if fuel resource scarce, RUSH fuel
        if len(bc.map_process.fuel_mines) < 7:
            bc.log('    fuel resource scarce, RUSH fuel')
            self.fuel_scarce = True
            self.ECON = False
            self.RUSH = True

    def distance_of_castles(self, bc, loc):
        """ returns straight line distance """
        horizontal = bc.map_process.horizontal_reflection
        x, y = loc
        map_size = bc.map_process.map_size
        d = map_size
        if horizontal:
            d = abs(map_size - 2 * x)
        else:
            d = abs(map_size - 2 * y)
        return d


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

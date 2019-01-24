#
from battlecode import BCAbstractRobot, SPECS

# from .units import *
from bots.first_bot.units.castle import *
from bots.first_bot.units.church import *
from bots.first_bot.units.pilgrim import *
from bots.first_bot.units.crusader import *
from bots.first_bot.units.preacher import *
from bots.first_bot.units.prophet import *
from .tactics import *

__pragma__('iconv')
__pragma__('tconv')
__pragma__('opov')


# don't try to use global variables!!
class MyRobot(BCAbstractRobot):

    # Lists and maps
    vision_list = []
    vision_map = []
    passable_map = []
    karbonite_map = []
    fuel_map = []

    # Unit Variables
    # useful_locations
    destination = None
    spawn_loc = None
    church_spot = None

    # Game info blob
    game_info = None

    # Personal stats
    fuel_consumed = 0
    step = -1
    stuck = 0

    # Helper Objects
    build_order = None
    nav = None
    combat = None
    map_process = None
    comms = None


    def turn(self):
        """

        :return: action
        """
        self.step += 1

        """
    
            FIRST TURN PREPROCESS HERE   
    
            GENERAL FIRST TURN
    
    
        """
        if self.step == 0:  # First Turn shenanigans
            self.passable_map = self.get_passable_map()
            self.karbonite_map = self.get_karbonite_map()
            self.fuel_map = self.get_fuel_map()

            first_turn_monitor(self)  # Log firs turn info

            # Helper objects
            self.comms = Communications(self)
            self.map_process = MapPreprocess()
            self.nav = Navigation()
            self.combat = CombatManager(self)
            self.tactics = Tactics(self)
            self.map_process.get_initial_game_info(self)

        """
        GENERAL PRE-TURN HERE

        """
        self.vision_map = self.get_visible_robot_map()
        self.vision_list = self.get_visible_robots()
        self.comms.turn(self)  # Turn routine for communications
        self.combat.turn(self)  # Turn routine for classifying vision robots
        unit_monitor(self)

        """

            SPECIFIC FIRST TURN

        """
        if self.step == 0:  # First Turn shenanigans
            if self.me['unit'] == SPECS['CASTLE']:
                first_turn_castle(self)
            elif self.me['unit'] == SPECS['CHURCH']:
                first_turn_church(self)
            elif self.me['unit'] == SPECS['PILGRIM']:
                first_turn_pilgrim(self)
            elif self.me['unit'] == SPECS['CRUSADER']:
                first_turn_crusader(self)
            elif self.me['unit'] == SPECS['PROPHET']:
                first_turn_prophet(self)
            elif self.me['unit'] == SPECS['PREACHER']:
                first_turn_preacher(self)

        """

        SPECIFIC ACTIONS HERE

        """
        if self.me['unit'] == SPECS['CASTLE']:
            return castle(self)
        elif self.me['unit'] == SPECS['CHURCH']:
            return church(self)
        elif self.me['unit'] == SPECS['PILGRIM']:
            return pilgrim(self)
        elif self.me['unit'] == SPECS['CRUSADER']:
            return crusade(self)
        elif self.me['unit'] == SPECS['PROPHET']:
            return prophet(self)
        elif self.me['unit'] == SPECS['PREACHER']:
            return preacher(self)

        """
        ########################################################################
        """


robot = MyRobot()

#

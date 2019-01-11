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

    # Game info blob
    game_info = None

    # Personal stats
    fuel_consumed = 0
    step = -1

    # Helper Objects
    build_order = None



    def turn(self):
        """

        :return: action
        """
        self.step += 1

        if self.step == 0:  # First Turn shenanigans
            """
    
            FIRST TURN PREPROCESS HERE   
    
            GENERAL FIRST TURN
    
    
            """
            self.passable_map = self.get_passable_map()
            self.karbonite_map = self.get_karbonite_map()

            self.game_info = get_initial_game_info(self)

            first_turn_monitor(self)  # Log firs turn info

            """

            SPECIFIC FIRST TURN

            """
            # TODO reactivate units
            if self.me['unit'] == SPECS['CASTLE']:
                # self.log('castle')
                first_turn_castle(self)
            # elif self.me['unit'] == SPECS['CHURCH']:
            #     firs_turn_church(self)
            # elif self.me['unit'] == SPECS['PILGRIM']:
            #     # self.log('pilgrim')
            #     firs_turn_pilgrim(self)
            # elif self.me['unit'] == SPECS['CRUSADER']:
            #     first_turn_crusade(self)
            # elif self.me['unit'] == SPECS['PROPHET']:
            #     firs_turn_prophet(self)
            # elif self.me['unit'] == SPECS['PREACHER']:
            #     firs_turn_preach(self)




        """
        GENERAL PRE-TURN HERE

        """
        self.vision_map = self.get_visible_robot_map()
        self.vision_list = self.get_visible_robots()
        unit_monitor(self)

        """

        SPECIFIC ACTIONS HERE

        """
        # TODO reactivate units
        if self.me['unit'] == SPECS['CASTLE']:
            return castle(self)
        # elif self.me['unit'] == SPECS['CHURCH']:
        #     return church(self)
        elif self.me['unit'] == SPECS['PILGRIM']:
            return pilgrim(self)
        elif self.me['unit'] == SPECS['CRUSADER']:
            return crusade(self)
        # elif self.me['unit'] == SPECS['PROPHET']:
        #     return prophet(self)
        # elif self.me['unit'] == SPECS['PREACHER']:
        #     return preach(self)

        """
        ########################################################################
        """


robot = MyRobot()

#

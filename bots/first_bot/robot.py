from battlecode import BCAbstractRobot, SPECS

# from .units import *
from bots.first_bot.units.castle import *
from bots.first_bot.units.church import *
from bots.first_bot.units.pilgrim import *
from bots.first_bot.units.crusader import *
from bots.first_bot.units.preacher import *
from bots.first_bot.units.prophet import *


__pragma__('iconv')
__pragma__('tconv')
__pragma__('opov')


# don't try to use global variables!!
class MyRobot(BCAbstractRobot):
    step = -1
    fuel_consumed = 0
    vision_list = []
    vision_map = []
    passable_map = []
    karbonite_map = []
    game_info = None

    def turn(self):
        """

        :return: action
        """
        self.step += 1
        if self.step == 0:
            """
    
            FIRST TURN PREPROCESS HERE   
    
            GENERAL AND SPECIFIC
    
    
            """
            self.passable_map = self.get_passable_map()
            self.karbonite_map = self.get_karbonite_map()
            # TODO create a method to gather info of the map, size, type, n_castles etc...
            self.game_info = get_initial_game_info(self)
            self.log('Map size {}x{}'.format(self.game_info['map_size'],
                                             self.game_info['map_size']))

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
            # self.log('castle')
            return castle(self)

        # elif self.me['unit'] == SPECS['CHURCH']:
        #     church(self)

        elif self.me['unit'] == SPECS['PILGRIM']:
            #self.log('pilgrim')
            return pilgrim(self)
        #
        # elif self.me['unit'] == SPECS['CRUSADER']:
        #     crusade(self)
        #
        # elif self.me['unit'] == SPECS['PROPHET']:
        #     prophet(self)
        #
        # elif self.me['unit'] == SPECS['PREACHER']:
        #     preach(self)

        """
        ########################################################################
        """


robot = MyRobot()

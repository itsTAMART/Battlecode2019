from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import random

# from bots.first_bot.units.crusader import *
# from bots.first_bot.units.castle import *
from .units import *

__pragma__('iconv')
__pragma__('tconv')
__pragma__('opov')


# don't try to use global variables!!
class MyRobot(BCAbstractRobot):
    step = -1

    """
    
    PREPROCESS HERE   
    
    GENERAL AND SPECIFIC
    
    
    """

    def turn(self):
        self.step += 1

        """
        GENERAL PRE-TURN HERE
        
        """

        self.log("START TURN " + self.step)

        """
        
        SPECIFIC ACTIONS HERE
        
        """

        if self.me['unit'] == SPECS['CASTLE']:
            castle(self)

        elif self.me['unit'] == SPECS['CHURCH']:
            church(self)

        elif self.me['unit'] == SPECS['PILGRIM']:
            pilgrim(self)

        elif self.me['unit'] == SPECS['CRUSADER']:
            crusade(self)

        elif self.me['unit'] == SPECS['PROPHET']:
            prophet(self)

        elif self.me['unit'] == SPECS['PREACHER']:
            preach(self)

        """
        ########################################################################
        """


robot = MyRobot()

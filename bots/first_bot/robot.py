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

    """

    PREPROCESS HERE   

    GENERAL AND SPECIFIC


    """

    def turn(self):
        self.step += 1

        """
        GENERAL PRE-TURN HERE

        """

        self.log("turn " + self.step)

        """

        SPECIFIC ACTIONS HERE

        """

        if self.me['unit'] == SPECS['CASTLE']:
            self.log('castle')
            return castle(self)

        # elif self.me['unit'] == SPECS['CHURCH']:
        #     church(self)

        elif self.me['unit'] == SPECS['PILGRIM']:
            self.log('pilgrim')
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

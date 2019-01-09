from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import random

__pragma__('iconv')
__pragma__('tconv')
__pragma__('opov')


def can_build(self, unit_name):
    """
    Helper method for building units
    :param self:
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


def castle(self):
    if can_build(self, 'PILGRIM'):
        choices = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
        choice = random.choice(choices)
        self.log("Building a pilgrim at " + str(self.me['x'] + 1) + ", " + str(self.me['y'] + 1))
        return self.build_unit(SPECS['PILGRIM'], *choice)

    else:
        self.log("Castle health: " + self.me['health'])


def pilgrim(self):
    self.log('Pilgrim {}'.format(self.id))

    # SOMETHING HERE TIMES OUT
    # self.log('#' * 80)
    # self.log(self.get_visible_robots())
    # self.log('#' * 80)
    # self.log(self.get_visible_robot_map())
    # self.log('#' * 80)
    # self.log(self.get_passable_map())
    # self.log('#' * 80)
    # self.log(self.get_karbonite_map())
    # self.log('#' * 80)
    # self.log('Karb: {}, Fuel: {}'.format(self.karbonite, self.fuel))
    #
    # self.log('#' * 80)

    # Move to closest non-occupied mine
    self.log('moving to closest non occupied mine')

    # Temporal walking code
    choices = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
    choice = random.choice(choices)
    self.log('TRYING TO MOVE IN DIRECTION ' + str(choice))
    return self.move(*choice)

    # # Mine
    # self.log('mining')


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

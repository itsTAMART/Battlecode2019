
from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import random


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


from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import random


def pilgrim(self):
    # Move to closest non-occupied mine

    # Temporal walking code
    choices = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
    choice = random.choice(choices)
    self.log('TRYING TO MOVE IN DIRECTION ' + str(choice))
    return self.move(*choice)

    # # Mine
    # self.log('mining')

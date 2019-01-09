from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import random


def pilgrim(self):
    self.log('Pilgrim {}'.format(self.id))

    self.log('#' * 80)
    self.log(self.get_visible_robots())
    self.log('#' * 80)
    self.log(self.get_visible_robot_map())
    self.log('#' * 80)
    self.log(self.get_passable_map())
    self.log('#' * 80)
    self.log(self.get_karbonite_map())
    self.log('#' * 80)
    self.log('Karb: {}, Fuel: {}'.format(self.karbonite, self.fuel))

    self.log('#' * 80)

    # Move to closest non-occupied mine
    self.log('moving to closest non occupied mine')
    # Mine
    self.log('mining')

from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import random


def crusade(self):
    self.log("Crusader health: " + str(self.me['health']))

    visible = self.get_visible_robots()

    # get attackable robots
    attackable = []
    for r in visible:
        # x = 5
        # if not self.is_visible(r):
        if 'x' not in r:  # not visible. hacky. do not use at home
            continue
        # now all in vision range, can see x, y etc
        dist = (r['x'] - self.me['x']) ** 2 + (r['y'] - self.me['y']) ** 2
        if r['team'] != self.me['team'] and SPECS['UNITS'][SPECS["CRUSADER"]]['ATTACK_RADIUS'][0] <= dist <= \
                SPECS['UNITS'][SPECS["CRUSADER"]]['ATTACK_RADIUS'][1]:
            attackable.append(r)

    if attackable:
        # attack first robot
        r = attackable[0]
        self.log('attacking! ' + str(r) + ' at loc ' + (r['x'] - self.me['x'], r['y'] - self.me['y']))
        return self.attack(r['x'] - self.me['x'], r['y'] - self.me['y'])

    # The directions: North, NorthEast, East, SouthEast, South, SouthWest, West, NorthWest
    choices = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
    choice = random.choice(choices)
    self.log('TRYING TO MOVE IN DIRECTION ' + str(choice))
    return self.move(*choice)

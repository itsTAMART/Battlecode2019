#
from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
from bots.first_bot.utils import *

C2T = {
    0: 'YOUR_MINE_IS',
    1: 'GO_MINE_BUILD_CHURCH',
    2: 'SCOUT_RUSH',
    3: 'FAVORABLE_FIGHT_AT',
    4: 'UNFAVORABLE_FIGHT_AT',
    5: 'not_implemented_yet',
    6: 'not_implemented_yet',
    7: 'not_implemented_yet',
    8: 'not_implemented_yet',
    9: 'not_implemented_yet',
    10: 'not_implemented_yet',
    11: 'not_implemented_yet',
    12: 'not_implemented_yet',
    13: 'not_implemented_yet',
    14: 'not_implemented_yet',
    15: 'not_implemented_yet',
    16: 'not_implemented_yet'
}

T2C = {
    'YOUR_MINE_IS': 0,
    'GO_MINE_BUILD_CHURCH': 1,
    'SCOUT_RUSH': 2,
    'FAVORABLE_FIGHT_AT': 3,
    'UNFAVORABLE_FIGHT_AT': 4,
    # 'not_implemented_yet':5 ,
    # 'not_implemented_yet':6 ,
    # 'not_implemented_yet':7 ,
    # 'not_implemented_yet':8 ,
    # 'not_implemented_yet':9 ,
    # 'not_implemented_yet':10 ,
    # 'not_implemented_yet':11 ,
    # 'not_implemented_yet':12 ,
    # 'not_implemented_yet':13 ,
    # 'not_implemented_yet':14 ,
    # 'not_implemented_yet':15 ,
    # 'not_implemented_yet':16
}

# For CASTLE TALK 2 ^ 8 - 1
M2T = {
    0: 'CASTLE_AT',
    1: 'CHURCH_AT',
    2: 'HELLO_CHURCH',
    3: 'not_implemented_yet',
    4: 'not_implemented_yet',
    5: 'not_implemented_yet',
    6: 'not_implemented_yet',
    7: 'not_implemented_yet'
}

# For CASTLE TALK 2 ^ 8 - 1
T2M = {
    'CASTLE_AT': 0,
    'CHURCH_AT': 1,
    'HELLO_CHURCH': 2,
    # 'not_implemented_yet':3 ,
    # 'not_implemented_yet':4 ,
    # 'not_implemented_yet':5 ,
    # 'not_implemented_yet':6 ,
    # 'not_implemented_yet':7 ,
    'null': 256
}

#

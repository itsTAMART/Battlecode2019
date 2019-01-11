#
from battlecode import BCAbstractRobot, SPECS
import battlecode as bc
import random

# def get_karb_mines(self):
#     self.karbonite_map()

# TODO create a method to gather info of the map, size, type, n_castles etc..
def get_initial_game_info(self):
    info = {
        'map_size': len(self.passable_map[0])
    }

    return info
#

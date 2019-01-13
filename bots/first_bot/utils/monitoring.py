#
TYPES = ["CASTLE", "CHURCH", "PILGRIM", "CRUSADER", "PROPHET", "PREACHER"]


def first_turn_monitor(self):
    # TODO do it
    self.log('Map size {}x{}'.format(self.game_info['map_size'],
                                     self.game_info['map_size']))


def unit_monitor(self):
    #  Unit type, id
    #  Turn, Turns alive
    #  Total consumption

    message = '- \n' \
              ' Type: {unit_type}, id: {id} \n' \
              ' turn: {turn}, alive: {alive} \n' \
              ' fuel consumed: {fuel} \n' \
              ' my position: {position} \n' \
              ' my goal: {goal} \n' \
              '- \n'.format(
        unit_type=TYPES[self.me['unit']],
        id=self.me['id'],
        turn=self.me['turn'],
        alive=self.step,
        fuel=self.fuel_consumed,
        position=(self.me.x, self.me.y),
        goal=self.destination
    )
    self.log(message)

    return

# TODO specific monitors for each units
# Carrying materials
#

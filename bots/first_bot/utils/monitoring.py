TYPES = ["CASTLE", "CHURCH", "PILGRIM", "CRUSADER", "PROPHET", "PREACHER"]


def unit_monitor(self):
    #  Unit type, id
    #  Turn, Turns alive
    #  Total consumption

    message = '- \n' \
              ' Type: {unit_type}, id: {id} \n' \
              ' turn: {turn}, alive: {alive} \n' \
              ' fuel consumed: {fuel} \n ' \
              '- \n'.format(
        unit_type=TYPES[self.me['unit']],  # TODO left here
        id=self.me['id'],
        turn=self.me['turn'],
        alive=self.step,
        fuel=self.fuel_consumed
    )
    self.log(message)

    return

# TODO specific monitors for each units
# Carrying materials

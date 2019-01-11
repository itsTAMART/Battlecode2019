#


FIRST_BUILD_ORDER = ["PILGRIM", "CRUSADER", "CRUSADER",
                     "PILGRIM", "CRUSADER", "CRUSADER",
                     "PILGRIM", "PILGRIM", "CRUSADER"]

BUILD_ORDER = FIRST_BUILD_ORDER


# TODO test
class BuildOrderManager(object):
    # TODO something left to synchronize castles

    def __init__(self, build_order):
        self.build_order = build_order
        self.build_step = 0

    def current_order(self):
        build_step = min(self.build_step, len(self.build_order) - 1)  # Hacky -1 to keep it in bounds
        return self.build_order[build_step]

    def next_order(self):
        build_step = min(self.build_step, len(self.build_order) - 2)  # Hacky -2 to keep it in bounds
        return self.build_order[build_step + 1]

    def built_correctly(self):
        self.build_step += 1
        self.build_step = min(self.build_step, len(self.build_order) - 1)  # Hacky -2 to keep it in bounds

#

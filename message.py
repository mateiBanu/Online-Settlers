START_TURN = 0
ROLL = 1
INIT_VILLAGE = 2
BUILD_ROAD = 3
BUILD_VILLAGE = 4
BUILD_CITY = 5
PAY_RES = 6
PAY_DEVS = 7
LONGEST_ROAD = 8
LARGEST_ARMY = 9
INIT_ROAD = 10
ROBBER = 11

MESSAGE_SIZE = 2048


class Message:
    def __init__(self, flag, player, data):
        self.flag = flag
        self.player = player
        self.data = data

# By Tom Hotchkiss
import csv


class Room:
    def __init__(self, name='', north=None, south=None, east=None, west=None, teleporter=False, item=None):
        self.name = name
        self.north = north
        self.south = south
        self.east = east
        self.west = west
        self.teleporter = teleporter
        self.item = item

    def __str__(self):
        return 'Name: {}\nNorth: {}\nSouth: {}\nEast: {}\nWest: {}\nTeleporter: {}\nItem: {}' \
            .format(self.name, self.north, self.south, self.east, self.west, self.teleporter, self.item)

    def pickup_item(self, item_name):
        '''picks up the item in the room if it has the correct name, returns true if successful, false otherwise'''
        if item_name == self.item:
            self.item = None
            return True
        else:
            return False

    def is_adjacent(self, other_room):
        '''returns true if the room connects to the room passed as argument, false otherwise
        does not consider teleporters to be connected'''
        if self.north == other_room.name or self.south == other_room.name or self.east == other_room.name \
                or self.west == other_room.name:
            return True
        else:
            return False


class Character:
    def __init__(self, name='', location=Room(), human=False, movement_speed=1):
        self.inventory = []
        self.name = name
        self.location = location
        self.human = human
        self.movement_speed = movement_speed

    def __str__(self):
        return 'Name: {}\nLocation: {}\nHuman: {}\nMovement speed: {}\nInventory: {}\n'.format(
            self.name, self.location.name, self.human, self.movement_speed, self.inventory
        )


def init_rooms():
    rooms = []
    with open('Room List.csv', 'r') as csvfile:
        room_list = csv.reader(csvfile, delimiter=',')
        for room in room_list:
            new_room = Room(room[0], room[1], room[2], room[3], room[4], bool(room[5]), room[6])
            rooms.append(new_room)
    rooms.pop(0)
    return rooms


def init_map(room_list):
    map_indexes = [[0, 1, 1, 1, 1, 1, 1, 0],
                   [1, 1, 1, 1, 1, 1, 1, 0],
                   [0, 1, 1, 1, 1, 1, 1, 1],
                   [0, 1, 1, 1, 1, 1, 1, 0]]
    ship_map = []
    room_index = 0
    for row in map_indexes:
        map_row = []
        for col in row:
            if col == 0:
                map_row.append(None)
            elif col == 1:
                map_row.append(room_list[room_index])
                room_index += 1
        ship_map.append(map_row.copy())
    return ship_map


def init_players(rooms):
    name = input('Enter your name: ')
    player = Character(name, rooms[6], True)  # rooms[6] is player starting position, or Earth Transporter
    robot = Character('Pap-AI', rooms[17])    # rooms[17] is robot's starting position, or Laboratory
    return player, robot


def print_map(my_map, player):
    player_location = player.location
    print('_' * 198)
    for row in my_map:
        for col in row:
            if col is None:
                room_name = ''
            elif col is player_location:
                room_name = player.name
            else:
                room_name = col.name
            formatted_name = '| {name:^20} | '
            print(formatted_name.format(name=room_name), end='')
        print('\n', '_' * 198)


def play_game():
    room_list = init_rooms()
    ship_map = init_map(room_list)
    player, robot = init_players(room_list)
    show_instructions()
    gameover = False
    while not gameover:
        gameover = process_command(get_command(), ship_map, player)


def show_instructions():
    """Displays initial room and explains game rules"""
    print('**********************************************************************************************\n'
          '*                           Welcome to the Spaceship Escape Game!                            *\n'
          '* Your goal is to collect of the items before encountering the rogue AI known as PAP-AI      *\n'
          '* PAP-AI starts in the Laboratory, so be sure to avoid that until you\'re ready!              *\n'
          '* Good luck and have fun!                                                                    *\n'
          '**********************************************************************************************\n')


def show_status(player):
    print('Name: {}'.format(player.name))
    print('You are in: {}'.format(player.location.name))
    #TODO print adjacent rooms
    if player.human:
        print('Inventory: {}'.format(player.inventory))
    print()


def get_command():
    """Displays possible commands to the player.
    Gets user input, and returns the selected command.

    """
    print('Please choose one of the following actions (type a number): ')
    print('1) Move')
    print('2) Pickup Item')
    print('3) Print Map')
    print('4) Show Status')
    print('5) Quit')

    command = int(input())
    print()
    if command == 1:
        command = 'move'
    elif command == 2:
        command = 'item'
    elif command == 3:
        command = 'map'
    elif command == 4:
        command = 'status'
    elif command == 5:
        command = 'quit'
    else:
        command = 'invalid'

    return command


def process_command(command, my_map, player):
    if command == 'move':
        return False
    elif command == 'item':
        return False
    elif command == 'map':
        print_map(my_map, player)
        return False
    elif command == 'status':
        show_status(player)
        return False
    elif command == 'quit':
        return True
    elif command == 'invalid':
        print('You have entered an invalid command.  Please try again.\n')
        return False


if __name__ == "__main__":
    # calls the core gameplay loop
    play_game()

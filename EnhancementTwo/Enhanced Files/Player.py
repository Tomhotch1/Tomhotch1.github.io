from Character import Character

class Player(Character):

    def __init__(self, map, name, location):
        """
        Constructor for the Player class.
        Initializes location, inventory, name and ties the Player to a Map.
        
        @param map, the Map object on which the Player will exist.
        @param name, the player's name.
        @param location, the initial location for the player.
        """
        super().__init__(map, name, location)
        self.inventory = []


    def moveTo(self, new_room_name):
        """
        Given a valid room name, moves the Character there
        and updates the color and visited statuses for the Map.

        @param new_room_name, the name of the room to move to.
        """
        # Update neighboring room color status, and move to new room.
        self.update_position(new_room_name)

        # Get accessible and locked neighbors and update color status
        # to either green or red respectively.
        accessible_neighbors = self.map.get_accessible(self.location)
        locked_neighbors = self.map.get_inaccessible(self.location)
        for adjacent_room in accessible_neighbors:
            adjacent_room.color = 'green'
        if locked_neighbors:
            for adjacent_room in locked_neighbors:
                adjacent_room.color = 'red'
    

    def attempt_move(self, direction):
        """
        Attempts to move the Character in a given direction. 
        Will print an error if the direction is invalid.

        @param direction, the direction to move.
        @return moved, True if the player successfully moved, False otherwise
        """
        x_pos = self.location.x_pos
        y_pos = self.location.y_pos
        new_room = None

        # Adjust x/y coordinates based on direction.
        if direction == 'north':
            y_pos += 1
        elif direction == 'south':
            y_pos -= 1
        elif direction == 'east':
            x_pos += 1
        elif direction == 'west':
            x_pos -= 1

        # If using a teleporter, get the direct location from the Map.
        elif direction == 'teleport':
            new_room = self.map.next_teleporter(self.location)
        # If not using a teleporter, update the location from new x/y coordinates.
        if new_room is None:
            new_room = self.map.room_from_coordinates(x_pos, y_pos)

        moved = False
        # Check if the new room exists, and move there if so.
        if new_room is not None:
            self.moveTo(new_room.name)
            moved = True
        # New room isn't valid, print an error.
        else:
            print('There is no accessible room to the {}.'.format(direction))
        return moved



    def update_position(self, new_room_name):
        """
        Updates the Character's location based on a given room name.
        
        @param new_room_name, name of the room to move to.
        """
        # Check if Character is already in a room, if not can set location directly.
        if self.location == None:
            self.location = self.map.get_room(new_room_name)
        # Update current room and neighbors' color status.
        else:
            self.location.color = 'grey'
            adjacent_rooms = self.map.get_neighbors(self.location)
            for adjacent_room in adjacent_rooms:
                if adjacent_room.visited:
                    adjacent_room.color = 'grey'
                else:
                    adjacent_room.color = 'black'
            # Execute move
            self.location = self.map.get_room(new_room_name)

        self.location.visited = True
        self.location.color = 'blue'


    def pickup_item(self):
        """
        Picks up the item in the Character's current room
        and prints either a confirmation or error.
        """
        # No item in the room. Print an error.
        if self.location.item == 'None':
            print('There is no item in this room.\n')
        # Add room to inventory and remove from the room.
        elif self.location.item not in self.inventory:
            print('Picked up {}.\n'.format(self.location.item))
            self.inventory.append(self.location.item)
            self.location.item = 'None'
        # Item would be a duplicate, print an error.
        else:
            print('{} was already in your inventory.\n'.format(self.location.item))

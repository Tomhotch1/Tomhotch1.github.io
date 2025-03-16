class Room:

    def __init__(self, x_pos, y_pos):
        """
        Constructor for the Room class.  Initializes position, name, type, neighbors, etc.
        
        @param x_pos, the x Map coordinate for the room.
        @param y_pos, the y Map coordinate for the room.
        """
        self.name = ''
        self.item = ''
        self.type = 'empty'
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.color = 'black'
        self.visited = False
        self.north = None
        self.south = None
        self.east = None
        self.west = None
        self.adjacent_rooms = []
        self.locked_neighbors = []


    def __str__(self):
        """
        Converts the Room's name, neighboring rooms, and item to a string for printing.
        """
        return '{}\nNorth: {}\nSouth: {}\nEast: {}\nWest: {}\nItem: {}' \
            .format(self.name, self.north, self.south, self.east, self.west, self.item)
    

    def update(self, name, item, north='None', south='None', east='None', west='None'):
        """
        Updates the room's name, neighboring rooms, and item.

        @param name, the name of the room.
        @param north, the name of the room to the north.
        @param south, the name of the room to the south.
        @param east, the name of the room to the east.
        @param west, the name of the room to the west.
        @param item, the name of the item in the room, if any.
        """
        self.name = name
        self.item = item

        # Sets the room's type to teleporter if it is one.
        if 'Teleporter' in self.name:
            self.type = 'teleporter'
        else:
            self.type = 'normal'
        
        # Adds the adjacent rooms to the list.
        self.add_adjacent(north, south, east, west)
        
    
    def add_adjacent(self, north, south, east, west):
        """
        Adds neighboring accessible rooms to the acjacent_rooms list.

        @param north, the name of the room to the north.
        @param south, the name of the room to the south.
        @param east, the name of the room to the east.
        @param west, the name of the room to the west.
        """
        if north != 'None':
            self.north = north
            self.adjacent_rooms.append(north)
        if south != 'None':
            self.south = south
            self.adjacent_rooms.append(south)
        if east != 'None':
            self.east = east
            self.adjacent_rooms.append(east)
        if west != 'None':
            self.west = west
            self.adjacent_rooms.append(west)
        
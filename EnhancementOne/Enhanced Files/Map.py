import matplotlib.pyplot as plt
import numpy as np
import csv
import Room
import matplotlib.patches as mpatches
import random

class Map:

    def __init__(self, room_list_path, grid_size):
        """
        Constructor for the map class.  Creates a grid of empty rooms, then populates it
        using a precreated csv file.

        @param room_list_path, the relative path of the csv file.
        @param grid_size, the side length of the internal square of the grid.
        """
        self.max_rooms = (grid_size ** 2) + 1   # max rooms is a a full square of grid_size + one starting room
        self.grid_size = grid_size + 2          # add a border of empty cells
        self.room_grid = []
        self.teleporters = []
        self.init_grid()
        self.init_rooms(room_list_path)
        
        
    def init_grid(self):
        """
        Populates the initial grid of empty rooms and converts to a numpy array.
        """
        for x in range(self.grid_size):
            row = []
            for y in range (self.grid_size):
                new_room = Room.Room(x, y)
                row.append(new_room)
            self.room_grid.append(row)
        # convert to numpy 2d array
        self.room_grid = np.array(self.room_grid)


    def init_rooms(self, room_list_path):
        """
        Reads room informatiom from a csv file and updates the room grid accordingly.
        
        @param room_list_path, the relative path of the csv file.
        """
        with open(room_list_path, 'r') as csvfile:
            room_list = list(csv.reader(csvfile, delimiter=','))
            # remove header line
            room_list.pop(0)                  

            # Add first room independently, since it will
            # be positioned somewhere on the border of empty rooms.
            current_room = room_list.pop(0)  
            target_room = self.room_grid[1][0]
            target_room.update(current_room[0], current_room[1], current_room[2],
                        current_room[3], current_room[4], current_room[5])
            
            added_rooms = 1
            # loop over grid adding rooms
            # starts at (1, 1) and fills vertically then horizontally
            for x in range(1, self.grid_size - 1):
                for y in range (1, self.grid_size - 1):
                    target_room = self.room_grid[x][y]
                    # check if room list has more rooms
                    if room_list:
                        current_room = room_list.pop(0)
                        if added_rooms <= self.max_rooms:
                            # Update room's name, north, south, east, west, and item fields
                            target_room.update(current_room[0], current_room[1], current_room[2],
                                               current_room[3], current_room[4], current_room[5])
                            
                            # check if room is a teleporter, if so add to the list
                            if target_room.type == 'teleporter':
                                self.teleporters.append(target_room)

                            # DEBUG: Uncomment the following line to check room positioning
                            # print('added ' + target_room.name + ' at position (' + str(x) +', ' + str(y) + ')')
                            added_rooms += 1

        # Add locked neighbor information to each room    
        self.update_locked_rooms()


    def update_locked_rooms(self):
        """
        Determines which neighboring rooms are inaccessible/locked
        for all rooms in the map, and adds that information to 
        the room object.
        """
        for row in self.room_grid:
            for room in row:
                if room.name:
                    # Calculate inaccessible adjacent rooms
                    locked_rooms = self.get_inaccessible(room)
                    # Add those rooms the the room object's locked room list
                    room.locked_neighbors = locked_rooms


    def get_room(self, room_name):
        """
        Gets the room object matching a given name.
        
        @param room_name, the name of the room to find.
        @return room, the matching room object, None if no match.
        """
        for row in self.room_grid:
            for room in row:
                if room.name == room_name:
                    return room
        return None
    

    def room_from_coordinates(self, x_pos, y_pos):
        """
        Gets the room object matching a pair of x,y coordinates.
        
        @param x_pos, the x coordinate of the desired room.
        @param y_pos, the y coordinate of the desired room.
        @return self.room_grid[x_pos][y_pos], the matching room object
        returns None if no match.
        """
        # Check if x/y coordinates are in bounds of map
        if self.grid_size > x_pos >= 0:
            if self.grid_size > y_pos >= 0:
                # Check if room is populated (not empty)
                if self.room_grid[x_pos][y_pos].name:
                    return self.room_grid[x_pos][y_pos]
        return None
    
    
    def get_neighbors(self, room):
        """
        Gets a list of all adjacent room objects.

        @param room: the room from which to get neighbors
        @return neighbors: a list of all adjacent rooms.
        """
        neighbors = []
        x_pos = room.x_pos
        y_pos = room.y_pos

        # Determine which neighbors are in bounds for the map
        if (x_pos < (self.grid_size - 1)):
            neighbors.append(self.room_grid[x_pos + 1][y_pos])
        if (y_pos < (self.grid_size - 1)):
            neighbors.append(self.room_grid[x_pos][y_pos + 1])
        if (x_pos > 0):
            neighbors.append(self.room_grid[x_pos - 1][y_pos])
        if (y_pos > 0):
            neighbors.append(self.room_grid[x_pos][y_pos - 1])
        return neighbors
    

    def get_accessible(self, room):
        """
        Gets a list of all adjacent room objects that are accessible to the player.

        @param room: the room from which to get accessible neighbors
        @return accessible_rooms: a list of all accessible adjacent rooms.
        """
        accessible_rooms = []
        for name in room.adjacent_rooms:
            accessible_rooms.append(self.get_room(name))
        return accessible_rooms


    def get_inaccessible(self, room):
        """
        Gets a list of all adjcent room objects which are not accessible to the player.
        
        @param room: the room from which to get inaccessible neighbors
        @return inaccessible_rooms: a list of all inaccessible adjacent rooms.
        """
        inaccessible_rooms = []
        all_neighbors = self.get_neighbors(room)
        accessible_rooms = self.get_accessible(room)

        # Add adjacent room to the list of locked neighbors if it
        # is not accessible from the current room.
        for adjacent_room in all_neighbors:
            if adjacent_room not in accessible_rooms:
                inaccessible_rooms.append(adjacent_room)
        return inaccessible_rooms
    

    def next_teleporter(self, curr_room):
        """
        Randomly gets a new teleporter to travel to.

        @param curr_room, the current room location 
        (must contain) a teleporter.
        @return next_room, a random other teleporter room.
        """
        # Temporarily remove curr_room from the teleporter list
        # to ensure we don't return the same room.
        self.teleporters.remove(curr_room)
        try:
            # Get another random teleporter
            next_room = random.choice(self.teleporters)
        except IndexError:
            # If the map only contains one teleporter,
            # no additional room will be found, and curr_room is returned.
            print('No remaining teleporters, staying in current room.')
            next_room = curr_room

        # Re-add curr_room to the list of valid teleporters.
        self.teleporters.append(curr_room)
        return next_room
    

    def print_map(self):
        """
        Creates a graphical representation of the game world.
        Color coded to indicate current location, previously explored rooms, etc.
        Blue - Current Position
        Black - Unknown
        Red - Inaccessible
        Green - Accessible
        Grey - Previously explored
        """

        # Create the figure and axes
        fig, ax = plt.subplots()
        ax.set_xlim(0, self.grid_size)
        ax.set_ylim(0, self.grid_size)
        ax.set_aspect('equal')
        ax.set_xticks(range(self.grid_size))
        ax.set_yticks(range(self.grid_size))
        ax.grid(True)

        # Color legend mapping
        legend_labels = {
            "blue": "Current Position",
            "black": "Unknown",
            "red": "Inaccessible",
            "green": "Accessible",
            "grey": "Explored"
        }

        # Create a legend with colored patches
        legend_patches = []
        for color, label in legend_labels.items():
            legend_patches.append(mpatches.Patch(color=color, label=label))
        ax.legend(handles=legend_patches, loc='upper right', fontsize=8, frameon=True)

        # Draw the grid with specified colors
        for row in self.room_grid:
            for room in row:
                rect = plt.Rectangle((room.x_pos, room.y_pos), 1, 1, 
                                      edgecolor='white', facecolor=room.color
                )
                ax.add_patch(rect)
                # if the room has been discovered, label it
                if room.visited:
                    # ensure solid contrasting text color
                    if room.color == 'grey' or room.color == 'red':
                        text_color = 'black'
                    else:
                        text_color = 'yellow'

                    # Replace spaces with newlines in room.name to fit to cell
                    display_text = room.name.replace(' ', '\n')

                    ax.text(
                        room.x_pos + 0.5, room.y_pos + 0.5, display_text,
                        ha='center', va='center', fontsize=6, color=text_color
                    )

        # Hide axis labels
        ax.set_xticks([])
        ax.set_yticks([])

        ax.set_title("Spaceship Map")

        # Show the grid
        plt.show()
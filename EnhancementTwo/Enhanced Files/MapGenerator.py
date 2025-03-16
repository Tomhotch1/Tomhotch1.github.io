import Room
import numpy as np
import csv
import random

class MapGenerator:
       
    def __init__(self, room_list_path, grid_size, generation_type='static'):
        """
        Constructor for the MapGenerator class.  Creates a grid of empty rooms, then populates it.
        Uses either a pre-defined list of room locations or generates locations dynamically.

        @param room_list_path, the relative path of the csv file.
        @param grid_size, the side length of the internal square of the grid.
        @param generation_type, the process used to generate the Map.  Static by default.
        """
        # max rooms is the central square of the grid + 1 starting room
        self.max_rooms = ((grid_size - 2) ** 2) + 1   
        self.grid_size = grid_size         
        self.room_list_path = room_list_path
        # Chooses whether to create a fixed map or a procedurally generated one.
        # Default is fixed.  
        self.generation_type = generation_type
        self.room_list = []


    def generate_map(self):
        """
        Creates and returns a map as a 2d NumPy array.
        
        @return map, the populated map of room locations.
        @return teleporters, a list of all teleporters on the map.
        """
        map = []
        teleporters = []

        # Initialize grid with empty rooms
        self.init_grid(map)
        # Get room info from csv file
        self.read_rooms()

        # Check whether to use static or procedural generation
        if self.generation_type == 'static':
            self.generate_static(map, teleporters)
        else:
            self.generate_dynamic(map, teleporters)

        return map, teleporters


    def init_grid(self, map):
        """
        Populates the initial grid of empty rooms and converts to a numpy array.

        @param map, the map to populate.
        """
        for x in range(self.grid_size):
            row = []
            for y in range (self.grid_size):
                new_room = Room.Room(x, y)
                row.append(new_room)
            map.append(row)
        # convert to numpy 2d array
        map = np.array(map)


    def read_rooms(self):
        """
        Reads room information from a csv file and stores in room_list
        """
        with open(self.room_list_path, 'r') as csvfile:
            self.room_list = list(csv.reader(csvfile, delimiter=','))
            # remove header line
            self.room_list.pop(0)

        # Randomize the list to ensure different room configurations
        random.shuffle(self.room_list)

    
    def update_teleporters(self, map, teleporters):
        """
        Updates list of teleporters with matching rooms.

        @param map, the map to scan for teleporters.
        @param teleporters, the list of teleporter rooms.
        """
        for row in map:
            for room in row:
                if 'Teleporter' in room.name:
                    teleporters.append(room)


    def generate_static(self, map, teleporters):
        """
        Processes room_list and builds a grid of rooms into a map.
        
        @param map, the grid of empty rooms to populate
        @param teleporters, a list of teleporters present on the map.
        """ 
        # Add first room independently, since it will
        # be positioned somewhere on the border of empty rooms.
        current_room = self.room_list.pop(0) 
        target_room = map[1][0]
        target_room.update(current_room[0], current_room[5], current_room[1],
                    current_room[2], current_room[3], current_room[4])
        
        added_rooms = 1
        # loop over grid adding rooms
        # starts at (1, 1) and fills vertically then horizontally
        for x in range(1, self.grid_size - 1):
            for y in range (1, self.grid_size - 1):
                target_room = map[x][y]
                # check if room list has more rooms
                if self.room_list:
                    current_room = self.room_list.pop(0)
                    if added_rooms <= self.max_rooms:
                        # Update room's name, north, south, east, west, and item fields
                        target_room.update(current_room[0], current_room[5], current_room[1],
                                        current_room[2], current_room[3], current_room[4])

                        # DEBUG: Uncomment the following line to check room positioning
                        # print('added ' + target_room.name + ' at position (' + str(x) +', ' + str(y) + ')')
                        added_rooms += 1

        # Add teleporters to list
        self.update_teleporters(teleporters)


    def generate_dynamic(self, map, teleporters):
        """
        Uses the room list to procedurally create a map.

        @param map, the map to update.
        @param teleporters, a list of teleporters on the map.
        """
        # Add player and enemy starting rooms to the map.
        # Player starts in a random edge location.
        # Enemy starts in the corner of the inner square furthest from player start.
        start_room = self.add_starting_room(map)
        enemy_start = self.add_enemy_start(map, start_room)

        # Add up to 4 (including enemy start) escape pods to inner square corners.
        escape_pods = self.add_escape_pods(map, enemy_start)

        # Adds up to (grid_size * 4) - (12 + number of escape pods)
        # teleporters to the edges of the inner square of rooms.
        self.add_all_teleporters(map, escape_pods, teleporters)

        # Add remaining rooms to the map, grouped by type.
        groups = self.create_room_groups()
        generic = self.insert_grouped_rooms(map, groups)
        self.add_generic_rooms(map, generic)

        # Fill remaining empty rooms with hallways and update connected rooms.
        self.fill_hallways(map)
        self.update_connected_rooms(map)


    def create_room_groups(self):
        """
        Converts list of room info to a dictionary of room info.
        Seperates rooms into types like Engineering, Officer, Crew, etc.
        
        @return grouped_rooms, the dictionary of room information.  
        Keys are group name, value is a list of two element lists starting with name and then item.
        """
        # Initialize group definitions.
        grouped_rooms, keywords = self.define_room_groups()

        # Convert room_list info into the grouped_rooms dictionary.
        for group in grouped_rooms.keys():
            self.add_room_group(group, grouped_rooms, keywords[group])

        self.group_remaining_rooms(grouped_rooms)
        return grouped_rooms


    def define_room_groups(self):
        """
        Initializes a dictionary of room groups and associated keywords.

        @return room_groups, the dictionary of groups.
        @return keyword_dict, a dictionary of each group's keywords.
        """
        # Create group keys.
        room_groups = {
            'Engineering': [],
            'Science': [],
            'Officer': [],
            'Crew': [],
            'Weapons': [],
            'Generic': []
        }

        # Define keywords for each group.
        keyword_dict = {
            'Engineering': ['Engine'],
            'Science': ['Server', 'Lab', 'Laser'],
            'Officer': ['Officer', 'Bridge', 'Captain'],
            'Crew': ['Mess', 'Crew', 'Infirm'],
            'Weapons': ['Armor', 'Gun', 'Shield'],
            'Generic': ['Communication']
        }

        return room_groups, keyword_dict


    def add_room_group(self, group, rooms, keywords):
        """
        Adds room information for a given room group from 
        the csv file to a room groups dictionary.
        
        @param group, the key to add the room info to.
        @param rooms, the group dictionary to update.
        @param keywords, a list of keywords to match room info to.
        """
        index = -1

        # Get first matching room.
        for word in keywords:
            index = self.get_list_index(word)
            if index >= 0:
                break

        # Add rooms until no matches.
        while index >= 0:
            room_info = self.room_list.pop(index)
            rooms[group].append([room_info[0], room_info[5]])
            # Check room info until a matching room is found
            for word in keywords:
                index = self.get_list_index(word)
                if index >= 0:
                    break
                else:
                    # No room matching this keyword, remove the keyword from the list
                    keywords.remove(word)


    def group_remaining_rooms(self, rooms):
        """
        Adds remaining rooms from the room list to the
        group dictionary under 'Generic" grouping.

        @param rooms, the dictionary of room info.
        """
        for row in self.room_list:
            if row:
                rooms['Generic'].append([row[0], row[5]])


    def insert_grouped_rooms(self, map, groups):
        """
        Adds all grouped rooms to the map one group at a time.
        Randomly selects a group (not generic) and 
        an empty room, then adds rooms from that group to adjacent empty rooms.
        If no more connected rooms exist, moves remaining rooms in group to generic group.

        @param map, the map to insert the grouped rooms into.
        @param groups, a dictionary of group names and room info.
        @return generic, a list of generic room info.
        """
        # Remove generic rooms and store.
        generic = groups.pop('Generic')
        
        # Get all empty rooms
        empty_rooms = self.get_empty(map)

        while len(groups.keys()) > 0 and len(empty_rooms) > 0:
            # Select a group to insert and get room info
            group = random.choice(list(groups.keys()))
            rooms = groups[group]
            
            # Add the chosen group to the map
            remaining_rooms = self.insert_single_group(map, rooms, empty_rooms)
            print('Added {} room(s) to the map.'.format(group.lower()))
            
            # Remove the group from the dictionary
            groups.pop(group)

            # Add remaining rooms to the generic room list, if any.
            for room in remaining_rooms:
                generic.append(room)

            # Refresh empty room list
            empty_rooms = self.get_empty(map)

        return generic


    def add_generic_rooms(self, map, rooms):
        """
        Adds the remaining (generic) rooms to the map.

        @param map, the map to add rooms to.
        @param rooms, the rooms to add.
        """
        empty_rooms = self.get_empty(map)
        while len(empty_rooms) > 0 and len(rooms) > 0:
            next_room = random.choice(empty_rooms)
            room_info = rooms.pop(0)
            next_room.update(room_info[0], room_info[1])
            empty_rooms.remove(next_room)


    def fill_hallways(self, map):
        """
        Fills remaining empty rooms with hallways.
        Hallways are rooms with no items but a type of normal
        and a name of Hallway.
        
        @param map, the map to add hallways to.
        """
        hall_num = 1
        empty_rooms = self.get_empty(map)
        for room in empty_rooms:
            name = 'Hallway ' + str(hall_num)
            room.update(name, 'None')
            hall_num += 1


    def update_connected_rooms(self, map):
        """
        Updates the connected rooms for each room on the map.

        @param map, the map to update.
        """
        occupied_rooms = self.get_occupied(map)
        for room in occupied_rooms:
            north, south, east, west = 'None', 'None', 'None', 'None'
            x_pos = room.x_pos
            y_pos = room.y_pos

            # East Room
            if map[x_pos + 1][y_pos].type != 'empty':
                east = map[x_pos + 1][y_pos].name
            # North Room
            if map[x_pos][y_pos + 1].type != 'empty':
                north = map[x_pos][y_pos + 1].name
            # West Room
            if map[x_pos - 1][y_pos].type != 'empty':
                west = map[x_pos - 1][y_pos].name
            # South Room
            if map[x_pos][y_pos - 1].type != 'empty':
                south = map[x_pos][y_pos - 1].name

            # Update the room with adjacent room names
            room.add_adjacent(north, south, east, west)
    

    def get_occupied(self, map):
        """
        Gets a list of all occupied rooms on the map.
        
        @param map, the map to retrieve occupied rooms from.
        @return occupied_rooms, the list of occupied rooms.
        """
        occupied_rooms = []
        for x in range(1, self.grid_size - 1):
            for y in range(1, self.grid_size - 1):
                if map[x][y].type != 'empty':
                    occupied_rooms.append(map[x][y])
        return occupied_rooms


    def insert_single_group(self, map, rooms, empty):
        """
        Populates the map with a group of rooms

        @param map, the map to add rooms to.
        @param rooms, a list of room info in one group
        @param empty, a list of empty rooms in the map
        @return unadded_rooms, a list of rooms that 
        did not fit in the chosen spot.
        """            
        # Select a location and insert the first room
        if len(rooms) > 0 and len(empty) > 0:
            curr_room = random.choice(empty)
            room_info = rooms.pop(0)
            curr_room.update(room_info[0], room_info[1])
        # First room wasn't added, exit and try next group.
        else:
            return rooms
        
        # Get rooms adjacent to the first room
        options = self.get_adjacent_inner(map, curr_room)

        # Continue adding rooms until theres no more rooms adjacent
        # to the group or rooms in the group.
        while len(options) > 0 and len(rooms) > 0:
            # Get info and select target room
            room_info = rooms.pop(0)
            curr_room = random.choice(options)

            # Update room with info and remove from options list
            curr_room.update(room_info[0], room_info[1])
            options.remove(curr_room)

            # Add new adjacent empty rooms to the options list
            for room in self.get_adjacent_inner(map, curr_room):
                options.append(room)
        
        return rooms
            

    def add_starting_room(self, map):
        """
        Adds the starting room (Planetary Elevator) to
        the map in a random edge cell and updates the room information.

        @param map, the map to add the starting room to.
        @return start_cell, the starting room object, None if room wasn't found.
        """
        # Get info from the csv file and update the room.
        room_index = self.get_list_index('Planetary Elevator')
        start_cell = None
        room_info = None

        # Check if room was found in csv, return None if not.
        if room_index >= 0:
            room_info = self.room_list.pop(room_index)
            # Choose the outer edge cell to start in
            start_cell = self.random_start_room(map)
            start_cell.update(room_info[0], room_info[5])
            print('Added player starting location to the map.')
        return start_cell

    
    def random_start_room(self, map):
        """
        Randomly selects an edge cell to add the starting room to.

        @param map, the map to select from.
        @return edge_cell, the selected cell.  None if map has no edges.
        """
        edge_cells = []

        # Add vertical edges
        for y in range(1, self.grid_size - 1):
            edge_cells.append(map[0][y])
            edge_cells.append(map[self.grid_size - 1][y])

        # Add horizontal edges
        for x in range(1, self.grid_size - 1):
            edge_cells.append(map[x][0])
            edge_cells.append(map[x][self.grid_size - 1])

        try:
            return random.choice(edge_cells)
        except IndexError:
            print('Unable to pick starting room, map has no edge cells.')
            return None


    def add_enemy_start(self, map, start_room):
        """
        Adds the enemy's starting room (Escape Pods 2) to the map
        in the furthest corner of the central room square from
        the starting room.

        @param map, the map to add the room to.
        @param start_room, the room containing the player's starting location.
        @return enemy_room, the starting location for the enemy.
        """
        # Get corners of inner square of cells
        corners = self.get_inner_corners(map)
        
        max_dist = 0
        enemy_room = None

        # Find corner that is furthest from player start
        for corner in corners:
            dist = self.distance_between(start_room, corner)
            if dist > max_dist:
                max_dist = dist
                enemy_room = corner

        end_index = self.get_list_index('Escape Pods')

        # Check if csv file has info for at least one Escape Pods room.
        if (end_index >= 0):
            # Remove room info row from the list and update the map.
            end_room_info = self.room_list.pop(end_index)
            enemy_room.update(end_room_info[0], end_room_info[5])
            print('Added enemy starting location to the map.')

        return enemy_room
    

    def add_escape_pods(self, map, enemy_start):
        """
        Adds the remaining escape pods to the map.
        Max of 4 total escape pods.

        @param map, the map to add the escape pods to.
        @param enemy start, the room object where the Enemy is starting
        @return escape_pods, the list of updated escape pod rooms
        """
        escape_pods = []

        # Check if an enemy start was added, print an error if not.
        if not enemy_start:
            print ('No enemy starting location.')
            return escape_pods

        escape_pods.append(enemy_start)

        # Get the corners of the inner square of cells and remove
        # The cell where the enemy started.
        corners = self.get_inner_corners(map)
        corners.remove(enemy_start)

        next_index = self.get_list_index('Escape Pods')

        # add Escape Pod rooms to random corners until there
        # are no more Escape Pod rooms or corners available
        while next_index >= 0 and len(escape_pods) < 4:
            room_info = self.room_list.pop(next_index)
            next_room = random.choice(corners)
            escape_pods.append(next_room)
            next_room.update(room_info[0], room_info[5])
            corners.remove(next_room)
            next_index = self.get_list_index('Escape Pods')
        
        # Print confirmation of Escape Pod addition.
        print('Added {} total Escape Pod(s) to the map.'.format(len(escape_pods)))
        return escape_pods
    
    
    def add_all_teleporters(self, map, escape_pods, teleporters):
        """
        Positions teleporters to edge cells, spaced as far as possible.
        Maximum of (grid_size * 4) - (12 + number of escape pods)

        @param map, the map to add teleporters to.
        @param escape_pods, a list of the map's escape pods rooms.
        @param teleporters, a list of the map's teleporter rooms.
        """
        teleporters = []
        max_teleporters = (self.grid_size * 4) - 12 - len(escape_pods)

        # Check if there's room to add teleporters, print an error if not.
        if (max_teleporters < 0):
            print('No room to add teleporters')
            return teleporters
        
        # Add the first teleporter next to a random escape pod room.
        first = self.add_first_teleporter(map, escape_pods)
        if (first):
            teleporters.append(first)
            self.add_more_teleporters(map, teleporters, max_teleporters)
        print('Added {} teleporters to the map.'.format(len(teleporters)))
        return teleporters

    
    def add_first_teleporter(self, map, escape_pods):
        """
        Adds a single teleporter adjacent to a random escape pods room.

        @param map, the map to add the teleporter to.
        @param escape_pods, a list of escape pods rooms.
        @return next_room, the room the teleporter was added to; 
        None if invalid.
        """
        # If there's no escape pods, print an error and return None.
        if len(escape_pods) < 1:
            print('No escape pods present; no teleporter added.')
            return None
        
        # Get a random escape pod room and teleporter room info.
        pod = random.choice(escape_pods)
        next_index = self.get_list_index('Teleporter')
        next_room = None

        # If there was an teleporter remaining in the csv file,
        # add it to the in a random adjacent cell for a random
        # escape pods room.
        if next_index >= 0:
            room_info = self.room_list.pop(next_index)
            next_room = random.choice(self.get_adjacent_inner(map, pod))
            next_room.update(room_info[0], room_info[5])

        return next_room
    

    def add_more_teleporters(self, map, teleporters, max_teleporters):
        """
        Continues adding teleporters until no valid spaces remain or
        the csv file runs out of teleporter rooms to add.

        @param map, the map to add teleporters to.
        @param teleporters, a list of all teleporters on the map
        @param max_teleporters, the limit of how many teleporters can be added.
        """
        # Get room info and list of empty inner square edge rooms
        next_index = self.get_list_index('Teleporter')
        options = self.get_empty_edges(map)
        
        # Add teleporters until there are no more in the csv file
        # or the maximum has been reached.
        while next_index >= 0 and len(teleporters) < max_teleporters:
            room_info = self.room_list.pop(next_index)
            next_room = None
            max_dist = 0

            # Find the room with the largest total distance to other teleporters
            for room in options:
                total_distance = self.sum_distance(room, teleporters)
                if total_distance > max_dist:
                    max_dist = total_distance
                    next_room = room

            # If there's another teleporter to add, add it and remove from csv file.
            if next_room:
                next_room.update(room_info[0], room_info[5])
                teleporters.append(next_room)
                options.remove(next_room)
                next_index = self.get_list_index('Teleporter')

    
    def get_empty(self, map):
        """
        Gets a list of all empty remaining rooms on the map.
        
        @param map, the map to retrieve empty rooms from.
        @return empty_rooms, the list of empty rooms.
        """
        empty_rooms = []
        for x in range(1, self.grid_size - 1):
            for y in range(1, self.grid_size - 1):
                if map[x][y].type == 'empty':
                    empty_rooms.append(map[x][y])
        return empty_rooms

    
    def sum_distance(self, room, other_rooms):
        """
        Calculates the total distance between a room and a list of other rooms.
        
        @param room, the room to compare to the others.
        @param other_rooms, the list of other rooms to measure.
        @return distance, the total distance between rooms.
        """
        distance = 0
        for other_room in other_rooms:
            distance += self.distance_between(room, other_room)
        return distance


    def get_list_index(self, name):
        """
        Gets the index of the first row in room_list with a given name.

        @param name, the name of the room to match
        @return index, the index of the matching row. -1 if not found.
        """
        index = next((i for i, row in enumerate(self.room_list) if name in row[0]), -1)
        return index
    
    
    def get_adjacent_inner(self, map, room):
        """
        Gets a list of all adjacent and unoccupied inner square rooms.

        @param room, the room from which to get adjacent rooms.
        @return adjacent_inner, a list the rooms that are adjacent.
        """
        neighbors = []
        x_pos = room.x_pos
        y_pos = room.y_pos

        # Determine which unoccupied neighbors are in bounds of the central square
        # East Room
        if ((x_pos < (self.grid_size - 2)) and (map[x_pos + 1][y_pos].type == 'empty')):
            neighbors.append(map[x_pos + 1][y_pos])
        # North Room
        if ((y_pos < (self.grid_size - 2)) and (map[x_pos][y_pos + 1].type == 'empty')):
            neighbors.append(map[x_pos][y_pos + 1])
        # West Room
        if ((x_pos > 1) and (map[x_pos - 1][y_pos].type == 'empty')):
            neighbors.append(map[x_pos - 1][y_pos])
        # South Room
        if ((y_pos > 1) and (map[x_pos][y_pos - 1].type == 'empty')):
            neighbors.append(map[x_pos][y_pos - 1])
        return neighbors


    def get_inner_corners(self, map):
        """
        Gets a list of rooms in the corners of the inner square of the map.

        @param map, the map to get corners from.
        @return corners, the list of corner cells.
        """
        corners = []
        corners.append(map[1][1])
        corners.append(map[1][self.grid_size - 2])
        corners.append(map[self.grid_size - 2][1])
        corners.append(map[self.grid_size - 2][self.grid_size - 2])
        return corners
    

    def get_empty_edges(self, map):
        """
        Gets a list of all empty rooms on the edge of the inner square of cells.
        
        @param map, the map to get edge rooms from.
        @return edges, the list of empty edge rooms.
        """
        edges = []
        # Add rooms on the bottom and top edge if empty.
        for x in range(1, self.grid_size - 1):
            if map[x][1].type == 'empty':
                edges.append(map[x][1])
            if map[x][self.grid_size - 2].type == 'empty':
                edges.append(map[x][self.grid_size - 2])

        # Add non-corner rooms on the left and right edge if empty.
        for y in range(2, self.grid_size - 2):
            if map[1][y].type == 'empty':
                edges.append(map[1][y])
            if map[self.grid_size - 2][y].type == 'empty':
                edges.append(map[self.grid_size - 2][y])

        return edges
    

    def distance_between(self, room_a, room_b):
        """
        Calculates the number of moves required to travel from one room to another
        using the shortest path.

        @param room_a, the starting room
        @param room_b, the destination room
        @return distance, the number of moves required to move between the rooms.
        """
        a_x_pos = room_a.x_pos
        a_y_pos = room_a.y_pos
        b_x_pos = room_b.x_pos
        b_y_pos = room_b.y_pos
        distance = abs(a_x_pos - b_x_pos) + abs(a_y_pos - b_y_pos)
        return distance

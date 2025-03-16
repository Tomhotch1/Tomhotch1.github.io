from Character import Character
import random

class Enemy(Character):

    def __init__(self, map, name, location):
        """
        Constructor for the Enemy class.
        Initializes location, name and ties the Enemy to a Map.
        
        @param map, the Map object on which the Enemy will exist.
        @param name, the enemy's name.
        @param location, the initial location for the enemy.
        """
        super().__init__(map, name, location)


    def move(self):
        """
        Randomly selects an adjacent room to move to.
        Cannot use teleporters, but ignores locked rooms.
        """
        # Get non-empty neighboring rooms
        neighbors = self.map.get_non_empty(self.location)

        try:
            # Select a neighboring room at random and move there.
            next_room = random.choice(neighbors)
            self.moveTo(next_room.name)

        # If there were no valid rooms to move to, print an error.
        except IndexError:
            print('Enemy move failed: no adjacent rooms.')

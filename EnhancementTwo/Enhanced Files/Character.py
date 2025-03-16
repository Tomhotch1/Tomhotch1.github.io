import Room

class Character:
    
    def __init__(self, map, name='', location=''):
        """
        Constructor for the Character class.  
        Initializes location, name and ties the Character to a Map.
        
        @param map, the Map object on which the Character will exist.
        @param name, the character's name.
        @param location, the initial location for the character
        """
        self.map = map
        self.name = name
        self.location = None
        self.moveTo(location)
    

    def moveTo(self, new_room_name):
        """
        Updates the character's location to a new location.
        Will update to None if new_room_name is invalid or not found.

        @param new_room_name, the name of the room to move to.
        """
        self.location = self.map.get_room(new_room_name)
            
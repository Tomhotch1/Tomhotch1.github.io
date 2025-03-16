### Enhancement Two: Algorithms and Data Structures
This artifact was originally created as a part of the first core Computer Science course I took at SNHU, Introduction to Scripting.  It was the final project, which required the creation of a text-based game.  For enhancement one, I worked to substantially improve the structure of the project by breaking it up into multiple classes using the principles of object-oriented programming.  I also bolstered documentation, normalized the style, and worked to ensure functions were limited to fulfilling a single purpose.  Lastly, I added some functionality in the form of a map printing feature, that illustrated the player’s location and some status information.  To continue to extend this project further, I added two additional features for the data structures and algorithms enhancement.  These are movements for the enemy character, and a procedurally generated map.   

The enemy movement is simple, choosing a random adjacent room to move to each time the player moves after three turns.  This could continue to be refined, perhaps adding multiple difficulty settings.  The enemy could move towards the player or randomly, with the chance for each being modifiable to adjust difficulty.  To take this even further, the enemy player could even use machine learning to predict likely player movements.  Most of my time for this enhancement was spent working on implementing the MapGenerator class.  I first worked on the high-level algorithm, and decided to do the following: 

    Read information from CSV file and import it to a list. 

    Shuffle the list to add additional variety. 

    Create an empty square 2d array to represent the map. 

    Update a random edge cell (that isn’t a corner) with the name and item information for the starting room.  Remove this entry from the information list. 

    Update the inner square corner cell that is furthest away from the starting room with the enemy’s starting room (an Escape Pods room) information, remove that entry from the list. 

    Add up to three more Escape Pods in other random inner square corners and remove those entries from the list. 

    Add the first teleporter room to the map adjacent to a random Escape Pods room, if any, and remove their information from the list. 

    Add remaining teleporters one at a time.  Place them in the cell with the highest net distance from all other teleporters. 

    Convert the remaining room information into a dictionary of room types, using a set of keywords in the names. 

    Add any remaining room information to a “Generic” room type group. 

    Select a non-generic group and add the first room to a random empty inner square cell. 

    One at a time, add the remaining rooms for the group in an empty cell adjacent to the group's existing rooms. 

    If there are no remaining adjacent empty cells, shift the remaining rooms in the group to the generic group. 

    Repeat steps 11 through 13 for remaining non-generic group types. 

    One at a time, add rooms in the generic group to a random empty inner square cell until either the rooms are exhausted, or there are no more available empty cells. 

    Fill all remaining empty inner square cells with hallways.  These are rooms that are navigable but contain no items. 

    Lastly, for each room, update the room’s adjacent rooms list by finding its neighbors. 

The key part of this algorithm is that while it contains several decision points that are decided randomly, there are no cases were placing a room in one location will invalidate the placement of prior rooms or cause the map generator to enter a state where it is unable to place a future room.  This limits the run time and memory usage of the program by avoiding processing unnecessary instructions.   

In terms of time complexity, the function that has the lowest efficiency is the addition of teleporters.  This is because for each teleporter, it must calculate the distance to each other previously placed teleporter, meaning it technically has a n-factorial time-complexity.  This is reasonable for small map sizes, especially because the number of teleporters is a small subset of all rooms.  However, if the game was being played on a large map and similarly large number of teleporters, a different placement algorithm should be used to improve efficiency.  In addition to this challenge, I ran into some issues deciding how to best structure the MapGenerator class.  While I did work to limit function bloat by sticking to the single-purpose principle, the file grew quickly.  If more complexity was added to the procedural generation logic, I would split the class into further subclasses to maintain ease of future code development.  

[Portfolio Home](../README.md)
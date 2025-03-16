import Player
import Enemy
import Map

class Game:
    
    def __init__(self, room_list_path, grid_size, num_items):
        """
        Constructor for the Game class. Uses room list path, grid size, and 
        number of items required to win provided by the driver.

        @param room_list_path, the relative path of the room list csv file.
        @param grid_size, size of central square of rooms
        @param num_items, the number of items required to win the game
        when encountering the enemy.
        """
        self.room_list_path = room_list_path
        # Ensure final grid is at least 5x5
        if (grid_size < 3):
            self.grid_size = 3
        else:
            self.grid_size = grid_size
        self.player = None
        self.enemy = None
        self.map = []
        self.num_items = num_items
        self.round = 0


    def init_characters(self):
        """
        Initializes the player and enemy with their starting locations.
        """
        self.player = Player.Player(self.map, 'Tom', 'Planetary Elevator')      # player starting position is Planetary Elevator
        self.enemy = Enemy.Enemy(self.map, 'Pap-AI', 'Escape Pods 2')           # robot starting position is Escape Pods 2
        

    def play_game(self):
        """
        Initializes the map and characters, shows game introduction,
        and executes the core gameplay loop.
        """
        self.map = Map.Map(self.room_list_path, self.grid_size)
        self.init_characters()
        self.show_instructions()
        gameover = False
        while not gameover:
            command, direction = self.get_command()
            gameover = self.process_command(command, direction)

    
    def show_instructions(self):
        """
        Displays initial scenario and explains game rules
        """
        print('**********************************************************************************************\n'
              '*                           Welcome to the Spaceship Escape Game!                            *\n'
              '* Your goal is to collect of the items before encountering the rogue AI known as PAP-AI      *\n'
              '* PAP-AI starts in the Laboratory, so be sure to avoid that until you\'re ready!              *\n'
              '* Good luck and have fun!                                                                    *\n'
              '**********************************************************************************************\n')
        

    def show_status(self):
        """
        Prints out the player's location, accessible adjacent rooms,
        and items in inventory. 
        """
        print('You are in: ' + str(self.player.location))
        print()
        print('Inventory: {}'.format(self.player.inventory))
        print()
        

    def get_move_direction(self):
        """
        Prompts the user to select a direction to move.
        
        @return direction, the direction to move.
        """
        # Show the player the valid direction options
        self.print_move_options()

        # Get player's input
        try:
            direction = int(input())
        # If an invalid input was entered, print an error and try again.
        except ValueError:
            print('Please enter a valid number.')
            return self.get_move_direction()
        except Exception as e:
            print('An error occured:', e)
            return self.get_move_direction()
        
        print()

        # Convert input to a direction
        return self.interpret_direction(direction)
    

    def interpret_direction(self, direction):
        """
        Converts a the player's integer input to a direction command.

        @param direction, the user input integer.
        @return direction, a string (north, south, etc.) direction.
        """
        if direction == 1:
            return 'north'
        elif direction == 2:
            return 'south'
        elif direction == 3:
            return 'east'
        elif direction == 4:
            return 'west'
        # Check if teleporter is a valid option
        elif self.player.location.type == 'teleporter' and direction == 5:
            return 'teleport'
        # If an invalid number was entered, print error and try again.
        else:
            print("Invalid direction selected, please try again.")
            return self.get_move_direction()
        
    
    def print_move_options(self):
        """
        Displays possible movement directions to the player.
        """
        print('Which direction would you like to move? (type a number): ')
        print('1) North')
        print('2) South')
        print('3) East')
        print('4) West')
        if self.player.location.type == 'teleporter':
            print('5) Enter Teleporter')
        
    
    def get_command(self):
        """
        Displays possible commands to the player, gets user input, then 
        returns the selected command and direction (if applicable)

        @return command, the user entered command
        @return direction, the direction the user wants to move,
        None if a command other than move was selected.
        """
        self.print_command_options()

        # Get user command input
        try:
            command = int(input())
        # Print error and re-try if an invalid input was entered.
        except ValueError:
            print('Please enter a valid number 1-5.')
            return self.get_command()
        except Exception as e:
            print('An error occured:', e)
            return self.get_command()
        
        print()

        # Convert user input to a command string and get direction (if applicable)
        command, direction = self.interpret_command(command)
        return command, direction
    

    def interpret_command(self, command):
        """
        Converts user's integer input to a string command.  Also gets movement
        direction if the movement command was selected.

        @param command, the user's integer input.
        @return command, the string representing the action to take.
        @return direction, the direction to move.  None if move command wasn't selected.
        """
        direction = None
        if command == 1:
            command = 'move'
            # Since move was selected, get a direction to move in.
            direction = self.get_move_direction()
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
        return command, direction
    
    
    def print_command_options(self):
        """
        Displays command options to the player.
        """
        print('Please choose one of the following actions (type a number): ')
        print('1) Move')
        print('2) Pickup Item')
        print('3) Print Map')
        print('4) Show Status')
        print('5) Quit')
    

    def process_command(self, command, direction):
        """
        Takes the command string and direction and executes the relevant functions.

        @param command, a string indicating the action to take.
        @param direction, a string indicating which direction to move.
        @return gameover, the game's status, True if game is over and False otherwise.
        """
        gameover = False
        if command == 'move':
            # Attempt to move in the given direction
            if self.player.attempt_move(direction):
                self.round += 1
                print("Moved to {}.".format(self.player.location.name))
                # Enemy does nothing for the first three turns, to avoid early encounters
                if self.round > 3:
                    self.enemy.move()
                    print("Enemy moved to {}.\n".format(self.enemy.location.name))
                else:
                    print()
                # Check if player has encountered enemy, and determine if they've won or lost.
                if self.player.location == self.enemy.location:
                    # If the player has the requisite number of unique items, they've won.
                    if len(self.player.inventory) < self.num_items:
                        self.print_gameover(False)
                    else:
                        self.print_gameover(True)
                    gameover = True
        elif command == 'item':
            self.player.pickup_item()
        elif command == 'map':
            self.map.print_map()
        elif command == 'status':
            self.show_status()
        elif command == 'quit':
            gameover = True
        # Print an error if an invalid command was entered.
        elif command == 'invalid':
            print('You have entered an invalid command.  Please try again.\n')

        return gameover
        

    def print_gameover(self, win):
        """
        Displays a message indicating the game has ended.
        
        @param win, True if the player has won the game, false otherwise.
        """
        if win:
            print('You\'ve encounter Pap-AI with a robust inventory full of equipment.\n'
                  'Thinking quickly, you use your tools to shut down the robot.\n'
                  'The ship and Earth are saved.\n'
                  'Congratualations, you\'ve won the Spaceship Escape game!!!')
        else:
            print('Oh no! You\'ve encounter Pap-AI without the sufficient tools to shut him down.\n'
                  'He zaps you with his taser and locks you up in the Laboratory.\n'
                  'Your chance to shut him down is gone forever, and the ship is doomed.\n'
                  'Game Over!')

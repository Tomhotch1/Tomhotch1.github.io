 # By Tom Hotchkiss
import Game

# Path for static room list
ROOM_LIST_PATH = './Room List.csv'

# Ship will be a square of this side size, plus a 1 tile border.
# Player starting room will be in one of the border tiles.
SHIP_SIZE = 5

# Number of unique items required to defeat the enemy.
# Player will lose the game if the enemy is encountered with less than
# this number of items in their inventory.
NUM_REQUIRED_ITEMS = 10


if __name__ == "__main__":
    game = Game.Game(ROOM_LIST_PATH, SHIP_SIZE, NUM_REQUIRED_ITEMS)
    # calls the core gameplay loop
    game.play_game()

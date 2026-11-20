# Vivek Shah - CS 670 - Project 2 Part 1

# board_layout.py - The mansion map as data.

# BOARD_MAP is a 25 x 24 grid (the size of the classic board). Each character is one square:
#    .                  hallway square (walkable)
#    #                  off the board / solid wall
#    K B C D I L O H S  inside a room (see ROOM_CODES)
#    lowercase letter   a door into that room
#    X                  the center of the board

# Room squares act as walls from the hallway, so rooms can only be entered through a door.
# START_POSITIONS puts each character on a hallway square at the edge of the board.
# SECRET_PASSAGES links Kitchen <-> Study and Conservatory <-> Lounge.
# DIRECTIONS maps UP/DOWN/LEFT/RIGHT to (row change, column change); there are no diagonals.


# 25 rows x 24 columns. Row 0 is the top of the board; column 0 is the left edge.
BOARD_MAP = [
    "#########.####.#########",  # 0   White (col 9) and Green (col 14) start here
    "KKKKKK....BBBB....CCCCCC",  # 1
    "KKKKKK..BBBBBBBB..CCCCCC",  # 2
    "KKKKKK..BBBBBBBB..CCCCCC",  # 3
    "KKKKKK..BBBBBBBB..CCCCCC",  # 4
    "KKKKKK..bBBBBBBb..CcCCCC",  # 5   Ballroom side doors, Conservatory door
    "KKKKkK..BBBBBBBB........",  # 6   Kitchen door; Peacock starts at col 23
    "#.......BbBBBBbB.......#",  # 7   Ballroom bottom doors
    "#.................IIIIII",  # 8
    "DDDDDDDD..........iIIIII",  # 9   Billiard Room door (left side)
    "DDDDDDDD..XXXXX...IIIIII",  # 10  X = center / envelope (impassable)
    "DDDDDDDD..XXXXX...IIIIII",  # 11
    "DDDDDDDd..XXXXX...IIIIiI",  # 12  Dining Room door (right), Billiard door (bottom)
    "DDDDDDDD..XXXXX.........",  # 13
    "DDDDDDDD..XXXXX..LLLlLLL",  # 14  Library door (top)
    "DDDDDDdD..XXXXX..LLLLLLL",  # 15  Dining Room door (bottom)
    "#.........XXXXX..lLLLLLL",  # 16  Library door (left)
    ".................LLLLLLL",  # 17  Mustard starts at col 0
    "#........HHhhHH..LLLLLLL",  # 18  Hall doors (top)
    "OOOOOoO..HHHHHH.........",  # 19  Lounge door; Plum starts at col 23
    "OOOOOOO..HHHHHh........#",  # 20  Hall door (right)
    "OOOOOOO..HHHHHH..SsSSSSS",  # 21  Study door
    "OOOOOOO..HHHHHH..SSSSSSS",  # 22
    "OOOOOOO..HHHHHH..SSSSSSS",  # 23
    "OOOOOOO.#HHHHHH##SSSSSSS",  # 24  Scarlett starts at col 7
]

# Which room each capital letter stands for (lowercase = a door of that room).
ROOM_CODES = {
    "K": "Kitchen",
    "B": "Ballroom",
    "C": "Conservatory",
    "D": "Dining Room",
    "I": "Billiard Room",
    "L": "Library",
    "O": "Lounge",
    "H": "Hall",
    "S": "Study",
}

# Starting squares (row, col): hallway squares at the edge of the board, as in the classic game.
START_POSITIONS = {
    "Miss Scarlett": (24, 7),     # bottom edge, between Lounge and Hall
    "Colonel Mustard": (17, 0),   # left edge, below the Dining Room
    "Mrs. White": (0, 9),         # top edge, left of the Ballroom
    "Reverend Green":  (0, 14),   # top edge, right of the Ballroom
    "Mrs. Peacock": (6, 23),      # right edge, below the Conservatory
    "Professor Plum": (19, 23),   # right edge, between Library and Study
}

# Secret passages link opposite corners and work in both directions.
SECRET_PASSAGES = {
    "Kitchen": "Study",
    "Study": "Kitchen",
    "Conservatory": "Lounge",
    "Lounge": "Conservatory",
}

# Direction words -> (row change, column change). Only orthogonal moves exist.
DIRECTIONS = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1),
}

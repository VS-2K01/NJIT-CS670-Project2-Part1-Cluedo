# Vivek Shah - CS 670 - Project 2 Part 1

# cards.py - The 21 Cluedo cards: 6 characters, 6 weapons, 9 rooms.

# The CHARACTERS order is also the turn order (Miss Scarlett goes first).
# CATEGORY_OF maps a card to "character", "weapon" or "room".
# TOKEN_SYMBOL gives each character a number (1-6) used to draw them on the map.


# The six standard suspects. This order is also the turn order.
CHARACTERS = ["Miss Scarlett", "Colonel Mustard", "Mrs. White", "Reverend Green", "Mrs. Peacock", "Professor Plum"]

# The six standard weapons.
WEAPONS = ["Candlestick", "Dagger", "Lead Pipe", "Revolver", "Rope", "Wrench"]

# The nine rooms of the mansion.
ROOMS = ["Kitchen", "Ballroom", "Conservatory", "Dining Room", "Billiard Room", "Library", "Lounge", "Hall", "Study"]

# Every card in the game (6 + 6 + 9 = 21).
ALL_CARDS = CHARACTERS + WEAPONS + ROOMS

# Map each card name to its category so we can ask "what kind of card is this?"
CATEGORY_OF = {}
for name in CHARACTERS:
    CATEGORY_OF[name] = "character"
for name in WEAPONS:
    CATEGORY_OF[name] = "weapon"
for name in ROOMS:
    CATEGORY_OF[name] = "room"

# Single-character symbols used to draw character tokens on the map (1 = Scarlett ... 6 = Plum).
TOKEN_SYMBOL = {name: str(number) for number, name in enumerate(CHARACTERS, start=1)}

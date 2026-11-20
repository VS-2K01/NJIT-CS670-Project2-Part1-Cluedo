# Vivek Shah - CS 670 - Project 2 Part 1

# input_utils.py - Input helpers and move validation.

# GameQuit: raised when a player types QUIT (or input closes) so the game stops cleanly
# read_line: input() wrapper that strips whitespace and handles QUIT / closed input
# parse_move_command: "UP 2, RIGHT 3" or "u2 r3" -> [("UP", 2), ("RIGHT", 3)], or None
# match_option: accepts a list number, the full name, or a unique part of a name
# path_to_steps / format_steps: turn a list of squares into readable commands
# validate_move: checks a move square by square WITHOUT changing the game. It rejects moves that exceed the roll, leave the board, hit a wall, land on another token, re-enter the room just left, or stop short of the roll without entering a room. Stepping onto a door enters the room and ends movement immediately.

import re
from dataclasses import dataclass
from typing import Optional

from board_layout import DIRECTIONS


class GameQuit(Exception):
    # Raised when the user types QUIT (or input is closed) so the game can stop cleanly.
    pass


HELP_TEXT = """
---------------------------------- HELP ----------------------------------
Commands you can type at ANY prompt:
  BOARD  - show the mansion map        NOTES - show your detective notes
  HAND   - list your cards             HELP  - show this help
  QUIT   - stop the game
Moving through hallways:
  Use UP, DOWN, LEFT, RIGHT (or U, D, L, R) followed by a number of squares,
  e.g.  UP 2, RIGHT 3   or   U2 R3
  You must use your whole roll unless you step onto a room's door - entering
  a room ends your move. Type PASS to stay where you are.
In a room at the start of your turn:
  ROLL                       - roll the die and leave through a door
  SECRET_PASSAGE_TO_<ROOM>   - use a secret passage (no roll needed)
  STAY                       - (only if another player moved you here) suggest again
  PASS                       - stay where you are
Map key: . hallway   lowercase letter = door   X = center   1-6 = players
---------------------------------------------------------------------------
"""


def read_line(prompt):
    # input() wrapper: strips whitespace and converts QUIT / closed input into GameQuit.
    try:
        text = input(prompt)
    except (EOFError, KeyboardInterrupt):
        raise GameQuit()
    if text.strip().upper() == "QUIT":
        raise GameQuit()
    return text.strip()


# Accepted spellings for each direction.
DIRECTION_ALIASES = {"UP": "UP", "U": "UP", "DOWN": "DOWN", "D": "DOWN", "LEFT": "LEFT", "L": "LEFT", "RIGHT": "RIGHT", "R": "RIGHT"}


def parse_move_command(text):
    # Turn 'UP 2, RIGHT 3' (or 'u2 r3', 'up 2 right 3') into [('UP', 2), ('RIGHT', 3)].
    # A direction with no number means 1 square. Returns None if the text isn't understood.

    # Split into words and numbers
    tokens = re.findall(r"[A-Za-z]+|\d+", text)
    steps = []
    i = 0
    while i < len(tokens):
        word = tokens[i].upper()
        if word not in DIRECTION_ALIASES:
            # Unknown word -> not a valid move
            return None
        count = 1
        if i + 1 < len(tokens) and tokens[i + 1].isdigit():
            count = int(tokens[i + 1])
            i += 1
        if count < 1:
            return None
        steps.append((DIRECTION_ALIASES[word], count))
        i += 1
    return steps or None


def format_steps(steps):
    # [('UP', 2), ('LEFT', 1)] -> 'UP 2, LEFT 1'
    return ", ".join(f"{direction} {count}" for direction, count in steps)


def path_to_steps(start, path):
    # Convert a list of squares (as returned by Board.shortest_path) into direction steps.
    steps = []
    previous = start
    for square in path:
        delta = (square[0] - previous[0], square[1] - previous[1])
        direction = next(name for name, d in DIRECTIONS.items() if d == delta)
        if steps and steps[-1][0] == direction:
            # Merge repeated directions
            steps[-1] = (direction, steps[-1][1] + 1)
        else:
            steps.append((direction, 1))
        previous = square
    return steps


def match_option(text, options):
    # Resolve what the user typed to one item of `options`.
    # Accepts a 1-based number, the exact name, or a unique part of a name (case-insensitive).
    # Returns None if nothing (or more than one thing) matches.
    
    t = text.strip().lower()
    if not t:
        return None
    if t.isdigit():
        index = int(t) - 1
        return options[index] if 0 <= index < len(options) else None
    exact = [o for o in options if o.lower() == t]
    if exact:
        return exact[0]
    partial = [o for o in options if t in o.lower()]
    return partial[0] if len(partial) == 1 else None


def numbered(options):
    # ['A', 'B'] -> '1) A   2) B'
    return "   ".join(f"{i}) {option}" for i, option in enumerate(options, start=1))


@dataclass
class MoveResult:
    # Outcome of validate_move().
    ok: bool                         # Was the move legal?
    message: str = ""                # Explanation (why it failed, or what happened)
    end: Optional[tuple] = None      # Final hallway square (if the move ended in a hallway)
    room: Optional[str] = None       # Room entered (if the move ended in a room)
    steps_used: int = 0              # Squares actually moved


def validate_move(board, start, steps, max_steps, occupied, exact=True, banned_room=None):
    # Check a proposed move square-by-square WITHOUT changing the game.

    # board - the Board
    # start - (row, col) hallway square the token starts from
    # steps - list of (direction, count), e.g. [('UP', 2), ('RIGHT', 1)]
    # max_steps - the dice roll (or what's left of it)
    # occupied - squares holding OTHER tokens (players can't share hallway squares)
    # exact - if True, the whole roll must be used unless a room is entered
    # banned_room - a room the player may not re-enter (the one they just left)

    total = sum(count for _, count in steps)
    if total > max_steps:
        return MoveResult(False, f"That move is {total} steps but you only have {max_steps}.")

    r, c = start
    used = 0
    for direction, count in steps:
        dr, dc = DIRECTIONS[direction]
        for _ in range(count):
            nxt = (r + dr, c + dc)
            where = f"row {nxt[0]}, col {nxt[1]}"
            if not board.in_bounds(nxt):
                return MoveResult(False, f"Step {used + 1} ({direction}) would leave the board.")
            if board.is_door(nxt):
                room = board.door_room[nxt]
                if room == banned_room:
                    return MoveResult(False, f"You can't re-enter the {room} on the same turn you left it.")
                used += 1
                # Entering a room ends movement immediately, even with steps left over.
                return MoveResult(True, f"entered the {room}", room=room, steps_used=used)
            if not board.is_hallway(nxt):
                room = board.room_at(nxt)
                if room:
                    reason = f"runs into the wall of the {room} (rooms can only be entered through a door)"
                else:
                    reason = "hits a wall"
                return MoveResult(False, f"Step {used + 1} ({direction}) {reason} at {where}.")
            if nxt in occupied:
                return MoveResult(False, f"Step {used + 1} ({direction}) is blocked by another token at {where}.")
            r, c = nxt
            used += 1

    if exact and used != max_steps:
        return MoveResult(False, f"You must use all {max_steps} steps unless you enter a room (that move uses {used}). Type PASS to stay put.")
    return MoveResult(True, "moved", end=(r, c), steps_used=used)

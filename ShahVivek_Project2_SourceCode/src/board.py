# Vivek Shah - CS 670 - Project 2 Part 1

# board.py - The Board class: turns the text map into an object the game can query.

# Square Queries: is_hallway, is_door, room_at, neighbors
# Room Info: doors_of (each door with its outside hallway square), secret_passage_from
# shortest_path: breadth-first search to the nearest door of a goal room. Doors are end points only, so routes never cut through a room; squares holding tokens are blocked. Used for the route hints shown before each move and for map validation.
# render: draws the map with row/column numbers and tokens
# _validate: checks the map when the board is built (every door touches exactly one hallway square, every room has a door, start squares are hallways, every room is reachable)
# Run `python board.py` to print the board.

from collections import deque

from board_layout import BOARD_MAP, ROOM_CODES, START_POSITIONS, SECRET_PASSAGES, DIRECTIONS
from cards import CHARACTERS, ROOMS, TOKEN_SYMBOL


class Board:
    # Grid-based model of the mansion: rooms, doors, hallways and secret passages.

    def __init__(self, layout, room_codes, start_positions, secret_passages):
        # grid[row][col] -> map symbol
        self.grid = [list(row) for row in layout]
        self.rows = len(self.grid)
        self.cols = len(self.grid[0])
        self.room_codes = room_codes
        self.start_positions = start_positions
        self.secret_passages = secret_passages

        # Every row must be the same width, otherwise coordinates would be meaningless.
        for r, row in enumerate(self.grid):
            if len(row) != self.cols:
                raise ValueError(f"Row {r} has {len(row)} columns; expected {self.cols}.")

        # door_room:  door square -> room name
        # room_doors: room name -> list of (door square, outside hallway square)
        self.door_room = {}
        self.room_doors = {room: [] for room in room_codes.values()}

        # Find every door (lowercase letter) on the map.
        for r in range(self.rows):
            for c in range(self.cols):
                symbol = self.grid[r][c]
                if symbol.islower():
                    self.door_room[(r, c)] = room_codes[symbol.upper()]

        # Pair each door with the single hallway square outside it.
        for door, room in self.door_room.items():
            outside = [sq for sq in self.neighbors(door) if self.is_hallway(sq)]
            if len(outside) != 1:
                raise ValueError(f"Door at {door} ({room}) must touch exactly one hallway square, found {len(outside)}.")
            self.room_doors[room].append((door, outside[0]))

        self._validate()

    # Basic Square Queries
    def in_bounds(self, pos):
        # True if (row, col) lies on the grid.
        r, c = pos
        return 0 <= r < self.rows and 0 <= c < self.cols

    def symbol(self, pos):
        # The raw map character at a square.
        return self.grid[pos[0]][pos[1]]

    def is_hallway(self, pos):
        # Hallway squares are the only squares a token can walk across.
        return self.in_bounds(pos) and self.symbol(pos) == "."

    def is_door(self, pos):
        return pos in self.door_room

    def room_at(self, pos):
        # Name of the room a square belongs to (interior or door), else None.
        if not self.in_bounds(pos):
            return None
        return self.room_codes.get(self.symbol(pos).upper())

    def neighbors(self, pos):
        # The up-to-four orthogonally adjacent squares that are on the board.
        r, c = pos
        result = []
        for dr, dc in DIRECTIONS.values():
            nxt = (r + dr, c + dc)
            if self.in_bounds(nxt):
                result.append(nxt)
        return result

    # Room Helpers
    def doors_of(self, room):
        # List of (door square, outside square) pairs for a room.
        return self.room_doors[room]

    def secret_passage_from(self, room):
        # Destination room of this room's secret passage, or None.
        return self.secret_passages.get(room)

    # Route Finding
    def shortest_path(self, start, goal_rooms, blocked=frozenset()):
        # Breadth-first search from a hallway square to the nearest door of any room in goal_rooms.
        # Returns the list of squares to step on (start excluded, the door included), or None if no route exists. 'blocked' holds squares occupied by other tokens.
        queue = deque([start])
        # Remembers how we reached each square
        came_from = {start: None}
        while queue:
            current = queue.popleft()
            if current != start and self.is_door(current):
                # The first door we pop is the closest one -> rebuild the path backwards.
                path = []
                while current != start:
                    path.append(current)
                    current = came_from[current]
                return list(reversed(path))
            for nxt in self.neighbors(current):
                if nxt in came_from:
                    continue
                if self.is_door(nxt):
                    # Doors are destinations only (never walk *through* a room).
                    if self.door_room[nxt] in goal_rooms:
                        came_from[nxt] = current
                        queue.append(nxt)
                elif self.is_hallway(nxt) and nxt not in blocked:
                    came_from[nxt] = current
                    queue.append(nxt)
        return None

    # Validation
    def _validate(self):
        # Sanity-check the map so layout mistakes are caught immediately.
        for name, pos in self.start_positions.items():
            if not self.is_hallway(pos):
                raise ValueError(f"Start square for {name} at {pos} is not a hallway square.")
        for room, doors in self.room_doors.items():
            if not doors:
                raise ValueError(f"The {room} has no doors.")
        for room, other in self.secret_passages.items():
            if self.secret_passages.get(other) != room:
                raise ValueError(f"Secret passage {room} -> {other} must work both ways.")
        for name, pos in self.start_positions.items():
            for room in self.room_doors:
                if self.shortest_path(pos, {room}) is None:
                    raise ValueError(f"{name} cannot reach the {room} from the start square.")

    # Display
    def render(self, hallway_tokens=None):
        # Return the map as text. hallway_tokens maps (row, col) -> symbol to draw on top.
        hallway_tokens = hallway_tokens or {}
        # Room letters are shown as-is
        display = {"#": " ", ".": ".", "X": "X"}
        tens = "    " + " ".join(str(c // 10) if c >= 10 else " " for c in range(self.cols))
        ones = "    " + " ".join(str(c % 10) for c in range(self.cols))
        lines = [tens, ones]
        for r in range(self.rows):
            cells = []
            for c in range(self.cols):
                if (r, c) in hallway_tokens:
                    cells.append(hallway_tokens[(r, c)])
                else:
                    sym = self.grid[r][c]
                    cells.append(display.get(sym, sym))
            lines.append(f"{r:>2}  " + " ".join(cells))
        return "\n".join(lines)


def print_board_preview():
    # Print the empty board with every character on their start square, plus each room's doors.
    board = Board(BOARD_MAP, ROOM_CODES, START_POSITIONS, SECRET_PASSAGES)
    start_tokens = {pos: TOKEN_SYMBOL[name] for name, pos in START_POSITIONS.items()}
    print(board.render(start_tokens))
    print()
    print("Tokens: " + "  ".join(f"{TOKEN_SYMBOL[n]}={n}" for n in CHARACTERS))
    print()
    for room in ROOMS:
        door_text = ", ".join(f"(row {d[0]}, col {d[1]})" for d, _ in board.doors_of(room))
        passage = board.secret_passage_from(room)
        extra = f"   | secret passage -> {passage}" if passage else ""
        print(f"{room:<14} doors: {door_text}{extra}")


if __name__ == "__main__":
    print_board_preview()

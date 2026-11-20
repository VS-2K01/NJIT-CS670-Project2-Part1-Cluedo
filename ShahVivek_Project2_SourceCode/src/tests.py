# Vivek Shah - CS 670 - Project 2 Part 1

# tests.py - Self-tests for the core rules.

# Checks move parsing, move validation (walls, room walls, board edge, too many steps, exact roll, blocked squares, room entry ending the move, no re-entry), setup (envelope, dealing, weapons), token movement on suggestions, and refutation order.

# Run with: python tests.py

import io
import contextlib

from config import MIN_PLAYERS, MAX_PLAYERS
from cards import CHARACTERS, WEAPONS, CATEGORY_OF
from board_layout import BOARD_MAP, ROOM_CODES, START_POSITIONS, SECRET_PASSAGES
from board import Board
from input_utils import parse_move_command, match_option, validate_move
from game import CluedoGame


def run_self_tests():
    b = Board(BOARD_MAP, ROOM_CODES, START_POSITIONS, SECRET_PASSAGES)

    # Parsing
    assert parse_move_command("UP 2, RIGHT 3") == [("UP", 2), ("RIGHT", 3)]
    assert parse_move_command("u2 l1") == [("UP", 2), ("LEFT", 1)]
    assert parse_move_command("down") == [("DOWN", 1)]
    assert parse_move_command("jump 3") is None
    assert parse_move_command("") is None
    assert match_option("mustard", CHARACTERS) == "Colonel Mustard"
    assert match_option("3", WEAPONS) == "Lead Pipe"
    # Ambiguous -> None
    assert match_option("mrs", CHARACTERS) is None

    # Move Validation (Miss Scarlett)
    scarlett = START_POSITIONS["Miss Scarlett"]
    assert validate_move(b, scarlett, [("UP", 1)], 1, set()).ok
    assert not validate_move(b, scarlett, [("LEFT", 1)], 1, set()).ok      # Lounge wall
    assert not validate_move(b, scarlett, [("DOWN", 1)], 1, set()).ok      # Off the board
    assert not validate_move(b, scarlett, [("UP", 4)], 3, set()).ok        # More than the roll
    assert not validate_move(b, scarlett, [("UP", 1)], 3, set()).ok        # Must use the full roll
    assert validate_move(b, scarlett, [("UP", 1)], 3, set(), exact=False).ok
    assert not validate_move(b, scarlett, [("UP", 1)], 1, {(23, 7)}).ok    # Blocked by a token
    entered = validate_move(b, (18, 5), [("DOWN", 3)], 6, set())           # Lounge door is just below
    assert entered.ok and entered.room == "Lounge" and entered.steps_used == 1
    assert not validate_move(b, (18, 5), [("DOWN", 1)], 6, set(), banned_room="Lounge").ok

    # Setup: envelope and dealing
    for players in range(MIN_PLAYERS, MAX_PLAYERS + 1):
        g = CluedoGame(CHARACTERS[:players], seed=players)
        cats = sorted(CATEGORY_OF[card] for card in g.solution.values())
        assert cats == ["character", "room", "weapon"]
        dealt = [card for p in g.players for card in p.hand]
        assert len(dealt) == 18 and len(set(dealt)) == 18
        assert not set(dealt) & set(g.solution.values())
        sizes = [len(p.hand) for p in g.players]
        assert max(sizes) - min(sizes) <= 1
        assert len(set(g.weapon_location.values())) == len(WEAPONS)

    # Suggestions move tokens
    g = CluedoGame(["Miss Scarlett", "Colonel Mustard", "Mrs. White"], seed=5)
    g.token_location["Miss Scarlett"] = "Kitchen"
    with contextlib.redirect_stdout(io.StringIO()):
        g.move_tokens_for_suggestion("Colonel Mustard", "Rope", "Kitchen")
    assert g.token_location["Colonel Mustard"] == "Kitchen"
    assert g.weapon_location["Rope"] == "Kitchen"
    assert g.player_for("Colonel Mustard").moved_by_suggestion

    # Refutation order: the first player to the suggester's left with a match shows it
    g = CluedoGame(["Miss Scarlett", "Colonel Mustard", "Mrs. White", "Reverend Green"], seed=1)
    scarlett, mustard, white, green = g.players
    scarlett.hand, mustard.hand = ["Dagger"], ["Rope"]
    white.hand, green.hand = ["Kitchen"], ["Wrench"]
    with contextlib.redirect_stdout(io.StringIO()):
        result = g._refute(mustard, ("Mrs. White", "Wrench", "Kitchen"))
    # White (next after Mustard) refutes, not Green
    assert result == ("Mrs. White", "Kitchen")
    assert mustard.seen == {"Kitchen": "Mrs. White"}
    with contextlib.redirect_stdout(io.StringIO()):
        result = g._refute(white, ("Professor Plum", "Revolver", "Hall"))
    # Nobody holds any of these
    assert result is None

    print("All self-tests passed.")


if __name__ == "__main__":
    run_self_tests()

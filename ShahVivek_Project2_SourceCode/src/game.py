# Vivek Shah - CS 670 - Project 2 Part 1

# game.py - The game engine.

# GameSetup builds a new game and tracks the state:
#  Players sorted into turn order (Scarlett, Mustard, White, Green, Peacock, Plum)
#  All six character tokens on their start squares, even characters nobody plays
#  Weapons in six different random rooms
#  The envelope: one random card from each category (_select_solution)
#  The other 18 cards shuffled and dealt round-robin; some players may get one extra (_deal_cards)
#  A token's location is a room name (str) or a hallway square (row, col)

# CluedoGame adds the rules of play:
#  play(): turns in a fixed order until QUIT (or an optional turn limit); then reveals the envelope
#  movement: roll one die in a hallway; in a room, ROLL to leave by a door (1 step), take a secret passage with no roll, STAY if a suggestion moved you there, or PASS
#  suggestions: forced on entering a room; the suggested character and weapon move into the room
#  refutation: from the next player in turn order; the first player with a match shows ONE card (they choose which); the card is printed only in a line addressed to the suggester

import random

from config import DIE_SIDES, REQUIRE_EXACT_ROLL, MIN_PLAYERS, MAX_PLAYERS
from cards import CHARACTERS, WEAPONS, ROOMS, ALL_CARDS, TOKEN_SYMBOL
from board_layout import BOARD_MAP, ROOM_CODES, START_POSITIONS, SECRET_PASSAGES
from board import Board
from input_utils import GameQuit, validate_move, format_steps, path_to_steps
from player import HumanPlayer


class GameSetup:
    # Creates a new game (envelope, deal, tokens) and offers helpers to inspect the state.

    def __init__(self, player_characters, seed=None):
        # player_characters - list of character names, one per player
        # seed - optional number for repeatable dice/shuffles
        if not MIN_PLAYERS <= len(player_characters) <= MAX_PLAYERS:
            raise ValueError(f"Cluedo needs {MIN_PLAYERS}-{MAX_PLAYERS} players.")
        if len(set(player_characters)) != len(player_characters):
            raise ValueError("Each player must use a different character.")

        self.rng = random.Random(seed)
        self.board = Board(BOARD_MAP, ROOM_CODES, START_POSITIONS, SECRET_PASSAGES)

        # Players take turns in the classic order: Scarlett, Mustard, White, Green, Peacock, Plum.
        ordered = sorted(player_characters, key=CHARACTERS.index)
        self.players = [HumanPlayer(character) for character in ordered]

        # Where every token is: a room name (str) or a hallway square (row, col).
        self.token_location = dict(START_POSITIONS)   # all six characters are on the board
        self.weapon_location = {}                     # weapon -> room name
        self.solution = {}                            # the confidential envelope
        self.turn_number = 0

        self._place_weapons()
        self._select_solution()
        self._deal_cards()

    # Setup Steps
    def _place_weapons(self):
        # Put each weapon in a different random room.
        for weapon, room in zip(WEAPONS, self.rng.sample(ROOMS, len(WEAPONS))):
            self.weapon_location[weapon] = room

    def _select_solution(self):
        # Secretly choose one character, one weapon and one room for the envelope.
        self.solution = {
            "character": self.rng.choice(CHARACTERS),
            "weapon": self.rng.choice(WEAPONS),
            "room": self.rng.choice(ROOMS),
        }

    def _deal_cards(self):
        # Shuffle the remaining 18 cards and deal them round-robin (some may get one extra).
        deck = [card for card in ALL_CARDS if card not in self.solution.values()]
        self.rng.shuffle(deck)
        for i, card in enumerate(deck):
            self.players[i % len(self.players)].receive_card(card)

    # Helper Functions
    def roll_die(self):
        return self.rng.randint(1, DIE_SIDES)

    @staticmethod
    def is_in_room(location):
        # Rooms are stored as names (str); hallway squares as (row, col) tuples.
        return isinstance(location, str)

    def location_of(self, player):
        return self.token_location[player.character]

    def describe_location(self, location):
        if self.is_in_room(location):
            return f"the {location}"
        return f"the hallway at row {location[0]}, col {location[1]}"

    def occupied_squares(self, exclude=None):
        #Hallway squares holding a token (optionally ignoring one character's own token).
        return {
            loc for name, loc in self.token_location.items()
            if name != exclude and not self.is_in_room(loc)
        }

    def player_for(self, character):
        # The Player controlling a character, or None if nobody is playing that character.
        for player in self.players:
            if player.character == character:
                return player
        return None

    def message_for(self, player, text):
        # Print a line addressed to one player (e.g. the card they were shown).
        print(f"   [Message for {player.character}] {text}")

    def routes_to_rooms(self, start, max_steps, banned_room=None, exclude_character=None):
        # Rooms reachable within max_steps, with the shortest route to each (used for hints).
        blocked = self.occupied_squares(exclude=exclude_character)
        routes = []
        for room in ROOMS:
            if room == banned_room:
                continue
            path = self.board.shortest_path(start, {room}, blocked)
            if path and len(path) <= max_steps:
                routes.append((room, len(path), path_to_steps(start, path)))
        return sorted(routes, key=lambda route: route[1])

    def render_board(self):
        # The map with hallway tokens drawn on it, plus what's inside each room.
        hallway_tokens = {
            loc: TOKEN_SYMBOL[name]
            for name, loc in self.token_location.items()
            if not self.is_in_room(loc)
        }
        lines = [self.board.render(hallway_tokens), ""]
        lines.append("Tokens: " + "  ".join(f"{TOKEN_SYMBOL[n]}={n}" for n in CHARACTERS))
        lines.append("Rooms:  " + "  ".join(f"{code}={name}" for code, name in ROOM_CODES.items()))
        lines.append("        (lowercase letter = door, X = center, . = hallway)")
        lines.append("Inside the rooms:")
        for room in ROOMS:
            people = [n for n, loc in self.token_location.items() if loc == room]
            weapons = [w for w, loc in self.weapon_location.items() if loc == room]
            if people or weapons:
                lines.append(f"   {room:<14} " + ", ".join(people + weapons))
        return "\n".join(lines)


class CluedoGame(GameSetup):
    # Full game: GameSetup's state plus the rules for each turn.

    # Main Loop
    def play(self, max_turns=None):
        # Take turns in order until QUIT is typed (or max_turns is reached).
        self._print_welcome()
        seat = 0
        try:
            while max_turns is None or self.turn_number < max_turns:
                player = self.players[seat % len(self.players)]
                seat += 1
                self.turn_number += 1
                self.take_turn(player)
            print(f"\nStopping: the turn limit of {max_turns} was reached.")
        except GameQuit:
            print("\nGame stopped. Thanks for playing!")

        s = self.solution
        print(f"\nThe envelope contained: {s['character']}, with the {s['weapon']}, in the {s['room']}.")

    def _print_welcome(self):
        print("=" * 64)
        print("  A murder has been committed in the mansion!")
        print("  One character, one weapon and one room are sealed in the envelope.")
        print("=" * 64)
        print("Turn order: " + "  ->  ".join(p.character for p in self.players))
        for p in self.players:
            print(f"   {p.character} was dealt {len(p.hand)} cards.")

    # One Turn
    def take_turn(self, player):
        print("\n" + "=" * 64)
        print(f"Turn {self.turn_number}: {player.character}")
        print("=" * 64)
        print(self.render_board())
        print(f"\nYou are in {self.describe_location(self.location_of(player))}.")
        print("Your cards: " + ", ".join(player.hand))
        print("(Type BOARD, NOTES, HAND or HELP at any prompt - or QUIT to stop.)")

        room_to_suggest_in = self.movement_phase(player)
        if room_to_suggest_in:
            self.suggestion_phase(player, room_to_suggest_in)

        # The STAY option lasts one turn only
        player.moved_by_suggestion = False

    # Movement
    def movement_phase(self, player):
        # Move the player. Returns the room they must suggest in, or None.
        location = self.location_of(player)
        if self.is_in_room(location):
            return self._turn_from_room(player, location)

        player.wait_for_roll(self)
        roll = self.roll_die()
        print(f"{player.character}, your roll is {roll}.")
        return self._walk(player, location, roll)

    def _turn_from_room(self, player, room):
        # A player starting in a room must roll to leave, or may use a secret passage.
        occupied = self.occupied_squares(exclude=player.character)
        free_doors = [(door, outside) for door, outside in self.board.doors_of(room) if outside not in occupied]
        passage = self.board.secret_passage_from(room)

        options = {}
        if free_doors:
            options["ROLL"] = "roll the die and leave through a door"
        else:
            print(f"   Every door out of the {room} is blocked by another token.")
        if passage:
            options["SECRET"] = f"take the secret passage to the {passage} (no roll needed)"
        if player.moved_by_suggestion:
            options["STAY"] = f"stay in the {room} and make a suggestion (you were moved here)"
        options["PASS"] = "stay here this turn (no suggestion)"

        action = player.choose_room_action(self, room, options)

        if action == "SECRET":
            self.token_location[player.character] = passage
            print(f"{player.character} takes the secret passage from the {room} to the {passage}.")
            return passage
        if action == "STAY":
            print(f"{player.character} stays in the {room}.")
            return room
        if action == "PASS":
            print(f"{player.character} stays in the {room} this turn.")
            return None

        # ROLL: leaving a room always needs a dice roll.
        player.wait_for_roll(self)
        roll = self.roll_die()
        print(f"{player.character}, your roll is {roll}.")
        index = player.choose_exit_door(self, room, free_doors)
        door, outside = free_doors[index]
        # Stepping out costs 1 step
        self.token_location[player.character] = outside
        print(f"{player.character} leaves the {room} onto row {outside[0]}, col {outside[1]} (1 step used).")
        return self._walk(player, outside, roll - 1, banned_room=room)

    def _walk(self, player, start, steps_left, banned_room=None):
        # Ask for a hallway move until it's legal, then apply it. Returns the room entered, if any.
        if steps_left <= 0:
            return None
        occupied = self.occupied_squares(exclude=player.character)
        while True:
            choice = player.choose_move(self, start, steps_left, banned_room)
            if choice == "PASS":
                print(f"{player.character} stays at {self.describe_location(start)}.")
                return None
            result = validate_move(self.board, start, choice, steps_left, occupied,
                                   REQUIRE_EXACT_ROLL, banned_room)
            if result.ok:
                break
            # Explain, then ask again
            print("   Invalid move: " + result.message)

        if result.room:
            self.token_location[player.character] = result.room
            print(f"{player.character} moves {format_steps(choice)} and enters the {result.room}.")
            if result.steps_used < sum(count for _, count in choice):
                print("   (Movement ends as soon as you enter a room.)")
            return result.room

        self.token_location[player.character] = result.end
        print(f"{player.character} moves {format_steps(choice)} to row {result.end[0]}, col {result.end[1]}.")
        return None

    # Suggestions
    def suggestion_phase(self, player, room):
        character, weapon = player.choose_suggestion(self, room)
        print(f'\n{player.character}: "I suggest it was {character}, with the {weapon}, in the {room}."')
        self.move_tokens_for_suggestion(character, weapon, room)
        self._refute(player, (character, weapon, room))

    def move_tokens_for_suggestion(self, character, weapon, room):
        # The suggested character and weapon are brought into the room immediately.
        if self.token_location[character] != room:
            self.token_location[character] = room
            print(f"   {character}'s token is moved into the {room}.")
            summoned = self.player_for(character)
            if summoned is not None:
                # They may suggest here next turn
                summoned.moved_by_suggestion = True
        if self.weapon_location[weapon] != room:
            self.weapon_location[weapon] = room
            print(f"   The {weapon} is moved into the {room}.")

    def _refute(self, suggester, suggestion):
        # Go around the table from the suggester's left until someone can show a card.
        n = len(self.players)
        start = self.players.index(suggester)
        for offset in range(1, n):
            other = self.players[(start + offset) % n]
            matching = [card for card in suggestion if card in other.hand]
            if not matching:
                print(f"   {other.character} cannot refute.")
                continue
            card = other.choose_card_to_show(self, matching, suggester)
            print(f"   {other.character} shows a card to {suggester.character}.")
            self.message_for(suggester, f"{other.character} showed you: {card}")
            suggester.observe_shown_card(card, other.character)
            return other.character, card
        print("   Nobody could refute the suggestion!")
        return None

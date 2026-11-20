# Vivek Shah - CS 670 - Project 2 Part 1

# player.py - Players.

# Player stores a character, their hand, the cards they've been shown (and by whom), and whether another player's suggestion moved them into a room (which gives them the STAY option).

# HumanPlayer makes every decision by prompting at the keyboard. Its ask() method handles the commands that work at every prompt: BOARD, NOTES, HAND and HELP. The game engine (game.py) only calls the choose_... methods, so the rules stay in one place.

from cards import CHARACTERS, WEAPONS, ROOMS
from input_utils import HELP_TEXT, read_line, parse_move_command, format_steps, match_option, numbered


class Player:
    # Common data for every player.
    is_human = False

    def __init__(self, character):
        # Which token this player controls
        self.character = character
        # Cards dealt to this player
        self.hand = []
        # Card -> name of the player who showed it
        self.seen = {}
        # True if another player's suggestion pulled us into a room
        self.moved_by_suggestion = False

    def receive_card(self, card):
        self.hand.append(card)

    def observe_shown_card(self, card, shown_by):
        # Called when another player shows us a card during a refutation.
        self.seen[card] = shown_by

    def notes_text(self):
        # Simple notes: X = you hold it or were shown it, ? = not seen yet.
        lines = [f"Notes for {self.character}:"]
        for title, cards in (("Characters", CHARACTERS), ("Weapons", WEAPONS), ("Rooms", ROOMS)):
            lines.append(f"  {title}:")
            for card in cards:
                if card in self.hand:
                    lines.append(f"    [X] {card:<16} (in your hand)")
                elif card in self.seen:
                    lines.append(f"    [X] {card:<16} (shown to you by {self.seen[card]})")
                else:
                    lines.append(f"    [?] {card}")
        return "\n".join(lines)


class HumanPlayer(Player):
    # A player controlled through text prompts.
    is_human = True

    def ask(self, game, prompt):
        # Prompt for input, handling the commands that work at every prompt.
        while True:
            answer = read_line(prompt)
            command = answer.upper()
            if command == "BOARD":
                print(game.render_board())
            elif command == "NOTES":
                print(self.notes_text())
            elif command == "HAND":
                print("Your cards: " + ", ".join(self.hand))
            elif command == "HELP":
                print(HELP_TEXT)
            else:
                return answer

    def _pick(self, game, prompt, options):
        # Ask until the answer matches exactly one of `options`.
        print("   " + numbered(options))
        while True:
            choice = match_option(self.ask(game, prompt), options)
            if choice:
                return choice
            print("   Not recognized - type the number or (part of) the name.")

    def wait_for_roll(self, game):
        self.ask(game, f"{self.character}, press Enter to roll the dice: ")

    def choose_room_action(self, game, room, options):
        # Options: dict of action key -> description (ROLL, SECRET, STAY, PASS).
        print(f"{self.character}, you are in the {room}. What would you like to do?")
        labels = {}
        for key, description in options.items():
            label = key
            if key == "SECRET":
                destination = game.board.secret_passage_from(room)
                label = "SECRET_PASSAGE_TO_" + destination.upper().replace(" ", "_")
            labels[key] = label
            print(f"   {label:<32} {description}")
        while True:
            answer = self.ask(game, "Your choice: ").upper()
            if answer == "" and "ROLL" in options:
                # Enter = roll (convenience)
                return "ROLL"
            if answer.startswith("SECRET") and "SECRET" in options:
                return "SECRET"
            if answer in options:
                return answer
            print("   Please type one of: " + ", ".join(labels.values()))

    def choose_exit_door(self, game, room, doors):
        # doors: list of (door square, outside square). Returns the index of the chosen door.
        if len(doors) == 1:
            outside = doors[0][1]
            print(f"   You leave the {room} by its door onto row {outside[0]}, col {outside[1]}.")
            return 0
        print(f"   Doors out of the {room}:")
        for i, (door, outside) in enumerate(doors, start=1):
            print(f"     {i}) door at row {door[0]}, col {door[1]}  ->  step out to row {outside[0]}, col {outside[1]}")
        while True:
            answer = self.ask(game, f"Choose a door (1-{len(doors)}): ")
            if answer.isdigit() and 1 <= int(answer) <= len(doors):
                return int(answer) - 1
            print("   Please type one of the door numbers.")

    def choose_move(self, game, start, steps_left, banned_room):
        # Returns a list of (direction, count) steps, or the string 'PASS'.
        # Helpful hint: which rooms can be reached with this roll, and how.
        routes = game.routes_to_rooms(start, steps_left, banned_room, self.character)
        if routes:
            print("   Rooms you can reach this turn:")
            for room, distance, steps in routes:
                print(f"     {room:<14} {distance} step(s): {format_steps(steps)}")
        else:
            print("   No room is within reach this turn - you'll finish in a hallway.")
        while True:
            answer = self.ask(
                game,
                f"{self.character}, you have {steps_left} step(s) from row {start[0]}, col {start[1]}. "
                f"Enter your move (e.g., UP 2, RIGHT 2) or PASS: ",
            )
            if answer.upper() == "PASS":
                return "PASS"
            steps = parse_move_command(answer)
            if steps:
                return steps
            print("   Sorry, I didn't understand that. Example: UP 2, LEFT 1   (or U2 L1)")

    def choose_suggestion(self, game, room):
        # Returns (character, weapon). The room is always the player's current room.
        print(f"   Characters: {numbered(CHARACTERS)}")
        print(f"   Weapons:    {numbered(WEAPONS)}")
        while True:
            answer = self.ask(game, f"{self.character}, you are in the {room}. Make a suggestion (Character, Weapon): ")
            parts = answer.split(",")
            if len(parts) == 2:
                character = match_option(parts[0], CHARACTERS)
                weapon = match_option(parts[1], WEAPONS)
                if character and weapon:
                    return character, weapon
            print("   Please give a character and a weapon separated by a comma, e.g. 'Mustard, Rope' or '2, 5'.")

    def choose_card_to_show(self, game, matching, suggester):
        # The refuting player chooses which matching card to show.
        if len(matching) == 1:
            print(f"   {self.character}, you hold {matching[0]}, so you must show it to {suggester.character}.")
            return matching[0]
        print(f"   {self.character}, you can refute {suggester.character}'s suggestion. Choose ONE card to show:")
        return self._pick(game, "Card to show: ", matching)

# Vivek Shah - CS 670 - Project 2 Part 1

# main.py - Entry point for Cluedo Part 1.

# Asks how many players (2-6) and which character each one uses, then starts the game. All players share one screen and take turns at the keyboard.

# Run with: python main.py

from config import MIN_PLAYERS, MAX_PLAYERS
from cards import CHARACTERS
from input_utils import GameQuit, read_line, match_option, numbered
from game import CluedoGame


def ask_number(prompt, low, high):
    # Ask until the user types a whole number between low and high.
    while True:
        raw = read_line(prompt)
        if raw.isdigit() and low <= int(raw) <= high:
            return int(raw)
        print(f"   Please enter a whole number from {low} to {high}.")


def configure_players():
    # Interactive setup. Returns the list of characters being played.
    print("=" * 64)
    print("  CLUEDO - Part 1 (text edition)")
    print("=" * 64)
    print("Type QUIT at any prompt to stop.\n")
    count = ask_number(f"How many players ({MIN_PLAYERS}-{MAX_PLAYERS})? ", MIN_PLAYERS, MAX_PLAYERS)

    chosen = []
    for seat in range(1, count + 1):
        # Always number the full list, so each character keeps the same number (1 = Miss Scarlett ... 6 = Professor Plum).
        print(f"\nPlayer {seat}, choose a character:  {numbered(CHARACTERS)}")
        if chosen:
            print("   Already taken: " + ", ".join(chosen))
        while True:
            character = match_option(read_line("Character (number or name): "), CHARACTERS)
            if character and character not in chosen:
                break
            if character:
                print(f"   {character} is already taken - pick another character.")
            else:
                print("   Not recognized - pick one from the list above.")
        chosen.append(character)
    return chosen


def main(seed=None):
    # Configure players, then play.
    try:
        characters = configure_players()
    except GameQuit:
        print("Setup canceled.")
        return
    game = CluedoGame(characters, seed=seed)
    game.play()


if __name__ == "__main__":
    main()

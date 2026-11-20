# Vivek Shah - CS 670 - Project 2 Part 1
## Fall 2026

A digital, command-line version of the classic murder-mystery board game **Cluedo**. It's written in Python with an object-oriented design, and includes a Jupyter notebook that walks through each module and runs the game.

Part 1 Covers:
* The mansion layout (a 25 × 24 grid with 9 rooms, doors and secret passages)
* The 6 characters and their starting positions, and the 6 weapons
* Random solution selection and even dealing of the cards
* Turn-based dice movement with move validation
* Suggestions, which move the suggested character and weapon tokens into the room, and refutations.

All players are human and share one screen, taking turns at the keyboard. A game runs until a player types `QUIT`, which then reveals the envelope.

---

## Project Files

The `.py` files are in the `src/` folder, and the notebook is in the `Colab Demo/` folder.

| File | Description |
|---|---|
| `main.py` | **Entry point.** Asks for the players, then starts the game |
| `config.py` | Rule settings: die size, exact-roll rule, player limits |
| `cards.py` | The 6 characters, 6 weapons and 9 rooms |
| `board_layout.py` | The mansion map, starting squares, secret passages and directions |
| `board.py` | `Board` class: square queries, doors, route finding, map checks, drawing |
| `input_utils.py` | Input helpers and move validation (`validate_move`) |
| `player.py` | `Player` and `HumanPlayer` (all keyboard prompts) |
| `game.py` | `GameSetup` (envelope, dealing, tokens) and `CluedoGame` (turns, movement, suggestions, refutations) |
| `tests.py` | Self-tests of the core rules |
| `ShahVivek_Project2Part1_Demo.ipynb` | Guided notebook: explains each module, runs the tests, and plays the game |

---

## Prerequisites & Dependencies

* **Python 3.8 or newer**
* **No third-party packages.** The game only uses the Python standard library (`random`, `re`, `collections`, `dataclasses`, `typing`, `io`, `contextlib`).
* **For the notebook:** Google Colab or Jupyter on your computer (`pip install notebook`).

---

## How to run

### 1. Clone the repository
```bash
git clone https://github.com/VS-2K01/NJIT-CS670-Project2-Part1-Cluedo.git
```

### 2. Navigate to the source code directory
```bash
cd NJIT-CS670-Project2-Part1-Cluedo/ShahVivek_Project2_SourceCode/src
```

### 3. Run the Game

**Option A: terminal**
```bash
python main.py
```
To run the self-tests:
```bash
python tests.py
```

**Option B: Jupyter on your computer**
```bash
pip install notebook          # only if Jupyter isn't installed yet
jupyter notebook "../Colab Demo/ShahVivek_Project2Part1_Demo.ipynb"
```
Then choose **Run → Run All Cells**  and play in Section 8.

**Option C: Google Colab**
1. Go to <https://colab.research.google.com>, then **File → Open notebook → GitHub**. Paste `https://github.com/VS-2K01/NJIT-CS670-Project2-Part1-Cluedo` and open `ShahVivek_Project2Part1_Demo.ipynb`.
2. Click **Runtime → Run all**. The **Setup** cell (Section 1) downloads the code automatically and prints `Using the game files in: .../src`.
3. Scroll to the **Play the game** cell (Section 8) and type your answers in the input box under it.

---

## How to Play

| Situation | What to type |
|---|---|
| Number of Players | `2` – `6` |
| Choose a Character | Its number or name (e.g. `1` or `scarlett`) |
| Roll the Die | Press **Enter** |
| Move in a Hallway | `UP 2, RIGHT 3` or `U2 R3` (The game lists the rooms you can reach and the exact commands) |
| Start of Turn in a Room | `ROLL` (leave by a door), `SECRET_PASSAGE_TO_<ROOM>`, `STAY` (only if a suggestion moved you there), or `PASS` |
| Make a Suggestion | `Character, Weapon`, e.g. `Mustard, Rope` or `2, 5`. The `Room` will always equal the current room you are in. |
| Any Prompt | `BOARD`, `NOTES`, `HAND`, `HELP`, `QUIT` (Quitting ends the game and reveals the envelope) |

### Your First Game, Step by Step

1. **Start the game.** Run `python main.py`. Enter the number of players (2–6). Then each player picks a character by number (1 = Miss Scarlett, 2 = Colonel Mustard, 3 = Mrs. White, 4 = Reverend Green, 5 = Mrs. Peacock, 6 = Professor Plum) or by name. Turns always go in that order, skipping characters nobody picked. Unpicked characters stay on the board and can still be pulled into rooms by suggestions.
2. **Read the board.** The map prints at the start of every turn. Rows are numbered down the left side (0–24) and columns across the top (0–23; the tens digit is on the upper line). Positions are given as *row, col*.
   * `.` = hallway, capital letters = rooms (the legend is under the map), a lowercase letter = a door, `X` = the center (you can't enter it), `1`–`6` = character tokens.
   * Under the map you'll see which characters and weapons are in each room, where you are, and your cards.
3. **Take a turn in a hallway.** Press **Enter** to roll. The game lists the rooms you can reach with that roll and the exact command for each. Type your move, for example `UP 2, RIGHT 3`. You must use the whole roll unless you step onto a door; entering a room ends your move. If a move is illegal (a wall, another token, too many or too few steps), the game says why and asks again. Type `PASS` to stay where you are.
4. **Make a suggestion.** When you enter a room, type a character and a weapon, for example `Mustard, Rope` or `2, 5`. The room is always the one you're in. The suggested character's token and the weapon move into that room.
5. **Refute.** The game asks the other players in turn order. If you hold one of the suggested cards, the game shows it for you; if you hold more than one, choose which to show by number. Only the suggesting player should read the line that starts `[Message for ...]`, so everyone else looks away.
6. **Start a turn in a room.** Choose from the menu:
   * `ROLL` to leave by a door. If there are several doors, pick one by number. Stepping out uses 1 step of your roll.
   * `SECRET_PASSAGE_TO_<ROOM>` (Kitchen, Study, Conservatory and Lounge only). This needs no roll, and you must then make a suggestion.
   * `STAY`, only if another player's suggestion moved you there.
   * `PASS`.
7. **Stop the game.** Type `QUIT` at any prompt. The game ends and reveals the envelope. Part 1 has no accusations, so a game continues until someone quits.

**Main Rules Implemented**
* One six-sided die. Movement is horizontal or vertical along hallway squares only, and two tokens can't share a hallway square.
* You must use your whole roll **unless** you enter a room. Entering a room ends your move.
* Rooms can only be entered and left through doors. Leaving a room needs a roll, and stepping out of the door uses 1 step. You can't re-enter the room you just left on the same turn.
* Secret passages (Kitchen ↔ Study, Conservatory ↔ Lounge) need no roll.
* Entering a room means you must make a suggestion. The suggested character and weapon tokens are moved into that room.
* Refutation goes around the table from the next player. The first player who can shows **one** card, which appears only in a line addressed to the suggester (`[Message for <player>]`).

### Troubleshooting

| Problem | Fix |
|---|---|
| `python: command not found`, or Windows opens the Microsoft Store | Use `python3` (Mac/Linux) or `py` (Windows). If neither works, install Python from <https://www.python.org/downloads/>; on Windows, tick **"Add Python to PATH"** during setup. |
| `can't open file 'main.py'` | You aren't in the `src` folder. Repeat step 2. |
| `jupyter: command not found` | Run `pip install notebook`, or start it with `python -m notebook "../Colab Demo/ShahVivek_Project2Part1_Demo.ipynb"`. |
| Colab: "Couldn't find the game's .py files" | Run the **Setup** cell (Section 1) first, and check you have internet access. |
| Colab: the game seems stuck | It's waiting for you. Type in the input box under the **Play the game** cell. |

---

## How the Files Fit Together

Imports only flow one way, so no two files import each other:

```
config.py   cards.py   board_layout.py
        \       |       /
         board.py   input_utils.py
                \      /
               player.py
                   |
                game.py
                   |
                main.py      (tests.py imports from all of them)
```

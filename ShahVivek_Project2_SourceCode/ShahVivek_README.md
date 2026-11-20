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
1. Go to <https://colab.research.google.com>, then **File → Open notebook → GitHub**. Paste the repository URL and open `ShahVivek_Project2Part1_Demo.ipynb`.
2. Colab starts with no files, so in the **Setup** cell (Section 1) set `REPO_URL` to your repository URL. Alternatively, upload the nine `.py` files with the **Files** panel (the folder icon on the left).
3. Click **Runtime → Run all** and answer the prompts in the **Play the game** cell (Section 8).

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

**Main Rules Implemented**
* One six-sided die. Movement is horizontal or vertical along hallway squares only, and two tokens can't share a hallway square.
* You must use your whole roll **unless** you enter a room. Entering a room ends your move.
* Rooms can only be entered and left through doors. Leaving a room needs a roll, and stepping out of the door uses 1 step. You can't re-enter the room you just left on the same turn.
* Secret passages (Kitchen ↔ Study, Conservatory ↔ Lounge) need no roll.
* Entering a room means you must make a suggestion. The suggested character and weapon tokens are moved into that room.
* Refutation goes around the table from the next player. The first player who can shows **one** card, which appears only in a line addressed to the suggester (`[Message for <player>]`).

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

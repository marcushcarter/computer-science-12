import sys, time, random

import json
import os

SAVE_FILE = "prestige_save.json"

def sprint(text, delay=0.05):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)

yourTurn = True

# CHESS VALID MOVES
# we have a map of the chess pieces and thier movement types like the horse can move 1 up/down and 2 left/right or 2 up/down and 1 left/right
# all of these are relatvie upwards 
# we check if a move is valid by looking if the move is valid but only for going the players/opponents direction

PIECE_VALUES = {
    "P": 1,
    "H": 2,
    "R": 3,
    "Q": 4,
    "K": 0,
}

class Achievements:

    def __init__(self):
        self.run_achievements = {
            "untouchable": False
        }
        self.prestige = {
            "total_gold_earned": 0,
            "wealth_accumulator": False
        }
        self.load()

    def load(self):
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
                self.prestige.update(data)

    def save(self):
        with open(SAVE_FILE, "w") as f:
            json.dump(self.prestige, f)

    def unlock_run(self, key, name):
        if not self.run_achievements[key]:
            self.run_achievements[key] = True
            print(f"\nAchievement Unlocked: {name}\n")

    def unlock_prestige(self, key, name):
        if not self.prestige[key]:
            self.prestige[key] = True
            print(f"\nPrestige Achievement Unlocked: {name}\n")
            self.save()

    def reset_run(self):
        for k in self.run_achievements:
            self.run_achievements[k] = False

    def reset_run(self):
        for k in self.run_achievements:
            self.run_achievements[k] = False

    def get_all_achievements(self):
        achievements_list = []
        for k, v in self.run_achievements.items():
            status = "Unlocked" if v else "Locked"
            achievements_list.append(f"Run: {k} - {status}")
        for k, v in self.prestige.items():
            if isinstance(v, bool):
                status = "Unlocked" if v else "Locked"
                achievements_list.append(f"Prestige: {k} - {status}")
            else:
                achievements_list.append(f"Prestige: {k} - {v}")
        return achievements_list

    def show_achievements(self):
        print("\n=== ACHIEVEMENTS ===")
        for ach in self.get_all_achievements():
            print(ach)
        input("\n(Press Enter to return to shop)")

class Board:

    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.board = [["." for _ in range(w)] for _ in range(h)]
        self.overlay = [["." for _ in range(w)] for _ in range(h)]
        self.player = [["." for _ in range(w)] for _ in range(2)]
        self.opponent = [["." for _ in range(w)] for _ in range(2)]
        self.lives = 3
        self.round = 1

    def random_opponent_row(self, w, difficulty=0):
        choices = []
        choices += ["p"] * max(1, 6 - difficulty)
        choices += ["r"] * min(2, difficulty)
        choices += ["h"] * min(2, difficulty)
        choices += ["q"] * min(1, difficulty)
        choices += ["."] * max(1, 3 - difficulty)
        row = [random.choice(choices) for _ in range(w)]
        return row

    def in_bounds(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h

    def reset_board(self):
        for y in range(self.h):
            for x in range(self.w):
                self.board[y][x] = "."

        for i, row in enumerate(self.opponent):
            for x, piece in enumerate(row):
                self.board[i][x] = piece

        for i, row in enumerate(self.player):
            for x, piece in enumerate(row):
                self.board[self.h - len(self.player) + i][x] = piece

        self.clear_overlay()

    def your_move(self, y1, x1, y2, x2):
        global yourTurn
        if not self.in_bounds(x1, y1) or not self.in_bounds(x2, y2):
            print("Invalid move: out of bounds")
            return
        if y1 == y2 and x1 == x2:
            print("Invalid move: piece already there")
            return

        piece = self.board[y1][x1]
        target = self.board[y2][x2]

        if piece == ".":
            print("Invalid move: no piece here")
            return
        if piece.islower():
            print("Invalid move: can't move opponent")
            return
        if target.isupper():
            print("Invalid move: can't move onto your own piece")
            return

        self.board[y2][x2] = piece
        self.board[y1][x1] = "."

        self.clear_overlay()
        self.overlay[y1][x1] = "*"
        self.overlay[y2][x2] = "#"

        yourTurn = False
        print("YOU MOVED")

    def opponent_move(self):
        pass

    def clear_overlay(self):
        for y in range(self.h):
            for x in range(self.w):
                self.overlay[y][x] = "."

    def print_board(self):
        cols = [chr(ord('a') + i) for i in range(self.w)]
        print("  " + " ".join(cols))
        for y in range(self.h):
            row_num = self.h - y
            row = []
            for x in range(self.w):
                piece = self.board[y][x]
                overlay = self.overlay[y][x]

                if overlay == "#":
                    display = f"\033[32m{piece}\033[0m"
                elif overlay == "*":
                    display = f"\033[33m*\033[0m"
                elif piece.islower():
                    display = f"\033[31m{piece}\033[0m"  # opponent red
                else:
                    display = piece
                row.append(display)
            print(f"{row_num} " + " ".join(row))
        print()

    def setup_opponent(self):
        w = self.w
        king_pos = w // 2
        difficulty = min(self.round // 2, 5)

        row_with_king = []
        for x in range(w):
            if x == king_pos:
                row_with_king.append("k")
            else:
                row_with_king.append(random.choice(["p", "r", "h", "q", "."]))
        top_row = self.random_opponent_row(w, difficulty)

        self.opponent = [row_with_king, top_row]

    def your_king(self):
        return any(self.board[y][x] == "K" for y in range(self.h) for x in range(self.w))

    def other_king(self):
        return any(self.board[y][x] == "k" for y in range(self.h) for x in range(self.w))
    
    def calculate_board_value(self):
        value = 0
        for row in self.player:
            for piece in row:
                value += PIECE_VALUES.get(piece, 0)
        return value

    def reset_run(self):
        self.gold = 0
        
    def add_piece(self, piece):
        for row in self.player:
            for i in range(len(row)):
                if row[i] == ".":
                    row[i] = piece
                    print(f"You gained a {piece}!")
                    return
        print("No space for new piece.")

SHOP_ITEMS = {
    "heal": {
        "name": "Repair King (+1 life)",
        "cost": 15,
        "action": lambda board: setattr(board, "lives", board.lives + 1)
    },
    "pawn": {
        "name": "Hire Pawn",
        "cost": 4,
        "action": lambda board: board.add_piece("P")
    },
    "rook": {
        "name": "Hire Rook",
        "cost": 8,
        "action": lambda board: board.add_piece("R")
    },
    "achievements": {
        "name": "View Achievements",
        "cost": 0,
        "action": lambda board: achievements.show_achievements()
    }
}

def shop(board):
    while True:
        print("\n=== SHOP ===")
        print(f"Gold: {board.gold}")
        print(f"Lives: {board.lives}")
        print()

        for key, item in SHOP_ITEMS.items():
            print(f"{key:<6} - {item['name']} ({item['cost']}g)")

        print("leave  - continue to next round")
        print()

        cmd = input("> ").lower().strip()

        if cmd == "leave":
            print("Leaving shop...\n")
            return

        if cmd not in SHOP_ITEMS:
            print("Unknown item.")
            continue

        item = SHOP_ITEMS[cmd]

        if board.gold < item["cost"]:
            print("Not enough gold.")
            continue

        board.gold -= item["cost"]
        item["action"](board)

def parse_square(sq, w, h):
    if len(sq) != 2:
        return None
    col = ord(sq[0].lower()) - ord('a')
    row = h - int(sq[1])
    if 0 <= col < w and 0 <= row < h:
        return row, col
    return None

board = Board(6,6)

board.player = [
    ["P", "P", "P", "P", "P", "P"],
    ["R", "H", "K", "Q", "H", "R"]
]

board.opponent = [
    ["r", "h", "k", "q", "h", "r"],
    ["p", "p", "p", "p", "p", "p"]
]

board.reset_board()

achievements = Achievements()

def command():
    board.print_board()
    cmd = input("> ").lower().split()
    if not cmd:
        return
    
    if cmd[0] == "move" and len(cmd) >= 3:
        start = parse_square(cmd[1], board.w, board.h)
        end = parse_square(cmd[2], board.w, board.h)

        if start and end:
            board.your_move(*start, *end)
        else:
            print("Invalid move")
    else:
        print("Invalid command")

def tutorial():
    print()
    board.print_board()

    steps = [
        "Welcome to ChessLite tutorial!",
        "Step 1: This is your board. Uppercase = your pieces, lowercase = opponent.",
        "Step 2: Move a piece using 'move start_square end_square'. Example: move a5 a4",
        "Step 3: You cannot move opponent pieces or empty squares.",
        "Step 4: Special commands like 'ballistic' or 'sell' can also be used.",
        "Step 5: That's it! Tutorial complete. You're ready to play."
    ]

    firstTime = True

    for text in steps:
        if firstTime:
            sprint(text)
            input(" (Press Enter to continue)")
            firstTime = False
        else:
            sprint(text)
            input()

    print("\nTutorial finished. Let's start the game!")

dialog = [
    "Mentor: Welcome to the board, rookie. Are you ready to lose gracefully?\nStudent: Ready? I wasn't even ready to sign up for this ancient death trap!\nMentor: Ancient? It's literally older than the internet. And the last guy who underestimated it… well, you'll see.",
    "Mentor: See that row? Those pawns aren't toys.\nStudent: They look like toys.\nMentor: They *act* like toys. Until they bite your fingers off.",
    "Mentor: That king over there, dead center? He thinks he's clever.\nStudent: He? It's a piece of wood.\nMentor: Wood with attitude. And apparently memory. Don't ask me why.",
    "Mentor: Every piece has a story.\nStudent: A story? Like bedtime stories?\nMentor: No. Like ‘I've seen thirty bad players die and survived anyway' stories. Dark bedtime stories.",
    "Mentor: You think you're in control.\nStudent: I *am* in control!\nMentor: You're renting it. Short-term lease. Non-refundable.",
    "Mentor: The board doesn't care about your feelings.\nStudent: I think it's staring at me.\nMentor: That's because it is. And it's judging your fashion sense.",
    "Mentor: Your rook just sneezed. Did you notice?\nStudent: What? It can't sneeze!\nMentor: That's what they all say. Then suddenly it's on the opposite side of the board, eating your pawns.",
    "Mentor: When your king falls, something… changes.\nStudent: Like what? Gravity?\nMentor: Like the universe noticing you are fragile and laughing quietly.",
    "Mentor: The enemy pieces adapt.\nStudent: Adapt? They're literally wood and plastic.\nMentor: Don't underestimate wooden sarcasm. Or plastic rage. They're dangerous.",
    "Mentor: Some rounds you win. Some rounds you learn.\nStudent: Mostly I lose.\nMentor: Learning through pain is the only way here. And don't forget: the loser buys the next set of imaginary chess snacks.",
    "Mentor: At the end, only one king stands.\nStudent: Hopefully mine.\nMentor: Hopefully. But maybe not. And maybe it's the janitor's king. Who even knows at this point.",
    "Mentor: Remember, you're not playing chess.\nStudent: Then what am I playing?\nMentor: Fate, chance, and poor decision-making dressed as strategy.",
    "Mentor: Now go. Make your first move.\nStudent: Fine, but if I die, I'm haunting you.\nMentor: Please do. I need moral support."
]

dialogIndex = 0

def play_dialog():
    global dialogIndex

    if dialogIndex >= len(dialog):
        return

    sprint(dialog[dialogIndex])
    input("\n(Press Enter)")
    print()

    dialogIndex += 1

def main():
    global running
    running = True

    achievements.reset_run()
    board.reset_run()
    tutorial()

    while running:
        play_dialog()

        board.setup_opponent()
        board.reset_board()
        starting_lives = board.lives

        while board.your_king() and board.other_king():
            command()
            board.opponent_move()
            print()
            if not board.your_king():
                print("Your king was taken :(")
                board.lives -= 1
                break

            if not board.other_king():
                print("You took your opponents king!")
                break

        if board.lives == starting_lives:
            achievements.unlock_run(
                "untouchable",
                "Untouchable — Finish a round without losing a life"
            )

        reward = board.calculate_board_value() + board.round
        board.gold += reward
        achievements.prestige["total_gold_earned"] += reward
        print(f"You earned {reward} gold.")

        if achievements.prestige["total_gold_earned"] >= 100:
            achievements.unlock_prestige(
                "wealth_accumulator",
                "Wealth Accumulator — Earn 100 total gold"
            )

        board.round += 1

        if board.lives > 0:
            print(f"Round complete. Lives remaining: {board.lives}.")
            shop(board)
        else:
            running = False
            print("Your king ran out of health. Game over!")

main()
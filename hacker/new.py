import random
import copy

# =============================
# DATA
# =============================

FILES = "abcdefgh"

PIECE_VALUES = {
    "P": 1,
    "N": 3,
    "B": 3,
    "R": 5,
    "Q": 9,
    "K": 100
}

SHOP_ITEMS = [
    ("Extra Pawn", 15, "start_pawn"),
    ("Knight Training (+1 knight)", 25, "extra_knight"),
    ("Royal Treasury (+5 gold per win)", 20, "bonus_gold"),
    ("Heal King", 10, "heal")
]

# =============================
# GAME STATE
# =============================

class RunState:
    def __init__(self):
        self.gold = 10
        self.floor = 1
        self.bonus_gold = 0
        self.start_pawn = 0
        self.extra_knight = 0

    def reset(self):
        self.__init__()

# =============================
# BOARD
# =============================

def create_board(state):
    board = [["." for _ in range(8)] for _ in range(8)]

    # enemy
    board[0] = list("rnbqkbnr")
    board[1] = ["p"] * 8

    # player
    board[6] = ["P"] * 8
    board[7] = list("RNBQKBNR")

    # upgrades
    for i in range(state.start_pawn):
        board[5][i] = "P"

    for i in range(state.extra_knight):
        board[5][7 - i] = "N"

    return board


def print_board(board):
    print("\n  a b c d e f g h")
    for r in range(8):
        print(8 - r, end=" ")
        for c in range(8):
            print(board[r][c], end=" ")
        print()
    print()


# =============================
# MOVE LOGIC
# =============================

def in_bounds(r, c):
    return 0 <= r < 8 and 0 <= c < 8


def is_white(p):
    return p.isupper()


def parse_square(s):
    col = FILES.index(s[0])
    row = 8 - int(s[1])
    return row, col


def path_clear(board, r, c, dr, dc):
    r += dr
    c += dc
    while in_bounds(r, c):
        if board[r][c] != ".":
            return False
        r += dr
        c += dc
    return True


def legal_moves(board, r, c):
    p = board[r][c]
    if p == ".":
        return []

    moves = []
    white = is_white(p)

    def add(nr, nc):
        if not in_bounds(nr, nc):
            return
        target = board[nr][nc]
        if target == "." or is_white(target) != white:
            moves.append((nr, nc))

    # Pawn
    if p.upper() == "P":
        d = -1 if white else 1
        if in_bounds(r + d, c) and board[r + d][c] == ".":
            moves.append((r + d, c))
        for dc in (-1, 1):
            nr, nc = r + d, c + dc
            if in_bounds(nr, nc) and board[nr][nc] != ".":
                if is_white(board[nr][nc]) != white:
                    moves.append((nr, nc))

    # Knight
    elif p.upper() == "N":
        for dr, dc in [
            (2,1),(2,-1),(-2,1),(-2,-1),
            (1,2),(1,-2),(-1,2),(-1,-2)
        ]:
            add(r+dr,c+dc)

    # King
    elif p.upper() == "K":
        for dr in (-1,0,1):
            for dc in (-1,0,1):
                if dr or dc:
                    add(r+dr,c+dc)

    # Sliding pieces
    def slide(dirs):
        for dr, dc in dirs:
            nr, nc = r+dr, c+dc
            while in_bounds(nr,nc):
                if board[nr][nc]==".":
                    moves.append((nr,nc))
                else:
                    if is_white(board[nr][nc]) != white:
                        moves.append((nr,nc))
                    break
                nr+=dr
                nc+=dc

    if p.upper()=="B":
        slide([(1,1),(1,-1),(-1,1),(-1,-1)])
    elif p.upper()=="R":
        slide([(1,0),(-1,0),(0,1),(0,-1)])
    elif p.upper()=="Q":
        slide([(1,1),(1,-1),(-1,1),(-1,-1),(1,0),(-1,0),(0,1),(0,-1)])

    return moves


# =============================
# AI
# =============================

def all_moves(board, white):
    result = []
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p != "." and is_white(p)==white:
                for m in legal_moves(board,r,c):
                    result.append((r,c,m[0],m[1]))
    return result


def ai_move(board):
    moves = all_moves(board, False)
    if not moves:
        return False

    # greedy capture AI
    best = None
    best_score = -999

    for m in moves:
        tr, tc = m[2], m[3]
        target = board[tr][tc]
        score = PIECE_VALUES.get(target.upper(),0) if target!="." else 0
        score += random.random()
        if score > best_score:
            best_score = score
            best = m

    r,c,tr,tc = best
    board[tr][tc]=board[r][c]
    board[r][c]="."
    return True


# =============================
# WIN CHECK
# =============================

def king_alive(board, white):
    target = "K" if white else "k"
    return any(target in row for row in board)


# =============================
# SHOP
# =============================

def shop(state):
    print("\n=== SHOP ===")
    for i,(name,cost,_) in enumerate(SHOP_ITEMS):
        print(f"{i+1}. {name} ({cost}g)")
    print("0. leave")

    choice=input("> ")

    if not choice.isdigit():
        return

    choice=int(choice)-1
    if choice<0 or choice>=len(SHOP_ITEMS):
        return

    name,cost,key=SHOP_ITEMS[choice]

    if state.gold<cost:
        print("Too poor.")
        return

    state.gold-=cost

    if key=="start_pawn":
        state.start_pawn+=1
    elif key=="extra_knight":
        state.extra_knight+=1
    elif key=="bonus_gold":
        state.bonus_gold+=5
    elif key=="heal":
        print("King feels emotionally supported.")

    print("Purchased:",name)


# =============================
# GAME LOOP
# =============================

def play_run(state):

    while True:
        print(f"\n=== FLOOR {state.floor} ===")
        board=create_board(state)

        while True:
            print_board(board)

            if not king_alive(board,True):
                print("You lost the run.")
                return False

            if not king_alive(board,False):
                reward=10+state.bonus_gold
                print("Victory! +",reward,"gold")
                state.gold+=reward
                state.floor+=1
                shop(state)
                break

            cmd=input("> ").lower().split()

            if not cmd:
                continue

            if cmd[0]=="quit":
                exit()

            if cmd[0]=="stats":
                print(vars(state))
                continue

            if len(cmd)==3 and cmd[0]=="move":
                try:
                    r,c=parse_square(cmd[1])
                    tr,tc=parse_square(cmd[2])
                except:
                    print("bad input")
                    continue

                if (tr,tc) in legal_moves(board,r,c):
                    board[tr][tc]=board[r][c]
                    board[r][c]="."
                    ai_move(board)
                else:
                    print("illegal")


# =============================
# MAIN
# =============================

def main():
    state=RunState()

    while True:
        alive=play_run(state)
        print("\nRun ended. Resetting world.")
        state.reset()


if __name__=="__main__":
    main()
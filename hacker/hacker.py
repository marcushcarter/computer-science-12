import time, os, subprocess, random, msvcrt

# ===================== Renderer =====================
class Renderer:
    def __init__(self, w, h):
        self.width = w
        self.height = h
        self.screen = [[" " for _ in range(w)] for _ in range(h)]

    def clear(self, bg=40):
        for y in range(self.height):
            for x in range(self.width):
                self.screen[y][x] = (" ", 37, bg)

    def drawW(self, x, y, text, fg=37, bg=40):
        for i, ch in enumerate(text):
            if 0 <= x + i < self.width and 0 <= y < self.height:
                self.screen[y][x + i] = (ch, fg, bg)

    def drawH(self, x, y, text, fg=37, bg=40):
        for i, ch in enumerate(text):
            if 0 <= x < self.width and 0 <= y + i < self.height:
                self.screen[y + i][x] = (ch, fg, bg)

    def render(self):
        print("\033[H", end="")
        for row in self.screen:
            line = ""
            for ch, fg, bg in row:
                line += f"\033[{fg};{bg}m{ch}\033[0m"
            print(line)

    def border(self, text="#", fg=37, bg=40):
        self.drawW(0, 0, text * self.width, fg, bg)
        self.drawW(0, self.height - 1, text * self.width, fg, bg)
        self.drawH(0, 1, text * (self.height - 2), fg, bg)
        self.drawH(self.width - 1, 1, text * (self.height - 2), fg, bg)

# ===================== Game Classes =====================
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 20
        self.attack = 5

class Monster:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.hp = random.randint(5, 15)
        self.attack = random.randint(1, 4)

# ===================== Game Setup =====================
renderer = Renderer(50, 20)
player = Player(25, 10)
monsters = [Monster("Slime", random.randint(1, 48), random.randint(1, 18)) for _ in range(5)]

running = True
frame_speed = 0.05

def clear_terminal():
    command = "cls" if os.name == "nt" else "clear"
    subprocess.run(command, shell=True)
    print("\033[2J\033[H", end="")

# ===================== Main Loop =====================
clear_terminal()
while running:
    # Input
    if msvcrt.kbhit():
        key = msvcrt.getch()
        if key == b'q':
            running = False
        elif key == b'w' and player.y > 1:
            player.y -= 1
        elif key == b's' and player.y < renderer.height - 2:
            player.y += 1
        elif key == b'a' and player.x > 1:
            player.x -= 1
        elif key == b'd' and player.x < renderer.width - 2:
            player.x += 1

    # Collision check & combat
    for monster in monsters:
        if monster.x == player.x and monster.y == player.y:
            monster.hp -= player.attack
            player.hp -= monster.attack
            print(f"FIGHT! You hit {monster.name} (-{player.attack} HP).")
            print(f"{monster.name} hits you (-{monster.attack} HP).")
            time.sleep(0.3)
            if monster.hp <= 0:
                monsters.remove(monster)
                print(f"{monster.name} is defeated!")
                time.sleep(0.3)

    # Render
    renderer.clear(bg=40)
    renderer.border("#")
    renderer.drawW(player.x, player.y, "@", fg=33)  # player
    for monster in monsters:
        renderer.drawW(monster.x, monster.y, "M", fg=31)  # monster

    # HUD
    renderer.drawW(2, 0, f"HP: {player.hp}")
    renderer.drawW(15, 0, f"Monsters left: {len(monsters)}")

    renderer.render()
    time.sleep(frame_speed)

    if player.hp <= 0:
        print("\nYou fainted! Game Over.")
        break
    if not monsters:
        print("\nAll monsters defeated! Victory!")
        break
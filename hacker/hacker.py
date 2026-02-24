import time, subprocess, os

running = True
frame_speed = 0.01

class Renderer:
    def __init__(self, w, h):
        self.width = w
        self.height = h
        self.screen = [[" " for _ in range(w)] for _ in range(h)]

    def render(self):
        print("\033[H", end="")
        for row in self.screen:
            print("".join(row))

    def drawW(self, x, y, text):
        for i, ch in enumerate(text): # for the number of chars in the text string (the current char is visible)
            if 0 <= x + i < self.width and 0 <= y < self.height:
                self.screen[y][x + i] = ch

    def drawH(self, x, y, text):
        for i, ch in enumerate(text):
            if 0 <= x + i < self.width and 0 <= y < self.height:
                self.screen[y + i][x] = ch

    def clear(self):
        for y in range(self.height):
            for x in range(self.width):
                self.screen[y][x] = "#"

renderer = Renderer(40, 15)

command = "cls" if os.name == "nt" else "clear"
subprocess.run(command, shell=True)
print("\033[2J\033[H", end="")

previous_time = time.perf_counter()

while running:
    # dt
    current_time = time.perf_counter()
    dt = current_time - previous_time
    previous_time = time.perf_counter()

    # Update

    # Render

    renderer.clear()
    
    renderer.drawW(0, 0, f"dt : {dt:.4f}")
    # renderer.drawW(2, 2, "2345")
    # renderer.drawH(1, 1, "1281u401u02")
    
    # command = "cls" if os.name == "nt" else "clear"
    # subprocess.run(command, shell=True)
    renderer.render()
    time.sleep(frame_speed)
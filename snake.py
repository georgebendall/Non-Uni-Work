import tkinter
import random

ROWS = 25
COLS = 25
TILE_SIZE = 25

WindowWith = TILE_SIZE * COLS
WindowHeight = TILE_SIZE * ROWS

# Default speed (will be overwritten by difficulty)
SPEED_MS = 80  # lower = faster


class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y


# main game window
window = tkinter.Tk()
window.title("Snake")
window.resizable(False, False)

canvas = tkinter.Canvas(
    window,
    width=WindowWith,
    height=WindowHeight,
    bg="black",
    borderwidth=0,
    highlightthickness=0
)
canvas.pack()
window.update()

# centralize the window on the screen
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
window_width = window.winfo_width()
window_height = window.winfo_height()

window_x = int((screen_width / 2) - (window_width / 2))
window_y = int((screen_height / 2) - (window_height / 2))
window.geometry(f"{WindowWith}x{WindowHeight}+{window_x}+{window_y}")

# ---- Game state ----
snake_head = Tile(5 * TILE_SIZE, 5 * TILE_SIZE)
snake_body = []

velocity_x = 0
velocity_y = 0

score = 0
game_over = False

# MENU / SETTINGS
in_menu = True
selected_difficulty = None
food_count = 1  # will be set from menu
foods = []      # list[Tile]

DIFFICULTIES = {
    "1": ("Easy", 120),
    "2": ("Normal", 80),
    "3": ("Hard", 55),
    "4": ("Insane", 35),
}

FOOD_OPTIONS = {
    "f": 1,
    "g": 2,
    "h": 3,
}


def occupied_positions():
    occ = {(snake_head.x, snake_head.y)}
    for seg in snake_body:
        occ.add((seg.x, seg.y))
    for f in foods:
        occ.add((f.x, f.y))
    return occ


def spawn_food_one():
    """Spawn one food on an empty tile (not on snake head/body/other foods)."""
    occ = occupied_positions()

    while True:
        x = random.randint(0, COLS - 1) * TILE_SIZE
        y = random.randint(0, ROWS - 1) * TILE_SIZE
        if (x, y) not in occ:
            return Tile(x, y)


def spawn_foods(n):
    """Spawn n foods, all on empty distinct tiles."""
    global foods
    foods = []
    for _ in range(n):
        foods.append(spawn_food_one())


def reset_game():
    global snake_head, snake_body, velocity_x, velocity_y, score, game_over
    snake_head = Tile(5 * TILE_SIZE, 5 * TILE_SIZE)
    snake_body = []
    velocity_x = 0
    velocity_y = 0
    score = 0
    game_over = False
    spawn_foods(food_count)
    game_loop()


def draw_menu():
    canvas.delete("all")
    canvas.create_text(
        WindowWith // 2, 80,
        fill="white",
        text="SNAKE",
        font=("Arial", 44, "bold")
    )
    canvas.create_text(
        WindowWith // 2, 180,
        fill="white",
        text="Choose difficulty:\n"
             "1 = Easy\n2 = Normal\n3 = Hard\n4 = Insane",
        font=("Arial", 18),
        justify="center"
    )
    canvas.create_text(
        WindowWith // 2, 360,
        fill="white",
        text="Choose number of foods:\n"
             "F = 1 food\nG = 2 foods\nH = 3 foods",
        font=("Arial", 18),
        justify="center"
    )
    canvas.create_text(
        WindowWith // 2, 520,
        fill="white",
        text="Tip: Pick BOTH, then press Enter to start",
        font=("Arial", 16),
        justify="center"
    )

    diff_text = selected_difficulty if selected_difficulty else "None"
    canvas.create_text(
        WindowWith // 2, 610,
        fill="white",
        text=f"Selected: difficulty={diff_text}, foods={food_count}",
        font=("Arial", 16),
        justify="center"
    )


def draw():
    canvas.delete("all")

    # draw foods
    for f in foods:
        canvas.create_rectangle(
            f.x, f.y,
            f.x + TILE_SIZE, f.y + TILE_SIZE,
            fill="red", outline=""
        )

    # draw snake body
    for seg in snake_body:
        canvas.create_rectangle(
            seg.x, seg.y,
            seg.x + TILE_SIZE, seg.y + TILE_SIZE,
            fill="green", outline=""
        )

    # draw snake head
    canvas.create_rectangle(
        snake_head.x, snake_head.y,
        snake_head.x + TILE_SIZE, snake_head.y + TILE_SIZE,
        fill="lime green", outline=""
    )

    # draw score
    canvas.create_text(
        10, 10,
        anchor="nw",
        fill="white",
        text=f"Score: {score}",
        font=("Arial", 16)
    )

    if game_over:
        canvas.create_text(
            WindowWith // 2, WindowHeight // 2,
            fill="white",
            text="GAME OVER\nPress R to restart\nPress M for menu",
            font=("Arial", 26),
            justify="center"
        )


def change_direction(event):
    global velocity_x, velocity_y, game_over, in_menu, SPEED_MS
    global selected_difficulty, food_count

    key = event.keysym.lower()

    # ----- MENU CONTROLS -----
    if in_menu:
        # difficulty selection 1-4
        if key in DIFFICULTIES:
            name, spd = DIFFICULTIES[key]
            selected_difficulty = name
            SPEED_MS = spd
            draw_menu()
            return

        # food count selection f/g/h
        if key in FOOD_OPTIONS:
            food_count = FOOD_OPTIONS[key]
            draw_menu()
            return

        # start game
        if key == "return":
            # allow starting even if difficulty not chosen; it will use current SPEED_MS
            in_menu = False
            reset_game()
            return

        return  # ignore movement keys while in menu

    # ----- IN-GAME CONTROLS -----
    if game_over:
        if key == "r":
            reset_game()
            return
        if key == "m":
            in_menu = True
            draw_menu()
            return

    # Prevent reversing directly into yourself
    if event.keysym == "Up" and velocity_y != TILE_SIZE:
        velocity_x = 0
        velocity_y = -TILE_SIZE
    elif event.keysym == "Down" and velocity_y != -TILE_SIZE:
        velocity_x = 0
        velocity_y = TILE_SIZE
    elif event.keysym == "Left" and velocity_x != TILE_SIZE:
        velocity_x = -TILE_SIZE
        velocity_y = 0
    elif event.keysym == "Right" and velocity_x != -TILE_SIZE:
        velocity_x = TILE_SIZE
        velocity_y = 0


def game_loop():
    global snake_head, snake_body, score, game_over

    if in_menu:
        draw_menu()
        return

    if game_over:
        draw()
        return

    # If not moving yet, just draw and schedule next tick
    if velocity_x == 0 and velocity_y == 0:
        draw()
        window.after(SPEED_MS, game_loop)
        return

    # 1) Move body: new first segment becomes the old head position
    snake_body.insert(0, Tile(snake_head.x, snake_head.y))

    # 2) Move head
    snake_head.x += velocity_x
    snake_head.y += velocity_y

    # 3) Wall collision
    if (snake_head.x < 0 or snake_head.x >= WindowWith or
            snake_head.y < 0 or snake_head.y >= WindowHeight):
        game_over = True
        draw()
        return

    # 4) Self collision
    head_pos = (snake_head.x, snake_head.y)
    for seg in snake_body:
        if (seg.x, seg.y) == head_pos:
            game_over = True
            draw()
            return

    # 5) Food collision: check against ALL foods
    ate_index = None
    for i, f in enumerate(foods):
        if snake_head.x == f.x and snake_head.y == f.y:
            ate_index = i
            break

    if ate_index is not None:
        score += 1
        # replace the eaten food with a new one elsewhere
        foods.pop(ate_index)
        foods.append(spawn_food_one())
        # Do NOT pop tail: snake grows by 1
    else:
        # Not eating: keep length constant by removing tail
        snake_body.pop()

    # 6) Draw and schedule next cycle
    draw()
    window.after(SPEED_MS, game_loop)


window.bind("<KeyRelease>", change_direction)

# start in menu
draw_menu()
window.mainloop()
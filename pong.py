import tkinter
import random

# -----------------------------
# Config
# -----------------------------
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
FPS_MS = 16  # ~60 FPS

PADDLE_WIDTH = 18
PADDLE_HEIGHT = 110
PADDLE_SPEED = 12

BALL_SIZE = 18
BALL_SPEED_X = 6
BALL_SPEED_Y = 4

WINNING_SCORE = 7

BG_COLOR = "black"
FG_COLOR = "white"
LEFT_PADDLE_COLOR = "cyan"
RIGHT_PADDLE_COLOR = "orange"
BALL_COLOR = "white"


class Paddle:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    @property
    def top(self):
        return self.y

    @property
    def bottom(self):
        return self.y + self.height

    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + self.width

    def move_up(self):
        self.y -= PADDLE_SPEED
        if self.y < 0:
            self.y = 0

    def move_down(self):
        self.y += PADDLE_SPEED
        if self.y + self.height > WINDOW_HEIGHT:
            self.y = WINDOW_HEIGHT - self.height


class Ball:
    def __init__(self, x, y, size, color):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.vx = 0
        self.vy = 0

    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + self.size

    @property
    def top(self):
        return self.y

    @property
    def bottom(self):
        return self.y + self.size

    @property
    def center_y(self):
        return self.y + self.size / 2

    def reset(self, direction=None):
        self.x = WINDOW_WIDTH // 2 - self.size // 2
        self.y = WINDOW_HEIGHT // 2 - self.size // 2

        if direction is None:
            direction = random.choice([-1, 1])

        self.vx = BALL_SPEED_X * direction
        self.vy = random.choice([-BALL_SPEED_Y, BALL_SPEED_Y])


# -----------------------------
# Window / canvas
# -----------------------------
window = tkinter.Tk()
window.title("Pong")
window.resizable(False, False)

canvas = tkinter.Canvas(
    window,
    width=WINDOW_WIDTH,
    height=WINDOW_HEIGHT,
    bg=BG_COLOR,
    highlightthickness=0
)
canvas.pack()
window.update()

# Center the window
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
window_x = int((screen_width / 2) - (WINDOW_WIDTH / 2))
window_y = int((screen_height / 2) - (WINDOW_HEIGHT / 2))
window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{window_x}+{window_y}")


# -----------------------------
# Game state
# -----------------------------
left_paddle = Paddle(
    40,
    WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2,
    PADDLE_WIDTH,
    PADDLE_HEIGHT,
    LEFT_PADDLE_COLOR
)

right_paddle = Paddle(
    WINDOW_WIDTH - 40 - PADDLE_WIDTH,
    WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2,
    PADDLE_WIDTH,
    PADDLE_HEIGHT,
    RIGHT_PADDLE_COLOR
)

ball = Ball(
    WINDOW_WIDTH // 2 - BALL_SIZE // 2,
    WINDOW_HEIGHT // 2 - BALL_SIZE // 2,
    BALL_SIZE,
    BALL_COLOR
)
ball.reset()

left_score = 0
right_score = 0
game_over = False

# held keys
keys_pressed = set()


# -----------------------------
# Helpers
# -----------------------------
def reset_game():
    global left_score, right_score, game_over
    left_score = 0
    right_score = 0
    game_over = False

    left_paddle.y = WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2
    right_paddle.y = WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2
    ball.reset()


def rects_overlap(a_left, a_top, a_right, a_bottom, b_left, b_top, b_right, b_bottom):
    return (
        a_right > b_left and
        a_left < b_right and
        a_bottom > b_top and
        a_top < b_bottom
    )


def handle_input():
    if game_over:
        return

    # Left paddle: W / S
    if "w" in keys_pressed:
        left_paddle.move_up()
    if "s" in keys_pressed:
        left_paddle.move_down()

    # Right paddle: Up / Down
    if "Up" in keys_pressed:
        right_paddle.move_up()
    if "Down" in keys_pressed:
        right_paddle.move_down()


def update_ball():
    global left_score, right_score, game_over

    if game_over:
        return

    ball.x += ball.vx
    ball.y += ball.vy

    # Bounce off top/bottom walls
    if ball.top <= 0:
        ball.y = 0
        ball.vy *= -1
    elif ball.bottom >= WINDOW_HEIGHT:
        ball.y = WINDOW_HEIGHT - ball.size
        ball.vy *= -1

    # Paddle collision: left paddle
    if rects_overlap(
        ball.left, ball.top, ball.right, ball.bottom,
        left_paddle.left, left_paddle.top, left_paddle.right, left_paddle.bottom
    ) and ball.vx < 0:
        ball.x = left_paddle.right
        ball.vx *= -1

        # Add angle depending on where ball hits paddle
        offset = (ball.center_y - (left_paddle.y + left_paddle.height / 2)) / (left_paddle.height / 2)
        ball.vy = int(offset * 7)
        if ball.vy == 0:
            ball.vy = random.choice([-2, 2])

    # Paddle collision: right paddle
    if rects_overlap(
        ball.left, ball.top, ball.right, ball.bottom,
        right_paddle.left, right_paddle.top, right_paddle.right, right_paddle.bottom
    ) and ball.vx > 0:
        ball.x = right_paddle.left - ball.size
        ball.vx *= -1

        offset = (ball.center_y - (right_paddle.y + right_paddle.height / 2)) / (right_paddle.height / 2)
        ball.vy = int(offset * 7)
        if ball.vy == 0:
            ball.vy = random.choice([-2, 2])

    # Score
    if ball.right < 0:
        right_score += 1
        if right_score >= WINNING_SCORE:
            game_over = True
        else:
            ball.reset(direction=1)

    elif ball.left > WINDOW_WIDTH:
        left_score += 1
        if left_score >= WINNING_SCORE:
            game_over = True
        else:
            ball.reset(direction=-1)


def draw():
    canvas.delete("all")

    # center dashed line
    for y in range(0, WINDOW_HEIGHT, 30):
        canvas.create_rectangle(
            WINDOW_WIDTH // 2 - 3, y,
            WINDOW_WIDTH // 2 + 3, y + 18,
            fill="gray25", outline=""
        )

    # paddles
    canvas.create_rectangle(
        left_paddle.x, left_paddle.y,
        left_paddle.x + left_paddle.width,
        left_paddle.y + left_paddle.height,
        fill=left_paddle.color,
        outline=""
    )
    canvas.create_rectangle(
        right_paddle.x, right_paddle.y,
        right_paddle.x + right_paddle.width,
        right_paddle.y + right_paddle.height,
        fill=right_paddle.color,
        outline=""
    )

    # ball
    canvas.create_oval(
        ball.x, ball.y,
        ball.x + ball.size, ball.y + ball.size,
        fill=ball.color,
        outline=""
    )

    # scores
    canvas.create_text(
        WINDOW_WIDTH * 0.25, 50,
        text=str(left_score),
        fill=FG_COLOR,
        font=("Arial", 36, "bold")
    )
    canvas.create_text(
        WINDOW_WIDTH * 0.75, 50,
        text=str(right_score),
        fill=FG_COLOR,
        font=("Arial", 36, "bold")
    )

    # controls hint
    canvas.create_text(
        WINDOW_WIDTH // 2, WINDOW_HEIGHT - 20,
        text="Left: W/S    Right: ↑/↓    Restart: R",
        fill="gray70",
        font=("Arial", 12)
    )

    if game_over:
        winner = "Left Player Wins!" if left_score > right_score else "Right Player Wins!"
        canvas.create_text(
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 - 20,
            text=winner,
            fill=FG_COLOR,
            font=("Arial", 28, "bold")
        )
        canvas.create_text(
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 + 25,
            text="Press R to restart",
            fill=FG_COLOR,
            font=("Arial", 18)
        )


def game_loop():
    handle_input()
    update_ball()
    draw()
    window.after(FPS_MS, game_loop)


# -----------------------------
# Input
# -----------------------------
def on_key_press(event):
    keys_pressed.add(event.keysym)

    if event.keysym.lower() == "r":
        reset_game()


def on_key_release(event):
    if event.keysym in keys_pressed:
        keys_pressed.remove(event.keysym)


window.bind("<KeyPress>", on_key_press)
window.bind("<KeyRelease>", on_key_release)

# -----------------------------
# Start
# -----------------------------
game_loop()
window.mainloop()
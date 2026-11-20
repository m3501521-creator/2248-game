
import pygame
import random
import math
import struct

pygame.init()

# Fullscreen
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
W, H = screen.get_size()
pygame.display.set_caption("2248")

clock = pygame.time.Clock()

# Colors
BG = (20, 24, 38)
WHITE = (245, 245, 255)
GRAY = (110, 120, 145)
GREEN = (60, 210, 140)
YELLOW = (255, 205, 70)

# Board
ROWS = 8
COLS = 5
GAP = 5
MARGIN = 12

cell_w = (W - 2 * MARGIN - GAP * (COLS - 1)) // COLS
cell_h = min(
    int(cell_w * 0.78),
    (H - 240 - GAP * (ROWS - 1)) // ROWS
)

board_w = COLS * cell_w + (COLS - 1) * GAP
board_h = ROWS * cell_h + (ROWS - 1) * GAP

board_x = (W - board_w) // 2
board_y = max(120, (H - board_h) // 2)

# Fonts
font_size = max(18, min(cell_h // 2, 42))
font = pygame.font.Font(None, font_size)
title_font = pygame.font.Font(None, max(40, W // 10))
small_font = pygame.font.Font(None, max(24, W // 18))

# Sound system
keyboard_sound = None
win_sound = None

def make_sound(frequency, duration, volume=0.25):
    sample_rate = 22050
    samples = bytearray()

    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        fade = min(1, i / 200, (duration * sample_rate - i) / 500)
        value = int(
            32767 * volume * fade *
            math.sin(2 * math.pi * frequency * t)
        )
        samples.extend(struct.pack("<h", value))

    return pygame.mixer.Sound(buffer=bytes(samples))

try:
    pygame.mixer.init(
        frequency=22050,
        size=-16,
        channels=1
    )
    keyboard_sound = make_sound(900, 0.045, 0.16)

    # Two-tone victory sound
    win_sound = make_sound(880, 0.22, 0.25)
except Exception:
    pass

# Numbers and colors
def tile_color(value):
    colors = {
        2: (65, 105, 180),
        4: (65, 145, 205),
        8: (50, 175, 170),
        16: (55, 185, 125),
        32: (125, 185, 75),
        64: (205, 175, 60),
        128: (220, 135, 55),
        256: (220, 100, 75),
        512: (190, 85, 145),
        1024: (135, 90, 190),
        2048: (230, 175, 45)
    }
    return colors.get(value, (100, 90, 180))


def random_tile():
    return random.choice([2, 2, 2, 2, 4, 4, 8])


def new_board():
    return [
        [random_tile() for _ in range(COLS)]
        for _ in range(ROWS)
    ]


board = new_board()
score = 0
selected = []
dragging = False
won = False
win_sound_played = False


def get_cell(pos):
    x, y = pos
    col = (x - board_x) // (cell_w + GAP)
    row = (y - board_y) // (cell_h + GAP)

    if 0 <= row < ROWS and 0 <= col < COLS:
        return int(row), int(col)

    return None


def adjacent(a, b):
    return (
        max(abs(a[0] - b[0]), abs(a[1] - b[1])) == 1
    )


def draw_text(text, fnt, color, x, y):
    image = fnt.render(str(text), True, color)
    rect = image.get_rect(center=(x, y))
    screen.blit(image, rect)


def draw():
    screen.fill(BG)

    draw_text("2248", title_font, WHITE, W // 2, 48)
    draw_text(
        "SCORE: " + str(score),
        small_font,
        YELLOW,
        W // 2,
        95
    )

    for r in range(ROWS):
        for c in range(COLS):
            value = board[r][c]

            x = board_x + c * (cell_w + GAP)
            y = board_y + r * (cell_h + GAP)

            rect = pygame.Rect(x, y, cell_w, cell_h)

            pygame.draw.rect(
                screen,
                tile_color(value),
                rect,
                border_radius=10
            )

            if (r, c) in selected:
                pygame.draw.rect(
                    screen,
                    WHITE,
                    rect,
                    width=4,
                    border_radius=10
                )

            draw_text(
                value,
                font,
                WHITE,
                x + cell_w // 2,
                y + cell_h // 2
            )

    draw_text(
        "DRAG TO CONNECT MATCHING NUMBERS",
        small_font,
        GRAY,
        W // 2,
        H - 55
    )

    if won:
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        screen.blit(overlay, (0, 0))

        draw_text("YOU WIN!", title_font, YELLOW, W // 2, H // 2 - 35)
        draw_text(
            "SCORE: " + str(score),
            small_font,
            WHITE,
            W // 2,
            H // 2 + 25
        )
        draw_text(
            "TAP TO PLAY AGAIN",
            small_font,
            GREEN,
            W // 2,
            H // 2 + 85
        )

    pygame.display.flip()


def finish_selection():
    global score, selected, board, won, win_sound_played

    if len(selected) >= 2:
        first = selected[0]
        value = board[first[0]][first[1]]

        result = value * (2 ** (len(selected) - 1))

        # Remove connected tiles
        for r, c in selected:
            board[r][c] = 0

        # Put result in the last selected cell
        r, c = selected[-1]
        board[r][c] = result

        score += result

        # Fill empty cells
        for r in range(ROWS):
            for c in range(COLS):
                if board[r][c] == 0:
                    board[r][c] = random_tile()

        if score >= 2248 and not won:
            won = True

            if win_sound and not win_sound_played:
                win_sound.play()
                win_sound_played = True

    selected.clear()


running = True

while running:
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if won:
                board = new_board()
                score = 0
                won = False
                win_sound_played = False
                selected.clear()
                continue

            cell = get_cell(event.pos)

            if cell:
                r, c = cell
                selected = [cell]
                dragging = True

                if keyboard_sound:
                    keyboard_sound.play()

        elif event.type == pygame.MOUSEMOTION and dragging:
            cell = get_cell(event.pos)

            if cell and cell not in selected:
                r, c = cell

                if (
                    board[r][c] == board[selected[0][0]][selected[0][1]]
                    and adjacent(selected[-1], cell)
                ):
                    selected.append(cell)

                    if keyboard_sound:
                        keyboard_sound.play()

        elif event.type == pygame.MOUSEBUTTONUP:
            if dragging:
                finish_selection()
                dragging = False

    draw()
    clock.tick(60)

pygame.quit()

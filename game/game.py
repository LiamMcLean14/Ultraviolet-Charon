import pygame
import random

# -----------------------------
# Initialization
# -----------------------------
pygame.init()

WIDTH = 600
HEIGHT = 800
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Basic Rhythm Game")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 32)
small_font = pygame.font.SysFont("Arial", 24)

# -----------------------------
# Colors
# -----------------------------
BLACK = (20, 20, 20)
WHITE = (255, 255, 255)
GRAY = (60, 60, 60)
GREEN = (50, 220, 100)
RED = (220, 70, 70)
BLUE = (80, 140, 255)
YELLOW = (255, 220, 50)

LANE_COLORS = [RED, YELLOW, GREEN, BLUE]

# -----------------------------
# Lanes
# -----------------------------
LANE_COUNT = 4
LANE_WIDTH = WIDTH // LANE_COUNT

KEYS = [pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k]
KEY_LABELS = ["D", "F", "J", "K"]

# -----------------------------
# Gameplay settings
# -----------------------------
NOTE_SPEED = 6
NOTE_WIDTH = LANE_WIDTH - 20
NOTE_HEIGHT = 25
HIT_LINE_Y = HEIGHT - 120
HIT_WINDOW = 40

score = 0
combo = 0
max_combo = 0
misses = 0

# -----------------------------
# Note class
# -----------------------------
class Note:
    def __init__(self, lane, y):
        self.lane = lane
        self.x = lane * LANE_WIDTH + 10
        self.y = y
        self.hit = False

    def update(self):
        self.y += NOTE_SPEED

    def draw(self, surface):
        pygame.draw.rect(
            surface,
            LANE_COLORS[self.lane],
            (self.x, self.y, NOTE_WIDTH, NOTE_HEIGHT),
            border_radius=8,
        )

    def is_hittable(self):
        return abs(self.y - HIT_LINE_Y) <= HIT_WINDOW


# -----------------------------
# Generate notes
# -----------------------------
notes = []
spawn_timer = 0
spawn_interval = 40
song_length = 1200
frames_elapsed = 0

# -----------------------------
# Main loop
# -----------------------------
running = True

while running:
    clock.tick(FPS)
    frames_elapsed += 1

    # -------------------------
    # Spawn notes
    # -------------------------
    spawn_timer += 1

    if spawn_timer >= spawn_interval and frames_elapsed < song_length:
        lane = random.randint(0, 3)
        notes.append(Note(lane, -NOTE_HEIGHT))
        spawn_timer = 0

    # -------------------------
    # Events
    # -------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key in KEYS:
                lane = KEYS.index(event.key)

                hit_note = None

                for note in notes:
                    if note.lane == lane and note.is_hittable():
                        hit_note = note
                        break

                if hit_note:
                    notes.remove(hit_note)
                    score += 100
                    combo += 1
                    max_combo = max(max_combo, combo)
                else:
                    combo = 0
                    misses += 1

    # -------------------------
    # Update notes
    # -------------------------
    for note in notes[:]:
        note.update()

        # Missed note
        if note.y > HEIGHT:
            notes.remove(note)
            combo = 0
            misses += 1

    # -------------------------
    # Drawing
    # -------------------------
    screen.fill(BLACK)

    # Draw lanes
    for i in range(LANE_COUNT):
        x = i * LANE_WIDTH

        pygame.draw.rect(
            screen,
            GRAY,
            (x, 0, LANE_WIDTH, HEIGHT),
            width=2,
        )

        # Key labels
        label = font.render(KEY_LABELS[i], True, WHITE)
        label_rect = label.get_rect(center=(x + LANE_WIDTH // 2, HEIGHT - 50))
        screen.blit(label, label_rect)

    # Draw hit line
    pygame.draw.line(
        screen,
        WHITE,
        (0, HIT_LINE_Y + NOTE_HEIGHT // 2),
        (WIDTH, HIT_LINE_Y + NOTE_HEIGHT // 2),
        4,
    )

    # Draw notes
    for note in notes:
        note.draw(screen)

    # Draw score
    score_text = small_font.render(f"Score: {score}", True, WHITE)
    combo_text = small_font.render(f"Combo: {combo}", True, WHITE)
    miss_text = small_font.render(f"Misses: {misses}", True, WHITE)

    screen.blit(score_text, (20, 20))
    screen.blit(combo_text, (20, 55))
    screen.blit(miss_text, (20, 90))

    # End screen
    if frames_elapsed >= song_length and len(notes) == 0:
        end_text = font.render("Song Complete!", True, WHITE)
        combo_end = small_font.render(f"Max Combo: {max_combo}", True, WHITE)

        screen.blit(end_text, (WIDTH // 2 - 120, HEIGHT // 2 - 50))
        screen.blit(combo_end, (WIDTH // 2 - 100, HEIGHT // 2))

    pygame.display.flip()

pygame.quit()

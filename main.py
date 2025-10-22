import pygame
import sys
import random
from PIL import Image

# --- Initialize ---
pygame.init()
WIDTH, HEIGHT = 800, 400
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jungle Runner")

clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24)

# --- Game Variables ---
gravity = 0.8
game_speed = 6
score = 0
ground_height = 64

# --- Load GIF Frames using Pillow ---
def load_gif_frames(path):
    frames = []
    gif = Image.open(path)
    for frame in range(gif.n_frames):
        gif.seek(frame)
        frame_image = gif.convert("RGBA")
        mode = frame_image.mode
        size = frame_image.size
        data = frame_image.tobytes()
        surface = pygame.image.fromstring(data, size, mode)
        frames.append(surface)
    return frames

player_frames = load_gif_frames("characterrun.gif")
if len(player_frames) == 0:
    raise Exception("No frames were loaded from characterrun.gif!")

current_frame = 0
frame_delay = 5
frame_counter = 0

player_rect = player_frames[0].get_rect(midbottom=(100, HEIGHT - ground_height))
player_y_velocity = 0
is_jumping = False

# --- Load jungle tileset ---
tileset = pygame.image.load("jungle tileset.png").convert_alpha()

# Choose one visible “ground-looking” section — adjust these numbers to your liking
# (for example, (0, 96, 128, 32)) means: start x=0, y=96, width=128, height=32
# you can tweak these if the selected area doesn’t look right
ground_crop = tileset.subsurface((0, 96, 128, 32))

# Stretch it to full width
ground_surface = pygame.transform.scale(ground_crop, (WIDTH, ground_height))

# --- Obstacle setup ---
obstacle_width, obstacle_height = 40, 60
obstacle_x = WIDTH
obstacle_y = HEIGHT - ground_height - obstacle_height

# --- Game Loop ---
while True:
    clock.tick(60)
    win.fill((135, 206, 235))  # sky blue

    # --- Input ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and not is_jumping:
            if event.key == pygame.K_SPACE:
                is_jumping = True
                player_y_velocity = -15

    # --- Player physics ---
    if is_jumping:
        player_rect.y += player_y_velocity
        player_y_velocity += gravity
        if player_rect.bottom >= HEIGHT - ground_height:
            player_rect.bottom = HEIGHT - ground_height
            is_jumping = False

    # --- Animate Player ---
    frame_counter += 1
    if frame_counter >= frame_delay:
        current_frame = (current_frame + 1) % len(player_frames)
        frame_counter = 0

    # --- Move obstacle ---
    obstacle_x -= game_speed
    if obstacle_x < -obstacle_width:
        obstacle_x = WIDTH + random.randint(300, 800)
        score += 1
        game_speed += 0.2

    # --- Draw ground (single large sprite) ---
    win.blit(ground_surface, (0, HEIGHT - ground_height))

    # --- Draw player ---
    win.blit(player_frames[current_frame], player_rect)

    # --- Draw obstacle ---
    pygame.draw.rect(win, (34, 139, 34), (obstacle_x, obstacle_y, obstacle_width, obstacle_height))

    # --- Collision ---
    obstacle_rect = pygame.Rect(obstacle_x, obstacle_y, obstacle_width, obstacle_height)
    if player_rect.colliderect(obstacle_rect):
        text = font.render("Game Over! Press R to Restart", True, (0, 0, 0))
        win.blit(text, (WIDTH//2 - 160, HEIGHT//2))
        pygame.display.update()

        # Wait for restart
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    player_rect.bottom = HEIGHT - ground_height
                    obstacle_x = WIDTH
                    score = 0
                    game_speed = 6
                    waiting = False

    # --- Score ---
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    win.blit(score_text, (10, 10))

    pygame.display.update()

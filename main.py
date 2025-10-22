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
ground_height = 100  # Ground height

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

# --- Player ---
player_rect = player_frames[0].get_rect(midbottom=(120, HEIGHT - ground_height))
player_y_velocity = 0
is_jumping = False

# --- Gradient ground drawing ---
segment_width = WIDTH
def draw_gradient_ground(surface, x, y, width, height):
    top_color = (76, 187, 23)    # bright green
    mid_color = (166, 123, 75)   # medium brown
    bottom_color = (90, 55, 37)  # dark brown
    for i in range(height):
        if i < height // 5:
            color = [int(top_color[j] * (1 - i/(height//5)) + mid_color[j] * (i/(height//5))) for j in range(3)]
        else:
            ratio = (i - height // 5) / (height - height // 5)
            color = [int(mid_color[j] * (1 - ratio) + bottom_color[j] * ratio) for j in range(3)]
        pygame.draw.line(surface, color, (x, y + i), (x + width, y + i))

ground_segments = [
    {"x": 0, "y": HEIGHT - ground_height},
    {"x": segment_width, "y": HEIGHT - ground_height}
]

# --- Obstacle setup ---
obstacle_width, obstacle_height = 40, 60
obstacle_x = WIDTH
obstacle_y = HEIGHT - ground_height - obstacle_height

# --- Airborne Red Blocks setup ---
airborne_blocks = []
airborne_block_width, airborne_block_height = 40, 40
airborne_min_y = HEIGHT - ground_height - 120
airborne_max_y = HEIGHT - ground_height - 60
airborne_spawn_interval = 150  # frames
airborne_counter = 0
airborne_min_gap = 120         # minimum horizontal gap between airborne blocks

# --- Game Loop ---
while True:
    clock.tick(60)
    win.fill((135, 206, 235))  # sky blue background

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

    # --- Airborne Blocks Logic ---
    airborne_counter += 1
    if airborne_counter >= airborne_spawn_interval:
        last_x = airborne_blocks[-1][0] if airborne_blocks else -airborne_min_gap
        x_pos = max(WIDTH + random.randint(0, 300), last_x + airborne_min_gap)
        y_pos = random.randint(airborne_min_y, airborne_max_y)
        airborne_blocks.append([x_pos, y_pos])
        airborne_counter = 0

    # Move airborne blocks and remove off-screen ones
    for block in airborne_blocks:
        block[0] -= game_speed
    airborne_blocks = [block for block in airborne_blocks if block[0] > -airborne_block_width]

    # --- Scroll ground segments ---
    for seg in ground_segments:
        seg["x"] -= game_speed
        if seg["x"] <= -segment_width:
            seg["x"] = max(gs["x"] for gs in ground_segments) + segment_width

    # --- Draw ground segments ---
    for seg in ground_segments:
        draw_gradient_ground(win, seg["x"], seg["y"], segment_width, ground_height)

    # --- Draw player ---
    win.blit(player_frames[current_frame], player_rect)

    # --- Draw obstacle (ground) ---
    pygame.draw.rect(win, (34, 139, 34), (obstacle_x, obstacle_y, obstacle_width, obstacle_height))
    # --- Draw red airborne blocks ---
    for ab in airborne_blocks:
        pygame.draw.rect(win, (220, 30, 30), (ab[0], ab[1], airborne_block_width, airborne_block_height))

    # --- Collision ---
    obstacle_rect = pygame.Rect(obstacle_x, obstacle_y, obstacle_width, obstacle_height)
    airborne_rects = [pygame.Rect(ab[0], ab[1], airborne_block_width, airborne_block_height) for ab in airborne_blocks]

    collision = False
    if player_rect.colliderect(obstacle_rect):
        collision = True
    for ab_rect in airborne_rects:
        if player_rect.colliderect(ab_rect):
            collision = True
            break

    if collision:
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
                    airborne_blocks = []
                    score = 0
                    game_speed = 6
                    airborne_counter = 0
                    waiting = False

    # --- Score ---
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    win.blit(score_text, (10, 10))

    pygame.display.update()

import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# --- Window setup ---
WIDTH, HEIGHT = 800, 400
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("No WiFi Dinosaur Game")

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GROUND_COLOR = (83, 83, 83)

# --- Game variables ---
gravity = 0.8
game_speed = 5
score = 0

# --- Fonts ---
font = pygame.font.SysFont("arial", 24)

# --- Dino setup ---
dino_width, dino_height = 40, 60
dino_x = 50
dino_y = HEIGHT - dino_height - 40
dino_y_velocity = 0
is_jumping = False

# --- Obstacle setup ---
obstacle_width, obstacle_height = 20, 50
obstacle_x = WIDTH
obstacle_y = HEIGHT - obstacle_height - 40

clock = pygame.time.Clock()

# --- Game loop ---
while True:
    clock.tick(60)
    win.fill(WHITE)

    # Ground
    pygame.draw.rect(win, GROUND_COLOR, (0, HEIGHT - 40, WIDTH, 40))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Jump control
        if event.type == pygame.KEYDOWN and not is_jumping:
            if event.key == pygame.K_SPACE:
                is_jumping = True
                dino_y_velocity = -15

    # Dino physics
    if is_jumping:
        dino_y += dino_y_velocity
        dino_y_velocity += gravity
        if dino_y >= HEIGHT - dino_height - 40:
            dino_y = HEIGHT - dino_height - 40
            is_jumping = False

    # Move obstacle
    obstacle_x -= game_speed
    if obstacle_x < -obstacle_width:
        obstacle_x = WIDTH + random.randint(200, 800)
        score += 1
        game_speed += 0.2  # speed up gradually

    # Draw Dino
    pygame.draw.rect(win, BLACK, (dino_x, dino_y, dino_width, dino_height))

    # Draw obstacle
    pygame.draw.rect(win, BLACK, (obstacle_x, obstacle_y, obstacle_width, obstacle_height))

    # Collision detection
    dino_rect = pygame.Rect(dino_x, dino_y, dino_width, dino_height)
    obstacle_rect = pygame.Rect(obstacle_x, obstacle_y, obstacle_width, obstacle_height)
    if dino_rect.colliderect(obstacle_rect):
        # Game over screen
        text = font.render("Game Over! Press R to Restart", True, BLACK)
        win.blit(text, (WIDTH//2 - 150, HEIGHT//2))
        pygame.display.update()

        # Wait for restart
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    # Reset game
                    obstacle_x = WIDTH
                    dino_y = HEIGHT - dino_height - 40
                    game_speed = 5
                    score = 0
                    waiting = False

    # Draw score
    score_text = font.render(f"Score: {score}", True, BLACK)
    win.blit(score_text, (10, 10))

    # Update display
    pygame.display.update()

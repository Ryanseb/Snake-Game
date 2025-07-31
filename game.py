import pygame
import sys
import random

# Constants
FRAME_SIZE_X, FRAME_SIZE_Y = 720, 480
SNAKE_SIZE = 10
DIFFICULTY = 25

# Initialize pygame
pygame.init()

# Setup game window
pygame.display.set_caption('Snake Eater')
game_window = pygame.display.set_mode((FRAME_SIZE_X, FRAME_SIZE_Y))

# Colors
BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255, 255, 255)
RED = pygame.Color(255, 0, 0)
GREEN = pygame.Color(0, 255, 0)
GOLD = pygame.Color(255, 215, 0)
BROWN = pygame.Color(139, 69, 19)
DARK_GREEN = pygame.Color(0, 200, 0)

# FPS controller
fps_controller = pygame.time.Clock()

# Load high score
try:
    with open("highscore.txt", "r") as f:
        content = f.read().strip()
        high_score = int(content) if content else 0
except (FileNotFoundError, ValueError):
    high_score = 0


def show_score(score, high_score):
    font = pygame.font.SysFont('consolas', 24, bold=True)
    score_surface = font.render(f'Score: {score}', True, GREEN)
    high_score_surface = font.render(f'High Score: {high_score}', True, GOLD)
    game_window.blit(score_surface, (20, 15))
    game_window.blit(high_score_surface, (FRAME_SIZE_X - 200, 15))

def main_game():
    snake_pos = [100, 50]
    snake_body = [[100, 50], [90, 50], [80, 50]]
    food_pos = [random.randrange(1, FRAME_SIZE_X // SNAKE_SIZE) * SNAKE_SIZE,
                random.randrange(1, FRAME_SIZE_Y // SNAKE_SIZE) * SNAKE_SIZE]
    direction = 'RIGHT'
    change_to = direction
    score = 0
    food_spawn = True

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, ord('w')) and direction != 'DOWN':
                    change_to = 'UP'
                elif event.key in (pygame.K_DOWN, ord('s')) and direction != 'UP':
                    change_to = 'DOWN'
                elif event.key in (pygame.K_LEFT, ord('a')) and direction != 'RIGHT':
                    change_to = 'LEFT'
                elif event.key in (pygame.K_RIGHT, ord('d')) and direction != 'LEFT':
                    change_to = 'RIGHT'
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        direction = change_to

        # Move snake
        if direction == 'UP':
            snake_pos[1] -= SNAKE_SIZE
        elif direction == 'DOWN':
            snake_pos[1] += SNAKE_SIZE
        elif direction == 'LEFT':
            snake_pos[0] -= SNAKE_SIZE
        elif direction == 'RIGHT':
            snake_pos[0] += SNAKE_SIZE

        snake_body.insert(0, list(snake_pos))

        if snake_pos == food_pos:
            score += 1
            food_spawn = False
        else:
            snake_body.pop()

        if not food_spawn:
            food_pos = [random.randrange(1, FRAME_SIZE_X // SNAKE_SIZE) * SNAKE_SIZE,
                        random.randrange(1, FRAME_SIZE_Y // SNAKE_SIZE) * SNAKE_SIZE]
            food_spawn = True

        # Fill background
        game_window.fill(BLACK)

        # Draw snake
        for pos in snake_body:
            pygame.draw.rect(game_window, GREEN, pygame.Rect(pos[0], pos[1], SNAKE_SIZE, SNAKE_SIZE), border_radius=3)

        # Draw food (apple with stem and leaf)
        pygame.draw.circle(game_window, RED, (food_pos[0] + 5, food_pos[1] + 5), 5)
        pygame.draw.rect(game_window, BROWN, (food_pos[0] + 4, food_pos[1] - 1, 2, 3))
        pygame.draw.circle(game_window, DARK_GREEN, (food_pos[0] + 7, food_pos[1]), 1)

        # Check collisions with walls
        if (snake_pos[0] < 0 or snake_pos[0] >= FRAME_SIZE_X or
            snake_pos[1] < 0 or snake_pos[1] >= FRAME_SIZE_Y):
            return score

        # Check collisions with itself
        if snake_pos in snake_body[1:]:
            return score

        show_score(score, high_score)

        pygame.display.update()
        fps_controller.tick(DIFFICULTY)

def game_over(score):
    global high_score
    if score > high_score:
        high_score = score
        with open("highscore.txt", "w") as f:
            f.write(str(high_score))

    game_window.fill(BLACK)
    font_large = pygame.font.SysFont('timesnewroman', 90)
    font_medium = pygame.font.SysFont('timesnewroman', 30)
    font_small = pygame.font.SysFont('timesnewroman', 30)

    msg1 = font_large.render('YOU DIED', True, RED)
    msg1_rect = msg1.get_rect(center=(FRAME_SIZE_X / 2, FRAME_SIZE_Y / 4))
    game_window.blit(msg1, msg1_rect)

    score_msg = font_medium.render(f'Score: {score}  High Score: {high_score}', True, RED)
    score_rect = score_msg.get_rect(center=(FRAME_SIZE_X / 2, msg1_rect.bottom + 30))
    game_window.blit(score_msg, score_rect)

    msg2 = font_small.render('Press R to Restart or Q to Quit', True, WHITE)
    msg2_rect = msg2.get_rect(center=(FRAME_SIZE_X / 2, FRAME_SIZE_Y / 1.5))
    game_window.blit(msg2, msg2_rect)

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                elif event.key == pygame.K_q:
                    return False

def run_game():
    while True:
        score = main_game()
        if not game_over(score):
            break

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    run_game()

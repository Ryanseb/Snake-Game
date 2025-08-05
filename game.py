import pygame
import random
import asyncio

FRAME_SIZE_X, FRAME_SIZE_Y = 720, 480
CELL_SIZE = 10
BASE_SPEED = 10


BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255, 255, 255)
RED = pygame.Color(255, 0, 0)
GREEN = pygame.Color(0, 255, 0)
GOLD = pygame.Color(255, 215, 0)
TRAIL_COLOR = pygame.Color(0, 150, 0)
DARK_GREEN = pygame.Color(0, 200, 0)

pygame.init()
pygame.font.init()
pygame.mixer.init()


EAT_SOUND = pygame.mixer.Sound("eat.ogg")
GAME_OVER_SOUND = pygame.mixer.Sound("gameover.ogg")

game_window = pygame.display.set_mode((FRAME_SIZE_X, FRAME_SIZE_Y))
pygame.display.set_caption('Snake Eater 2.0')


class Snake:
    def __init__(self):
        self.position = [100, 50]
        self.body = [[100, 50], [90, 50], [80, 50]]
        self.direction = 'RIGHT'
        self.change_to = 'RIGHT'
        self.trail = []

    def update_direction(self, key):
        if key in (pygame.K_UP, pygame.K_w) and self.direction != 'DOWN':
            self.change_to = 'UP'
        elif key in (pygame.K_DOWN, pygame.K_s) and self.direction != 'UP':
            self.change_to = 'DOWN'
        elif key in (pygame.K_LEFT, pygame.K_a) and self.direction != 'RIGHT':
            self.change_to = 'LEFT'
        elif key in (pygame.K_RIGHT, pygame.K_d) and self.direction != 'LEFT':
            self.change_to = 'RIGHT'

    def move(self):
        self.direction = self.change_to
        if self.direction == 'UP':
            self.position[1] -= CELL_SIZE
        elif self.direction == 'DOWN':
            self.position[1] += CELL_SIZE
        elif self.direction == 'LEFT':
            self.position[0] -= CELL_SIZE
        elif self.direction == 'RIGHT':
            self.position[0] += CELL_SIZE

        self.body.insert(0, list(self.position))
        self.trail.append(list(self.position))
        if len(self.trail) > 15:
            self.trail.pop(0)

    def shrink(self):
        self.body.pop()

    def check_collision(self):
        return (
            self.position[0] < 0 or self.position[0] >= FRAME_SIZE_X or
            self.position[1] < 0 or self.position[1] >= FRAME_SIZE_Y or
            self.position in self.body[1:]
        )

    def draw(self):
        for i, t in enumerate(self.trail):
            fade = max(10, 80 - (len(self.trail) - i) * 5)
            color = pygame.Color(0, fade, 0)
            pygame.draw.circle(game_window, color, (t[0] + CELL_SIZE // 2, t[1] + CELL_SIZE // 2), 2)
        for pos in self.body:
            pygame.draw.rect(game_window, GREEN, pygame.Rect(pos[0], pos[1], CELL_SIZE, CELL_SIZE), border_radius=2)


class Food:
    def __init__(self):
        self.position = self.spawn()
        self.is_gold = False

    def spawn(self):
        return [random.randrange(1, FRAME_SIZE_X // CELL_SIZE) * CELL_SIZE,
                random.randrange(1, FRAME_SIZE_Y // CELL_SIZE) * CELL_SIZE]

    def maybe_spawn_gold(self, score):
        self.is_gold = (random.randint(1, 10) == 1 and score > 0)

    def draw(self):
        if self.is_gold:
            pygame.draw.circle(game_window, GOLD, (self.position[0] + 5, self.position[1] + 5), 6)
            pygame.draw.rect(game_window, (139, 69, 19), (self.position[0] + 4, self.position[1] - 1, 2, 3))
            pygame.draw.circle(game_window, DARK_GREEN, (self.position[0] + 7, self.position[1]), 1)
        else:
            pygame.draw.circle(game_window, RED, (self.position[0] + 5, self.position[1] + 5), 5)
            pygame.draw.rect(game_window, (139, 69, 19), (self.position[0] + 4, self.position[1] - 1, 2, 3))
            pygame.draw.circle(game_window, DARK_GREEN, (self.position[0] + 7, self.position[1]), 1)


def show_score(score, high_score, level):
    font = pygame.font.SysFont('consolas', 24, bold=True)
    score_surface = font.render(f'Score: {score}', True, GREEN)
    high_surface = font.render(f'High Score: {high_score}', True, GOLD)
    level_surface = font.render(f'Level: {level}', True, WHITE)

    game_window.blit(score_surface, (20, 15))
    game_window.blit(high_surface, (FRAME_SIZE_X - 200, 15))

    level_rect = level_surface.get_rect(center=(FRAME_SIZE_X // 2, 27))
    game_window.blit(level_surface, level_rect)


async def main_game(high_score):
    snake = Snake()
    food = Food()
    score = 0
    paused = False
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, high_score
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False, high_score
                elif event.key == pygame.K_p:
                    paused = not paused
                else:
                    snake.update_direction(event.key)

        if paused:
            await asyncio.sleep(0.1)
            continue

        snake.move()

        if snake.position == food.position:
            EAT_SOUND.play()
            score += 3 if food.is_gold else 1
            food = Food()
            food.maybe_spawn_gold(score)
        else:
            snake.shrink()

        if snake.check_collision():
            return score, max(high_score, score)

        game_window.fill(BLACK)
        snake.draw()
        food.draw()

        level = score // 5 + 1
        speed = BASE_SPEED + level * 2

        show_score(score, max(score, high_score), level)
        pygame.display.update()
        clock.tick(speed)
        await asyncio.sleep(0)

    return score, high_score


async def game_over(score, high_score):
    GAME_OVER_SOUND.play() 

    font_large = pygame.font.SysFont('timesnewroman', 90)
    font_medium = pygame.font.SysFont('timesnewroman', 30)

    game_window.fill(BLACK)
    title_surface = font_large.render('YOU DIED', True, RED)
    score_surface = font_medium.render(f'Score: {score}  High Score: {high_score}', True, RED)
    info_surface = font_medium.render('Press R to Restart or Q to Quit', True, WHITE)

    title_rect = title_surface.get_rect(center=(FRAME_SIZE_X // 2, 120))
    score_rect = score_surface.get_rect(center=(FRAME_SIZE_X // 2, 220))
    info_rect = info_surface.get_rect(center=(FRAME_SIZE_X // 2, 320))

    game_window.blit(title_surface, title_rect)
    game_window.blit(score_surface, score_rect)
    game_window.blit(info_surface, info_rect)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                elif event.key == pygame.K_q:
                    return False
        await asyncio.sleep(0.1)


async def run_game():
    high_score = 0
    while True:
        score, high_score = await main_game(high_score)
        again = await game_over(score, high_score)
        if not again:
            break
    pygame.quit()


asyncio.run(run_game())

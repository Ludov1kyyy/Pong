# Pong by @Ludov1kyyyy

import pygame
from sys import exit
from time import perf_counter
from random import choice

pygame.mixer.pre_init(44100, -16, 2, 64)
pygame.init()

WINSIZE = WIDTH, HEIGHT = 854, 480
FONT = pygame.font.Font(None, 30)

BLACK_COLOR = (24, 24, 24)
WHITE_COLOR = (200, 200, 200)

class Text:
    def __init__(self, info, pos):
        win = pygame.display.get_surface()
        info_surf = FONT.render(str(info), True, WHITE_COLOR)
        info_rect = info_surf.get_rect(midbottom = pos)
        pygame.draw.rect(win, BLACK_COLOR, info_rect)
        win.blit(info_surf, info_rect)

class Audio:
    def __init__(self, path):
        self.audio = pygame.mixer.Sound(path)

    def play(self, volume=1):
        self.audio.play()

class Paddle(pygame.sprite.Sprite):
    def __init__(self, pos, type, group):
        super().__init__(group)
        self.type = type
        self.image = pygame.Surface((14, HEIGHT // 5))
        self.image.fill(WHITE_COLOR)
        self.rect = self.image.get_rect(center = pos)
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.move = 0
        self.speed = 320

    def input(self):
        keys = pygame.key.get_pressed()

        if self.type == "one":
            UP = keys[pygame.K_w]
            DOWN = keys[pygame.K_s]
        else:
            UP = keys[pygame.K_UP]
            DOWN = keys[pygame.K_DOWN]

        if UP:
            self.move = -1
        elif DOWN:
            self.move = 1
        else:
            self.move = 0

    def movement(self, dt):
        self.pos.y += self.move * self.speed * dt
        self.rect.y = round(self.pos.y)

    def constraint(self):
        if self.rect.top < 0:
            self.rect.top = 0
            self.pos.y = self.rect.y
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.pos.y = self.rect.y

    def update(self, dt):
        self.input()
        self.movement(dt)
        self.constraint()

class Ball(pygame.sprite.Sprite):
    def __init__(self, group, paddles):
        super().__init__(group)
        self.image = pygame.image.load("graphics/ball.png").convert_alpha()
        self.image.set_colorkey((255, 255, 255))
        self.rect = self.image.get_rect(center = (WIDTH // 2, HEIGHT // 2))
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.move = pygame.math.Vector2(choice((1, -1)), choice((1, -1)))
        self.speed = 360
        self.state = "static"
        self.ball_time = 0
        self.score_one = 0
        self.score_two = 0
        self.paddles = paddles

    def movement(self, dt):
        if self.state == "moving":
            self.pos.x += self.move.x * self.speed * dt
            self.rect.x = round(self.pos.x)
            self.pos.y += self.move.y * self.speed * dt
            self.rect.y = round(self.pos.y)

    def constraint(self):
        if self.rect.top < 0 or self.rect.bottom > HEIGHT:
            Audio("sfx/wall.mp3").play()
            self.move.y *= -1
        if self.rect.left < 0:
            Audio("sfx/score.mp3").play()
            self.reset_ball()
            self.score_two += 1
        if self.rect.right > WIDTH:
            Audio("sfx/score.mp3").play()
            self.reset_ball()
            self.score_one += 1

    def reset_ball(self):
        self.ball_time = pygame.time.get_ticks()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.move = pygame.math.Vector2(choice((1, -1)), choice((1, -1)))
        self.state = "static"

    def draw_timer(self):
        current_time = pygame.time.get_ticks()

        if (current_time - self.ball_time) <= 1000:
            Text("3", (WIDTH // 2 - 1, HEIGHT // 2 - 20))
        elif 1000 < (current_time - self.ball_time) <= 2000:
            Text("2", (WIDTH // 2 - 1, HEIGHT // 2 - 20))
        elif 2000 < (current_time - self.ball_time) <= 3000:
            Text("1", (WIDTH // 2 - 1, HEIGHT // 2 - 20))
        elif (current_time - self.ball_time) > 3000:
            self.state = "moving"

    def draw_score(self):
        Text(self.score_one, (WIDTH // 2 - 100, HEIGHT // 2 + 10))
        Text(self.score_two, (WIDTH // 2 + 100, HEIGHT // 2 + 10))

    def collision(self):
        if pygame.sprite.spritecollide(self, self.paddles, False):
            Audio("sfx/paddle.mp3").play()
            paddle = pygame.sprite.spritecollide(self, self.paddles, False)[0].rect
            if abs(self.rect.right - paddle.left) < 10 and self.move.x != -1:
                self.move.x *= -1
            if abs(self.rect.left - paddle.right) < 10 and self.move.x != 1:
                self.move.x *= -1
            if abs(self.rect.top - paddle.bottom) < 10 and self.move.y != 1:
                self.move.y *= -1
            if abs(self.rect.bottom - paddle.top) < 10 and self.move.y != -1:
                self.move.y *= -1

    def update(self, dt):
        self.movement(dt)
        self.constraint()
        self.collision()

class Game:
    def __init__(self):
        self.pf = perf_counter()
        self.win = pygame.display.set_mode(WINSIZE)
        pygame.display.set_caption("Pong")

        icon = pygame.image.load("graphics/icon.png").convert_alpha()
        icon.set_colorkey((255, 255, 255))
        pygame.display.set_icon(icon)

        self.paddles = pygame.sprite.Group()
        self.ball = pygame.sprite.GroupSingle()

        player_one = Paddle((16, HEIGHT // 2), "one", self.paddles)
        player_two = Paddle((WIDTH - 16, HEIGHT // 2), "two", self.paddles)
        ball = Ball(self.ball, self.paddles)

    def run(self):
        while True:
            dt = perf_counter() - self.pf
            self.pf = perf_counter()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()

            self.ball.update(dt)
            self.paddles.update(dt)

            self.win.fill(BLACK_COLOR)
            pygame.draw.line(self.win, WHITE_COLOR, (WIDTH // 2 - 1, 0), (WIDTH // 2 - 1, HEIGHT))
            self.ball.draw(self.win)
            self.paddles.draw(self.win)
            self.ball.sprite.draw_timer()
            self.ball.sprite.draw_score()

            pygame.display.update()

game = Game()
game.run()

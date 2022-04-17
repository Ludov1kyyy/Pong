# Pong by @Ludov1kyyyy :)

import pygame
from sys import exit
from time import perf_counter
from random import choice

WIDTH, HEIGHT = 1024, 576

BLACK_COLOR = (24, 24, 24)
WHITE_COLOR = (200, 200, 200)

def display_text(info, pos, win, block=False):
    font = pygame.font.Font(None, 30)

    info_surf = font.render(str(info), True, WHITE_COLOR)
    info_rect = info_surf.get_rect(center = pos)

    if block:
        pygame.draw.rect(win, BLACK_COLOR, info_rect)

    win.blit(info_surf, info_rect)

class Paddle(pygame.sprite.Sprite):
    def __init__(self, pos_x, group, num):
        super().__init__(group)
        self.image = pygame.Surface((WIDTH // 64, HEIGHT // 5))
        self.image.fill(WHITE_COLOR)
        self.rect = self.image.get_rect(center = (pos_x, HEIGHT // 2))
        self.last_pos = self.rect.copy()
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.move = 0
        self.speed = 400
        self.num = num
        self.score = 0

    def input(self):
        key = pygame.key.get_pressed()

        if self.num == "one":
            UP = key[pygame.K_w]
            DOWN = key[pygame.K_s]
        else:
            UP = key[pygame.K_UP]
            DOWN = key[pygame.K_DOWN]

        if UP:
            self.move = -1
        elif DOWN:
            self.move = 1
        else:
            self.move = 0

    def movement(self, dt):
        self.last_pos = self.rect.copy()
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
        self.image = pygame.image.load("graphics/ball.png").convert()
        self.image.set_colorkey("white")
        self.rect = self.image.get_rect(center = (WIDTH // 2, HEIGHT // 2))
        self.last_pos = self.rect.copy()
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.move = pygame.math.Vector2(choice((1, -1)), choice((1, -1)))
        self.speed = 450
        self.active = False
        self.reset_time = 0
        self.num = 0

        self.paddles = paddles
        self.get_paddles()

        self.win = pygame.display.get_surface()

    def get_overlap(self):
        overlap = []
        for paddle in self.paddles:
            if self.rect.colliderect(paddle.rect):
                overlap.append(paddle)
        return overlap

    def get_paddles(self):
        for paddle in self.paddles:
            if paddle.num == "one":
                self.one = paddle
            else:
                self.two = paddle

    def movement_x(self, dt):
        if self.active:
            self.pos.x += self.move.x * self.speed * dt
            self.rect.x = round(self.pos.x)

    def movement_y(self, dt):
        if self.active:
            self.pos.y += self.move.y * self.speed * dt
            self.rect.y = round(self.pos.y)

    def constraint_x(self):
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.pos.x = self.rect.x
            self.active = False
            self.reset_time = pygame.time.get_ticks()
            self.one.score += 1
        if self.rect.left < 0:
            self.rect.left = 0
            self.pos.x = self.rect.x
            self.active = False
            self.reset_time = pygame.time.get_ticks()
            self.two.score += 1

    def constraint_y(self):
        if self.rect.top < 0:
            self.rect.top = 0
            self.pos.y = self.rect.y
            self.move.y *= -1
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.pos.y = self.rect.y
            self.move.y *= -1

    def collision(self, dt):
        self.last_pos = self.rect.copy()

        self.movement_x(dt)
        overlap = self.get_overlap()
        for paddle in overlap:
            if self.rect.right >= paddle.rect.left and self.last_pos.right <= paddle.last_pos.left:
                self.rect.right = paddle.rect.left
                self.pos.x = self.rect.x
                self.move.x *= -1
            if self.rect.left <= paddle.rect.right and self.last_pos.left >= paddle.last_pos.right:
                self.rect.left = paddle.rect.right
                self.pos.x = self.rect.x
                self.move.x *= -1
        self.constraint_x()

        self.movement_y(dt)
        overlap = self.get_overlap()
        for paddle in overlap:
            if self.rect.top <= paddle.rect.bottom and self.last_pos.top >= paddle.last_pos.bottom:
                self.rect.top = paddle.rect.bottom
                self.pos.y = self.rect.y
                self.move.y *= -1
            if self.rect.bottom >= paddle.rect.top and self.last_pos.bottom <= paddle.last_pos.top:
                self.rect.bottom = paddle.rect.top
                self.pos.y = self.rect.y
                self.move.y *= -1
        self.constraint_y()

    def timer(self):
        current_time = pygame.time.get_ticks()

        if not self.active:
            if current_time - self.reset_time <= 900:
                self.num = 3
            elif 900 < current_time - self.reset_time <= 1800:
                self.num = 2
            elif 1800 < current_time - self.reset_time <= 2700:
                self.num = 1
            else:
                self.active = True

    def reset_pos(self):
        if not self.active:
            self.rect.center = (WIDTH // 2, HEIGHT // 2)
            self.pos = pygame.math.Vector2(self.rect.topleft)
            self.move = pygame.math.Vector2(choice((1, -1)), choice((1, -1)))

    def display_surf(self):
        if not self.active:
            display_text(self.num, (WIDTH // 2, HEIGHT // 2 - 60), self.win, True)

        display_text(self.one.score, (WIDTH // 2 - 100, HEIGHT // 2), self.win)
        display_text(self.two.score, (WIDTH // 2 + 100, HEIGHT // 2), self.win)

    def update(self, dt):
        self.collision(dt)
        self.timer()
        self.reset_pos()
        self.display_surf()

class Game:
    def __init__(self):
        pygame.init()
        self.pf = perf_counter()
        self.win = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pong")
        icon_image = pygame.image.load("graphics/icon.png").convert()
        icon_image.set_colorkey("white")
        pygame.display.set_icon(icon_image)
        self.all_sprites = pygame.sprite.Group()

        self.paddle_one = Paddle(16, self.all_sprites, "one")
        self.paddle_two = Paddle(WIDTH - 16, self.all_sprites, "two")
        self.ball = Ball(self.all_sprites, [self.paddle_one, self.paddle_two])

    def event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

    def run(self):
        while True:
            dt = perf_counter() - self.pf
            self.pf = perf_counter()
            self.event()

            self.win.fill(BLACK_COLOR)
            pygame.draw.line(self.win, WHITE_COLOR, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))

            self.all_sprites.update(dt)
            self.all_sprites.draw(self.win)

            pygame.display.update()

game = Game()
game.run()

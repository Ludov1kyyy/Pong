# Pong by @Ludov1kyyyy

import pygame
from sys import exit
from time import perf_counter
from random import choice

pygame.init()

WIDTH, HEIGHT = 1024, 576
FONT = pygame.font.Font(None, 35)

BLACK_COLOR = (24, 24, 24)
WHITE_COLOR = (200, 200, 200)

class Paddle(pygame.sprite.Sprite):
    def __init__(self, pos_x, group, num):
        super().__init__(group)
        self.type = "PADDLE"
        self.image = pygame.Surface((WIDTH // 64, HEIGHT // 5))
        self.image.fill(WHITE_COLOR)
        self.rect = self.image.get_rect(center = (pos_x, HEIGHT // 2))
        self.old_rect = self.rect.copy()
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.move = 0
        self.speed = 400
        self.score = 0
        self.num = num

        self.win = pygame.display.get_surface()

    def input(self):
        key = pygame.key.get_pressed()

        if self.num == "one":
            UP = key[pygame.K_w]
            DOWN = key[pygame.K_s]
        if self.num == "two":
            UP = key[pygame.K_UP]
            DOWN = key[pygame.K_DOWN]

        if UP:
            self.move = -1
        elif DOWN:
            self.move = 1
        else:
            self.move = 0

    def movement(self, dt):
        self.old_rect = self.rect.copy()
        self.pos.y += self.move * self.speed * dt
        self.rect.y = round(self.pos.y)

    def constraint(self):
        if self.rect.top < 0:
            self.rect.top = 0
            self.pos.y = self.rect.y
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.pos.y = self.rect.y

    def display_score(self):
        score_surf = FONT.render(str(self.score), True, WHITE_COLOR)
        score_rect = score_surf.get_rect()

        if self.num == "one":
            score_rect.center = (WIDTH // 2 - 100, HEIGHT // 2)
        if self.num == "two":
            score_rect.center = (WIDTH // 2 + 100, HEIGHT // 2)

        self.win.blit(score_surf, score_rect)

    def update(self, dt):
        self.input()
        self.movement(dt)
        self.constraint()
        self.display_score()

class Ball(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.type = "BALL"
        self.image = pygame.image.load("graphics/ball.png").convert_alpha()
        self.image.set_colorkey("white")
        self.rect = self.image.get_rect(center = (WIDTH // 2, HEIGHT // 2))
        self.old_rect = self.rect.copy()
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.move = pygame.math.Vector2(choice((1, -1)), choice((1, -1)))
        self.speed = 450
        self.active = False
        self.reset_time = 0
        self.num = 0

        self.all_sprites = group
        self.paddles = []
        self.paddle_one, self.paddle_two = None, None
        self.win = pygame.display.get_surface()

    def get_overlap(self):
        overlap = []
        for spr in self.all_sprites:
            if self.rect != spr.rect:
                self.paddles.append(spr)
                if self.rect.colliderect(spr.rect):
                    overlap.append(spr)
        return overlap

    def get_paddles(self):
        for paddle in self.paddles:
            if paddle.num == "one":
                self.paddle_one = paddle
            if paddle.num == "two":
                self.paddle_two = paddle

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
            self.reset_time = pygame.time.get_ticks()
            self.active = False
            self.paddle_one.score += 1
        if self.rect.left < 0:
            self.rect.left = 0
            self.pos.x = self.rect.x
            self.reset_time = pygame.time.get_ticks()
            self.active = False
            self.paddle_two.score += 1

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
        self.old_rect = self.rect.copy()

        self.movement_x(dt)
        overlap = self.get_overlap()
        for paddle in overlap:
            if self.rect.right >= paddle.rect.left and self.old_rect.right <= paddle.old_rect.left:
                self.rect.right = paddle.rect.left
                self.pos.x = self.rect.x
                self.move.x *= -1
            if self.rect.left <= paddle.rect.right and self.old_rect.left >= paddle.old_rect.right:
                self.rect.left = paddle.rect.right
                self.pos.x = self.rect.x
                self.move.x *= -1
        self.constraint_x()

        self.movement_y(dt)
        overlap = self.get_overlap()
        for paddle in overlap:
            if self.rect.bottom >= paddle.rect.top and self.old_rect.bottom <= paddle.old_rect.top:
                self.rect.bottom = paddle.rect.top
                self.pos.y = self.rect.y
                self.move.y *= -1
            if self.rect.top <= paddle.rect.bottom and self.old_rect.top >= paddle.old_rect.bottom:
                self.rect.top = paddle.rect.bottom
                self.pos.y = self.rect.y
                self.move.y *= -1
        self.constraint_y()

    def not_active(self):
        if not self.active:
            self.rect.center = (WIDTH // 2, HEIGHT // 2)
            self.pos = pygame.math.Vector2(self.rect.topleft)
            self.move = pygame.math.Vector2(choice((1, -1)), choice((1, -1)))

    def timer(self):
        current_time = pygame.time.get_ticks()

        if not self.active:
            if current_time - self.reset_time < 900:
                self.num = 3
            elif 900 <= current_time - self.reset_time < 1800:
                self.num = 2
            elif 1800 <= current_time - self.reset_time < 2700:
                self.num = 1
            else:
                self.active = True

    def display_time(self):
        time_surf = FONT.render(str(self.num), True, WHITE_COLOR)
        time_rect = time_surf.get_rect(center = (WIDTH // 2, HEIGHT // 2 - 50))

        if not self.active:
            pygame.draw.rect(self.win, BLACK_COLOR, time_rect)
            self.win.blit(time_surf, time_rect)

    def update(self, dt):
        self.collision(dt)
        self.get_paddles()
        self.not_active()
        self.timer()
        self.display_time()

class Game:
    def __init__(self):
        self.pf = perf_counter()
        self.win = pygame.display.set_mode((WIDTH, HEIGHT))
        
        pygame.display.set_caption("Pong")
        
        icon_image = pygame.image.load("graphics/icon.png").convert_alpha()
        icon_image.set_colorkey("white")
        pygame.display.set_icon(icon_image)
        
        self.all_sprites = pygame.sprite.Group()

        paddle_one = Paddle(16, self.all_sprites, "one")
        paddle_two = Paddle(WIDTH - 16, self.all_sprites, "two")
        ball = Ball(self.all_sprites)

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
            
            self.win.fill(BLACK_COLOR)
            pygame.draw.line(self.win, WHITE_COLOR, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))

            self.all_sprites.update(dt)
            self.all_sprites.draw(self.win)
            
            pygame.display.update()

game = Game()
game.run()

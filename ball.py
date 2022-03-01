import pygame
from setup import *
from random import choice

class Ball(pygame.sprite.Sprite):
	def __init__(self, pos, group, paddles):
		super().__init__(group)
		self.image = pygame.Surface((12, 12))
		self.rect = self.image.get_rect(center = pos)
		
		self.win = pygame.display.get_surface()
		self.font = pygame.font.Font("freesansbold.ttf", 24)

		self.paddles = paddles
		self.direction = pygame.math.Vector2(choice((-1, 1)), choice((-1, 1)))
		self.attri = {"radius": 12, "speed": 6, "active": False, "score_time": 0}
		self.score = {"one": 0, "two": 0}

	def movement(self):
		if self.attri["active"]:
			self.rect.center += self.direction * self.attri["speed"]
		else: self.timer()

	def collision(self):
		if pygame.sprite.spritecollide(self, self.paddles, False):
			paddle = pygame.sprite.spritecollide(self, self.paddles, False)[0].rect
			if abs(self.rect.right - paddle.left) < 15 and self.direction.x > 0:
				self.direction.x *= -1
			if abs(self.rect.left - paddle.right) < 15 and self.direction.x < 0:
				self.direction.x *= -1
			if abs(self.rect.top - paddle.bottom) < 15 and self.direction.y < 0:
				self.direction.y *= -1
			if abs(self.rect.bottom - paddle.top) < 15 and self.direction.y > 0:
				self.direction.y *= -1

	def bouncing(self):
		if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
			self.direction.y *= -1

	def reset_pos(self):
		self.attri["score_time"] = pygame.time.get_ticks()
		self.attri["active"] = False
		self.rect.center = (WIDTH//2 + 1, HEIGHT//2)
		self.direction.x = choice((-1, 1))

	def reset_ball(self):
		if self.rect.left >= WIDTH:
			self.reset_pos()
			self.score["one"] += 1
		if self.rect.right <= 0:
			self.reset_pos()
			self.score["two"] += 1

	def timer(self):
		current_time = pygame.time.get_ticks()
		num = 0

		if (current_time - self.attri["score_time"]) <= 700: num = 3
		if 700 < (current_time - self.attri["score_time"]) <= 1400: num = 2
		if 1400 < (current_time - self.attri["score_time"]) <= 2100: num = 1
		if (current_time - self.attri["score_time"]) >= 2100: self.attri["active"] = True

		text = self.font.render(str(num), True, PLAYER_COLOR)
		pos = text.get_rect(center = (WIDTH//2, HEIGHT//2 - 100))
		if num > 0:
			pygame.draw.rect(self.win, BG_COLOR, pos)
			self.win.blit(text, pos)

	def display_score(self):
		one = self.font.render(str(self.score["one"]), True, PLAYER_COLOR)
		one_pos = one.get_rect(center = (WIDTH//2 - 50, HEIGHT//2))
		
		two = self.font.render(str(self.score["two"]), True, PLAYER_COLOR)
		two_pos = two.get_rect(center = (WIDTH//2 + 50, HEIGHT//2))

		self.win.blit(one, one_pos)
		self.win.blit(two, two_pos)

	def draw(self):
		pygame.draw.circle(self.win, BALL_COLOR, self.rect.center, self.attri["radius"])
		self.display_score()

	def update(self):
		self.movement()
		self.collision()
		self.bouncing()
		self.reset_ball()

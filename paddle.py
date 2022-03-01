import pygame
from setup import *

class Paddle(pygame.sprite.Sprite):
	def __init__(self, pos, group, num="one"):
		super().__init__(group)
		self.image = pygame.Surface((15, 100))
		self.image.fill(PLAYER_COLOR)
		self.rect = self.image.get_rect(center = pos)
		self.paddle = num

		self.direction = pygame.math.Vector2()
		self.speed = 6

	def input(self):
		keys = pygame.key.get_pressed()

		if self.paddle == "one":
			UP = keys[pygame.K_w]
			DOWN = keys[pygame.K_s]
		else:
			UP = keys[pygame.K_UP]
			DOWN = keys[pygame.K_DOWN]

		if UP: self.direction.y = -1
		elif DOWN: self.direction.y = 1
		else: self.direction.y = 0

	def movement_y(self):
		self.rect.y += self.direction.y * self.speed

	def constraint(self):
		if self.rect.top <= 0:
			self.rect.top = 0
		elif self.rect.bottom >= HEIGHT:
			self.rect.bottom = HEIGHT

	def update(self):
		self.input()
		self.movement_y()
		self.constraint()

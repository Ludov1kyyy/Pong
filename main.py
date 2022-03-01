import pygame
from sys import exit
from setup import *
from paddle import Paddle
from ball import Ball

class Game:
	def __init__(self):
		self.paddles = pygame.sprite.Group()
		self.ball = pygame.sprite.GroupSingle()

		paddle_one = Paddle((15, HEIGHT//2), self.paddles)
		paddle_two = Paddle((WIDTH - 15, HEIGHT//2), self.paddles, "two")
		ball = Ball((WIDTH//2 + 1, HEIGHT//2), self.ball, self.paddles)

	def run(self):
		win.fill(BG_COLOR)
		pygame.draw.line(win, PLAYER_COLOR, (WIDTH//2, 0), (WIDTH//2, HEIGHT))

		self.ball.sprite.draw()
		self.paddles.draw(win)

		self.paddles.update()
		self.ball.update()

if __name__ == "__main__":
	pygame.init()

	win = pygame.display.set_mode(WINSIZE)
	clock = pygame.time.Clock()
	pygame.display.set_caption("Pong")

	game = Game()

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				exit()

		game.run()

		pygame.display.flip()
		clock.tick(FPS)

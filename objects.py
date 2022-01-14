
import pygame
from pygame.math import Vector2
from settings import *
from engine import *

class Player(GameObject):
	def __init__(self, filenames):
		super().__init__(filenames, (74, 52))
		
		self.position = Vector2(60, HEIGHT / 2)
		self.create_collider('circle', 12)
		
		self.last_update = pygame.time.get_ticks()
		self.max_time = 70
		self.frames = [1, 2, 1, 0]
		
		self.flapped = False
		self.start = False
		self.angle = 0
		self.angle_speed = 0
	
	def update(self, dt):
		now = pygame.time.get_ticks()
		if now - self.last_update >= self.max_time:
			self.last_update = now
			self.frame = self.frames.pop()
			self.update_image()
			if not self.frames:
				self.frames = [1, 2, 1, 0]
		
		if self.flapped:
			self.velocity.y = FLAPSPEED
			self.angle_speed = 7.8
			self.flapped = False
		
		if self.start:
			self.angle += self.angle_speed
			if self.velocity.y > 350:
				self.angle_speed = -3.5
			if self.angle > 30:
				self.angle = 30
			if self.angle < -90:
				self.angle = -90
				
			self.rotate(self.angle)

		self.move(dt)
		
		
class Pipe(GameObject):
	def __init__(self, x, y, filename):
		super().__init__(filename, (120, HEIGHT // 2 + 200))
		
		self.position = Vector2(x, y)
		self.velocity.x = PIPESPEED
	
	def update(self, dt):
		if self.position.x + self.width < 0:
			self.kill()
		self.move(dt)
		
		
class PointBlock(GameObject):
	def __init__(self, pipe):
		super().__init__((20, PIPEGAP))
		self.pipe = pipe
		self.position.x = pipe.position.x + pipe.width + 30
		self.position.y = pipe.position.y + pipe.height
		
		self.create_collider('box')
		
		self.velocity.x = PIPESPEED
		

class Score(GameObject):
	def __init__(self):
		super().__init__(NUMLIST, (50, 80))
		self.score = 0
		self.center = WIDTH / 2, 160
		
	def update(self):
		self.score += 1
		text = str(self.score)
		if len(text) == 1:
			self.frame += 1
			self.update_image()
		else:
			self.image = pygame.Surface((self.width * len(text), self.height))
			self.image.set_colorkey((0, 0, 0))
			for i in range(len(text)):
				num_img = self.images[int(text[i])].copy()
				self.image.blit(num_img, (self.width * i, 0))
				self.center = WIDTH / 2, 160
	
	
class Base(GameObject):
	def __init__(self, x, y):
		super().__init__('sprites/base.png', (WIDTH, 200))
		self.position = Vector2(x, y)
		self.create_collider('box', (0, 0), (0, 10))
		self.velocity.x = PIPESPEED
	
	def update(self, dt):
		if self.position.x + self.width < 1:
			self.position.x = WIDTH - 1
		self.move(dt)
		
		
class Sound:
	def __init__(self):
		self.wing = pygame.mixer.Sound('audio/wing.ogg')
		self.die = pygame.mixer.Sound('audio/die.ogg')
		self.point = pygame.mixer.Sound('audio/point.ogg')
		self.hit = pygame.mixer.Sound('audio/hit.ogg')
		

class ScorePanel(GameObject):
	def __init__(self, score):
		super().__init__(IMAGES_PATH + 'panel_score.png', (560, 280))
		self.center = WIDTH / 2, HEIGHT + self.height
		
		best_score = -1
		try:
			fp = open('best.txt', 'r')
			best_score = int(fp.read())
		except FileNotFoundError:
			fp = open('best.txt', 'w')
			fp.write(str(score.score))
		fp.close()
		
		if score.score > best_score:
			best_score = score.score
			fp = open('best.txt', 'w')
			fp.write(str(best_score))
			fp.close()
		
		
		if best_score != -1:
			text = str(best_score)
			best = pygame.Surface((score.width * len(text), score.height))
			best.set_colorkey((0, 0, 0))
			for i in range(len(text)):
				num_img = score.images[int(text[i])].copy()
				best.blit(num_img, (score.width * i, 0))
		
		best_width = best.get_width()
		score_width = score.image.get_width()
		score.image = pygame.transform.scale(score.image, (score_width * 2 // 3, 50))
		score_width = score.image.get_width()
		self.image.blit(score.image, (500 - score_width, 80))
		if best_score != -1:
			best = pygame.transform.scale(best, (best_width * 2 // 3, 50))
			best_width = best.get_width()
			self.image.blit(best, (500 - best_width, 180))
		else:
			self.image.blit(score.image, (500 - score_width, 180))
		
		n = 0
		for key in MEDALLIST.keys():
			if score.score >= key:
				n = key
		if n != 0:
			medal = load_scale(MEDALLIST[n], (110, 110))
			self.image.blit(medal, (65, 100))
			
		self.velocity.y = -2000
		self.last_update = 0
		self.show = False
	
	def update(self, dt):
		now = pygame.time.get_ticks()
		if now - self.last_update > 700:
			self.show = True
		if self.show:
			self.move(dt)
			if self.center.y <= HEIGHT / 2:
				self.center = WIDTH / 2, HEIGHT / 2

class GameOver(GameObject):
	def __init__(self):
		super().__init__(IMAGES_PATH + 'gameover.png', (WIDTH // 2 + 150, 120))
		self.center = WIDTH / 2, HEIGHT / 4
		
		self.velocity.y = -30
		self.last_update = 0
		self.show = False
		
	def update(self,dt):
		now = pygame.time.get_ticks()
		if now - self.last_update > 500:
			self.show = True
		if self.show:
			self.move(dt)
			if self.center.y > HEIGHT / 4:
				self.velocity.y *= -1
			if self.center.y < HEIGHT / 4 - 30:
				self.velocity.y *= -1
				
				
				
			
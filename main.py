
import pygame
from random import choice, randint
from pygame.locals import *
from objects import *
from settings import *
from engine import *

class FlappyBird:
	def __init__(self):
		pygame.init()
		self.window = pygame.display.set_mode((WIDTH, HEIGHT), SCALED | FULLSCREEN)
		self.clock = pygame.time.Clock()
		
	def initialize(self):
		self.background = GameSprite(choice(BGLIST), (WIDTH, HEIGHT - 150))
		
		self.player.gravity_scale = 2000
		self.player.start = True
		
		self.pipes = ObjectGroup()
		self.point_blocks = ObjectGroup()
		
		self.pipe_image = choice(PIPELIST)
		self.make_pipes()
		self.make_pipes()
		
		self.score = Score()
		
		self.gameover = GameOver()
		
		self.ok_button = GameObject(IMAGES_PATH + 'button_ok.png', (150, 75))
		self.ok_button.center = WIDTH / 2, HEIGHT * 3 / 4
		self.ok_button.create_collider('box')
		
		self.game_over = False
		self.done = False
		
	def check_events(self):
		for event in pygame.event.get():
			if event.type == MOUSEBUTTONDOWN:
				if self.game_over:
				   if self.ok_button.collidepoint(event.pos[0], event.pos[1]):
				   	self.done = True
				else:
					self.player.flapped = True
					self.sound.wing.play()
			
	def update(self, dt):
		if self.player.collide_group(self.bases, False):
			self.last_update = pygame.time.get_ticks()
			if not self.game_over:
				self.sound.hit.play()
				self.panel = ScorePanel(self.score)
				self.gameover.last_update = pygame.time.get_ticks()
				self.panel.last_update = pygame.time.get_ticks()
			self.player.stop_moving()
			self.player.position.y = self.bases.sprites()[0].position.y - 50
			self.player.max_time = 1000000
			self.game_over = True
			
		if self.player.collide_group(self.pipes, False) and not self.game_over:
			self.last_update = pygame.time.get_ticks()
			self.sound.hit.play()
			self.sound.die.play()
			self.player.velocity.y = 0
			self.player.max_time = 1000000
			self.game_over = True
			self.panel = ScorePanel(self.score)
			self.panel.last_update = pygame.time.get_ticks()
			self.gameover.last_update = pygame.time.get_ticks()
		
		if self.player.collide_group(self.point_blocks, True):
			self.score.update()
			self.sound.point.play()
		
		if not self.game_over:
			self.bases.update(dt)
			self.pipes.update(dt)
			self.point_blocks.update(dt)
		else:
			self.gameover.update(dt)
			self.panel.update(dt)
			
		self.player.update(dt)
		
		if len(self.pipes) < 3:
			self.make_pipes()

	def render(self):
		self.background.draw(self.window)
		self.pipes.draw(self.window)
		self.bases.draw(self.window)
		self.player.draw(self.window)
		
		if self.game_over:
			if self.gameover.show:
				self.gameover.draw(self.window)
			
			if self.panel.show:
				self.ok_button.draw(self.window)
				self.panel.draw(self.window)
		else:
			self.score.draw(self.window)
		
		pygame.display.flip()
		
	def run(self):
		# Game loop
		while not self.done:
			dt = self.clock.tick(FPS) / 1000
			self.check_events()
			self.update(dt)
			self.render()
			
	def make_pipes(self):
		if len(self.pipes) > 0:
			pipe_x = self.pipes.sprites()[-1].position.x + PIPEDISTANCE
		else:
			pipe_x = WIDTH + 100
		pipe_y = randint(HEIGHT // 2 - 260, HEIGHT // 2 + 260)
		l_pipe = Pipe(pipe_x, pipe_y, self.pipe_image)
		u_pipe = Pipe(pipe_x, pipe_y - PIPEGAP - l_pipe.height, self.pipe_image)
		u_pipe.flip(False, True)
		u_pipe.create_collider('box', (4, 0), (0, -6))
		l_pipe.create_collider('box', (4, 0), (0, 6))
		
		p_block = PointBlock(u_pipe)
		
		self.point_blocks.add(p_block)
		self.pipes.add(l_pipe)
		self.pipes.add(u_pipe)
	
	def menu_screen(self):
		background = GameSprite(BGLIST[0], (WIDTH, HEIGHT-150))
		
		message = GameSprite(IMAGES_PATH + 'message.png', (WIDTH // 2 + 40, HEIGHT//2))
		message.rect.center = (WIDTH / 2, HEIGHT / 2 - 100)
		
		self.bases = ObjectGroup()
		self.bases.add(Base(0, HEIGHT - 200))
		self.bases.add(Base(WIDTH, HEIGHT - 200))
		
		self.player = Player(choice(BIRDLIST))
		self.player.velocity.y = -60
		
		self.sound = Sound()
		
		while True:
			dt = self.clock.tick(FPS) / 1000
			
			for event in pygame.event.get():
				if event.type == FINGERDOWN:
					self.player.flapped = True
					self.player.velocity.y = FLAPSPEED
					self.sound.wing.play()
					self.initialize()
					return True
					
			if self.player.position.y < 600:
				self.player.velocity.y *= -1
			if self.player.position.y > 640:
				self.player.velocity.y *= -1
					
			self.player.update(dt)
			self.bases.update(dt)
					
			background.draw(self.window)
			message.draw(self.window)
			
			self.player.draw(self.window)
			self.bases.draw(self.window)
			
			pygame.display.flip()
	
	
if __name__ == '__main__':
	game = FlappyBird()
	while True:
		game.menu_screen()
		game.run()
		











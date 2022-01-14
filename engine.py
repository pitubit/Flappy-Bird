
import pygame
from pygame.locals import *
from pygame.math import Vector2
from pygame.sprite import Sprite, Group

Vector = Vector2

class ObjectGroup(Group):
	def __init__(self):
		super().__init__()
	
	def debug(self, target):
		for sp in self.sprites():
			sp.debug(target)
		
	def draw(self, target):
		for sp in self.sprites():
			sp.draw(target)


# ------------------- collision part ------------------
# A CLASS OF METHODS FOR CHECKING DIFFERENT COLLISIONS.
class Collisions:
	def box_collision(self, left, right):
		if left.rect.colliderect(right.rect):
			return True
		return False
		
	def circle_collision(self, left, right):
		lx, ly = left.position
		rx, ry = right.position
		
		dist_x = lx - rx
		dist_y = lx - rx
		
		dist = dist_x ** 2 + dist_y ** 2
		if dist < (left.radius + right.radius) ** 2:
			return True
		return False
	
	def box_circle_collision(self, box, circle):
		bx, by = box.rect.topleft
		cx, cy = circle.position
		test_x, test_y = cx, cy
		
		if cx < bx:
			test_x = bx
		elif cx > bx + box.rect.w:
			test_x = bx + box.rect.w
			
		if cy < by:
			test_y = by
		elif cy > by + box.rect.h:
			test_y = by + box.rect.h
			
		dist_x = cx - test_x
		dist_y = cy - test_y
			
		dist = dist_x ** 2 + dist_y ** 2
		if dist < circle.radius ** 2:
			return True 
		return False
		
		
# MODEL FOR PROVIDING HIT BOX COMPONENT.
class BoxCollider(Collisions):
	def __init__(self, object, crop=(0, 0), offset=(0, 0)):
		self.object = object
		self.rect = pygame.Rect(object.position, (object.width-crop[0], object.height-crop[1]))
		self.offset = Vector(offset)
		self.color = (0, 255, 0)
		self.rect.size -= Vector(crop)
	
		self.collidepoint = self.rect.collidepoint
		self.colliderect = self.rect.colliderect
		
	def is_collided_with(self, other):
		try:
			if other.radius:
				result = self.box_circle_collision(self, other)
		except AttributeError:
			result = self.colliderect(other)
		
		if result:
			self.color = (255, 0, 0)
		else:
			self.color = (0, 255, 0)
			
		return result
	
	def update(self):
		self.rect.center = self.object.center + self.offset
		
	def draw(self, target):
		pygame.draw.rect(target, self.color, self.rect, 2)
		
		
# MODEL FOR PROVIDING HIT CIRCLE COMPONENT.
class CircleCollider(Collisions):
	def __init__(self, object, crop=0, offset=(0, 0)):
		self.object = object
		self.radius = object.width / 2 - crop
		self.position = Vector(object.center)
		self.offset = Vector(offset)
		self.color = (0, 255, 0)
		
	def collidepoint(self, x, y):
		dist = Vector(x, y) - self.center
		dist = dist ** 2
		if dist.length_squared() < self.radius:
			return True
		return False
		
	def is_collided_with(self, other):
		try:
			if other.radius:
				result = self.circle_collision(self, other)
		except AttributeError:
			result = self.box_circle_collision(other, self)
		
		if result:
			self.color = (255, 0, 0)
		else:
			self.color = (0, 255, 0)
			
		return result
		
	def update(self):
		self.position = self.object.center + self.offset
		
	def draw(self, target):
		pygame.draw.circle(target, self.color, self.position, self.radius, 2)
# --------X--------- collision part ---------X---------------


# GAMEOBJECT MODEL OF SPRITE
class GameObject(Sprite):
	def __init__(self, *args):
		super().__init__()
		self.images = []
		if type(args[0]) == str:
			self.images.append(load_scale(*args))
		elif type(args[0]) == list:
			self.images = load_multiple(*args)
		else:
			surface = pygame.Surface(*args).convert_alpha()
			surface.fill((255, 255, 255))
			self.images.append(surface)
			
		self.frame = 0
		self.update_image()
		self.position = Vector(0, 0)
		self.collider = []
		
		self.velocity = Vector(0, 0)
		self.gravity_scale = 0
	
	def update_image(self):
		self.image = self.images[self.frame].copy()
		self._update_dim()
		
	def _update_dim(self):
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		
	@property
	def center(self):
		cen = Vector()
		cen.x = self.position.x + self.width / 2
		cen.y = self.position.y + self.height / 2
		return cen
	
	@center.setter
	def center(self, pos):
		pos = Vector(pos)
		self.position.x = pos.x - self.width / 2
		self.position.y = pos.y - self.height / 2
		 
	def create_collider(self, tag, *args):
		if tag == 'box':
			c = BoxCollider(self, *args)
		else:
			c = CircleCollider(self, *args)
		self.collider.append(c)
	
	def scale(self, size):
		copy = self.images[self.frame].copy()
		self.image = pygame.transform.scale(copy, size)
		self._update_dim()
		
	def rotate(self, angle):
		copy = self.images[self.frame].copy()
		self.image = pygame.transform.rotate(copy, angle)
		self._update_dim()
		
	def rotozoom(self, angle, scale):
		copy = self.images[self.frame].copy()
		self.image = pygame.transform.rotozoom(copy, angle, scale)
		self._update_dim()
		
	def flip(self, xbool, ybool):
		copy = self.images[self.frame].copy()
		self.image = pygame.transform.flip(copy, xbool, ybool)
		
	def stop_moving(self):
		self.gravity_scale = 0
		self.velocity *= 0
		
	def collidepoint(self, x, y):
		for c in self.collider:
			return c.collidepoint(x, y)
		
	def collide(self, object):
		for c1 in self.collider:
			for c2 in object.collider:
				return c1.is_collided_with(c2)
				
	def collide_group(self, group, dokill):
		collided = []
		for object in group:
			if self.collide(object):
				collided.append(object)
				if dokill:
					object.kill()
					
		if collided:
			return collided
		return None
		
	def move(self, dt):
		self.velocity.y += self.gravity_scale * dt
		self.position += self.velocity * dt
		if self.collider:
			for c in self.collider:
				c.update()
				
	def update(self, dt):
		self.move(dt)
		
	def debug(self, target):
		self.draw(target)
		for c in self.collider:
			c.draw(target)
		
	def draw(self, target):
		target.blit(self.image, self.position)
		

class GameSprite(Sprite):
	def __init__(self, *args):
		if type(args[0]) == str:
			self.image = load_scale(*args)
		else:
			self.image = pygame.Surface(*args).convert_alpha()
		self.rect = self.image.get_rect()
	
	def draw(self, target):
		target.blit(self.image, self.rect)


# Utility Functions.
def load_scale(file, size=1, colorkey=None):
	image = pygame.image.load(file).convert_alpha()
	if (size != 1):
		image = pygame.transform.scale(image, size)
	if colorkey:
		image.set_colorkey(colorkey)
	return image
		
def load_multiple(files, size=1, colorkey=None):
	images  = []
	for f in files:
		images.append(load_scale(f, size, colorkey))
	return images

def groupcollide(group1, group2, dokill1, dokill2):
	collided = {}
	for object in group1:
		list = object.collide_group(group2)
		if list:
			collided[object] = list
			
	if collided:
		return collided
	return None






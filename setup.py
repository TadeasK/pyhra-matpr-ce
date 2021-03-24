import pygame
import sys


"""
 	Vytvářím třídu Block, založenou na třídě Sprite,
 	která je v Pygame předdefinována.
	Třídu Block budu využívat pouze k tvoření jiných
	tříd, abych pro ně neopisoval stále stejný kód.
"""
class Block(pygame.sprite.Sprite):
	def __init__(self, path, pos_x, pos_y):
		"""
			Funkce načte cestu, pozici x a pozici y,
			které budou využívat dceřinné třídy.
			path poslouží pro nalezení cesty ke grafice objektu.
			pos_x, pos_y budou určovat pozici objektu.
			image a rect jsoou povinné vlastnosti Pygame spritů.
			Využívám vestavěnou funkci super(), která usnadňuje víceúrovňovou dědičnost.
		"""
		super().__init__()
		self.image = pygame.image.load(path)
		self.rect = self.image.get_rect(center = (pos_x, pos_y))

	
"""
	Třída Player založená na tříde Block.
	Ve hře bude zastávat funkce hráčova charakteru.
"""
class Player(Block):
	def __init__(self, path, pos_x, pos_y, speed):
		"""
			Díky funkci super() dědí vlastnosti path a pos_x, y z třídy Block
			Dále dostává vlastnost speed, která bude určovat rychlost pohybu.
		"""
		super().__init__(path, pos_x, pos_y)
		self.speed = speed
		self.movement = 0

	def constrain(self):
		"""
			Metoda constrain zajišťuje, že nebude možné odejít z hracího pole.
		"""
		pass

	def update(self, ball_group):
		"""
			Metoda, která zajistí vykreslování pohybu hráče.
		"""
		pass

	def shoot(self):
		"""
			Metoda shoot bude vytvářet projektily podle třídy Bullet.
		"""
		pass


"""
	Třída Bullet založená na třídě Block.
	Ve hře zastává funkčnost projektilů, které po sobě hráč a počítač střílí.
"""
class Bullet(Block):
	def __init__(self, path, pos_x, pos_y, speed_x, speed_y, characters):
		"""
			Díky funkci super() dědí vlastnosti path a pos_x, y z třídy Block
			Dále dostává vlastnost speed, která bude určovat rychlost pohybu
			a characters, která nám poslouží kvůli kolizím s hráčovým a počítačovým 
			charakterem.
		"""
		super().__init__(path, pos_x, pos_y)
		self.speed_x = speed_x
		self.speed_y = speed_y
		self.characters = characters

	def update(self):
		"""
			Metoda, která zajistí vykreslování pohybu projektilů.
		"""
		pass

	def collisions(self):
		"""
			Metoda, která bude hlídat, zda projektil nezasáhl něhjaký z charakterů.
		"""
		pass


"""
	Třída Opponent založená na třídě Block.
	Bude zastávat funkčnost oponenta hráče.
"""
class Opponent(Block):
	"""
		Díky funkci super() dědí vlastnosti path a pos_x, y z třídy Block
		Dále dostává vlastnost speed, která bude určovat rychlost pohybu.
	"""
	def __init__(self,path,x_pos,y_pos,speed):
		super().__init__(path,x_pos,y_pos)
		self.speed = speed

	def update(self,ball_group):
		"""
			Metoda zajišťující pohyb oponenta.
		"""

	def constrain(self):
		"""
			Metoda constrain zajišťuje, že nebude možné odejít z hracího pole.
		"""


	def shoot(self):
		"""
			Metoda shoot bude vytvářet projektily podle třídy Bullet.
		"""
		pass

"""
	Třáda Manager dá všechno dohromady a postará se o fungování hry jako celku.
"""
class Manager():
	"""
		Bere si skupinu spritů, ve které jsou charaktery a kulky, jako argumenty.
	"""
	def __init__(self, characters, bullets):
		self.characters = characters
		self.bullets = bullets

	def run_game(self):
		"""
			Vykresluje a updatuje objekty.
		"""	
		pass

	def draw_score(self):
		"""

		"""
		pass

	def draw_time(self):
		"""
		
		"""
		pass


"""
	Základní inicializace a funkčnost hry.
"""
pygame.init()
clock = pygame.time.Clock()


"""
	Nastavení herního okna
"""
screen_width = 1280
screen_height = 960
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('Přestřelka')


"""
	Hlavní loop, díky kterému hra poběží.
"""
while True:
	# Zpracování uživatelského vstupu
	for event in pygame.event.get():
		# Umožňuje vypnutí hry
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()

		

	# Obnovování okna, aby bylo možné pozorovat pohyb
	pygame.display.flip()
	clock.tick(60)

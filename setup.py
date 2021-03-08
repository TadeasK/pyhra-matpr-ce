import pygame, sys

# 
pygame.init()
clock = pygame.time.Clock()

# Nastavení hracího okna
screen_width = 1280
screen_height = 960
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('Přestřelka')

# Barvičky
green = (34,139,34)
darkgreen = (0,100,0)
blue = (30,144,255)
darkblue = (0,0,255)
yellow = (255,255,0)
black = (0, 0, 0)
grey = (200,200,200)

# Objekty
Player = pygame.Rect(screen_width/2 - 70, screen_height - 10, 140, 10)
Enemy = pygame.Rect(screen_width/2 - 70, 0, 140, 10)

background_color = green


# Průběh hry
while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()

	# Vizualizace
	pygame.draw.rect(screen, grey, Player)
	pygame.draw.rect(screen, yellow, Enemy)


	pygame.display.flip()
	clock.tick(60)
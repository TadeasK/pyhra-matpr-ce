import pygame
import sys
import os
import time
global elapsed_time


class Character(pygame.sprite.Sprite):
    """
    Vytvářím abstraktní třídu Character, založenou na třídě Sprite,
    která je v Pygame předdefinována.
    Třídu Character budu využívat pouze k tvoření jiných
    tříd, abych pro ně neopisoval stále stejný kód.
    """

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
        self.image = pygame.image.load(os.path.join('assets', path))
        self.rect = self.image.get_rect(center=(pos_x, pos_y))
        self.mask = pygame.mask.from_surface(self.image)


class Player(Character):
    """
    Třída Player založená na tříde Character.
    Ve hře bude zastávat funkce hráčova charakteru.
    """
    CD = 30

    def __init__(self, path, pos_x, pos_y, speed):
        """
        Díky funkci super() dědí vlastnosti path a pos_x, y z třídy Character.
        Dále dostává vlastnost speed, která bude určovat rychlost pohybu.
        """
        super().__init__(path, pos_x, pos_y)
        self.speed = speed
        self.movement_x = 0
        self.movement_y = 0
        self.cooldown_time = 0

    def cooldown(self):
        if self.cooldown_time >= self.CD:
            self.cooldown_time = 0
        elif self.cooldown_time > 0:
            self.cooldown_time += 1

    def shoot(self):
        """
        Metoda shoot bude vytvářet projektily.
        """
        if self.cooldown_time <= 0:
            self.cooldown_time = 0
            return Bullet('player_bullet.png', self.rect.centerx, self.rect.centery, characters)

    def constrain(self):
        """
        Metoda constrain zajišťuje, že nebude možné odejít z hracího pole.
        """
        if self.rect.top <= 730:
            self.rect.top = 730
        if self.rect.bottom >= screen_height:
            self.rect.bottom = screen_height
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.right >= screen_width:
            self.rect.right = screen_width

    def update(self):
        """
        Metoda, která zajistí vykreslování pohybu hráče.
        """
        self.rect.x += self.movement_x
        self.rect.y += self.movement_y
        self.constrain()

    def enemy_kill():
        pass


class Bullet(Character):


    """
    Třída Bullet ve hře zastává funkčnost projektilů,
    které po sobě hráč a počítač střílí.
    """

    def __init__(self, path, pos_x, posy, characters):
       	"""
    	Díky funkci super() dědí vlastnosti path a pos_x, y z třídy Character
    	Dále dostává vlastnost speed, která bude určovat rychlost pohybu
    	a characters, která nám poslouží kvůli kolizím s hráčovým a počítačovým
    	charakterem.
    	"""
        super().__init__(path, pos_x, pos_y)
        self.characters = characters

    def update(self, speed):
        """
        Metoda, která posouvá projektil..
        """
        self.rect.y += speed

    def collision(self, characters):
        """
        Metoda, která bude hlídat, zda projektil nezasáhl nějaký z charakterů.
        """
        return self.collide(characters, self)

    def collide(self, obj1, obj2):
        offset_x = obj2.x - obj1.x
        offset_y = obj2.y - obj1.y
        return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


class Opponent(Character):
    """
    Třída Opponent založená na třídě Character.
    Bude zastávat funkčnost oponenta hráče.
    """
    CD = 30

    def __init__(self, path, x_pos, y_pos, speed):
    """
    Díky funkci super() dědí vlastnosti path a pos_x, y z třídy Character
    Dále dostává vlastnost speed, která bude určovat rychlost pohybu.
    """
    super().__init__(path, x_pos, y_pos)
    self.speed = speed
    self.cooldown_time = 0

    def update(self):
        """
        Metoda zajišťující pohyb oponenta.
        """
        if self.cooldown_time == 0:
            if self.rect.centerx == player.rect.centerx or abs(self.rect.centerx - player.rect.centerx) <= 64:
                enemy_bullets.add(opponent.shoot())
                self.cooldown_time = 1

        self.constrain()

    def cooldown(self):
        if self.cooldown_time >= self.CD:
            self.cooldown_time = 0
        elif self.cooldown_time > 0:
            self.cooldown_time += 1

    def shoot(self):
        """
        Metoda shoot bude vytvářet projektily.
        """
        if self.cooldown_time == 0:
            return Bullet('enemy_bullet.png', self.rect.centerx, self.rect.centery, characters)
            self.cooldown_time = 1

    def constrain(self):
        """
        Metoda constrain zajišťuje, že nebude možné odejít z hracího pole.
        """
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= 230:
            self.rect.bottom = 230
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.right >= screen_width:
            self.rect.right = screen_width


class Manager():
    """
	Třída Manager dá všechno dohromady a postará se o fungování hry jako celku.
	"""
    def __init__(self, characters, player_bullets, enemy_bullets):
		"""
    	Bere si skupinu spritů, ve které jsou charaktery a kulky, jako argumenty.
    	"""
        self.characters = characters
        self.player_bullets = player_bullets
        self.enemy_bullets = enemy_bullets

    def run_game(self):
        """
        Vykresluje a updatuje objekty.
        """
        screen.blit(bg_river, (0, 230))
        screen.blit(bg_grass, (0, 0))
        screen.blit(bg_grass, (0, 730))
        self.player_bullets.draw(screen)
        self.enemy_bullets.draw(screen)
        self.characters.draw(screen)

        self.player_bullets.update(-8)
        self.enemy_bullets.update(+8)
        self.characters.update()

        player.cooldown()
        opponent.cooldown()

        self.draw_score()
        self.draw_time()

    def draw_score(self):
        """
        Metoda, která bude počítat skóre od začátku kola.
        Skóre bude stoupat lineárně, za každé zabití oponenta.
        """
        score = 0
        score += elapsed_time * 100
        if player.enemy_kill is True:
            score += 1000

        score_render = font.render(f"Score: {score:11.0f}", 1, font_color)

        screen.blit(score_render, (screen_width -
                    score_render.get_width() - 30, 30))

    def draw_time(self):
        """
        Metoda, která bude počítat čas od začátku kola.
        """
        time_render = font.render(f"Time: {elapsed_time:9.4f}", 1, font_color)

        screen.blit(time_render, (30, 30))


"""
Základní inicializace a funkčnost hry.
"""
pygame.init()
pygame.font.init()
clock = pygame.time.Clock()


"""
Nastavení herního okna
"""
screen_width = 1280
screen_height = 960
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Přestřelka')

"""
Nastavení proměnných pozadí a fontu.
"""

bg_river = pygame.transform.scale(pygame.image.load(
    os.path.join('assets', 'river_bg.png')), (screen_width, 500))
bg_grass = pygame.transform.scale(pygame.image.load(
    os.path.join('assets', 'grass_bg.png')), (screen_width, 230))
font = pygame.font.SysFont("Campus", 40)
font_color = (255, 255, 255)
start_time = time.time()
"""
Definování objektů.
"""
player = Player('player_char.png', screen_width/2 - 32, screen_height - 32, 4)
opponent = Opponent('enemy_char.png', (screen_width/2) - 32, 32, 4)
characters = pygame.sprite.Group()
characters.add(player)
characters.add(opponent)

player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()

game_manager = Manager(characters, player_bullets, enemy_bullets)
while True:
    """
    Hlavní loop, díky kterému hra poběží.
    """
    # Zpracování uživatelského vstupu
    for event in pygame.event.get():
        # Umožňuje vypnutí hry
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Převádí uživatelský vstup na akce ve hře
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                player.movement_y -= player.speed
            if event.key == pygame.K_DOWN:
                player.movement_y += player.speed
            if event.key == pygame.K_LEFT:
                player.movement_x -= player.speed
            if event.key == pygame.K_RIGHT:
                player.movement_x += player.speed
            if event.key == pygame.K_SPACE:
                player_bullets.add(player.shoot())
                player.cooldown_time = 1
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                player.movement_y += player.speed
            if event.key == pygame.K_DOWN:
                player.movement_y -= player.speed
            if event.key == pygame.K_LEFT:
                player.movement_x += player.speed
            if event.key == pygame.K_RIGHT:
                player.movement_x -= player.speed

    elapsed_time = time.time() - start_time
    # Run the game
    game_manager.run_game()

    # Obnovování okna, aby bylo možné pozorovat pohyb
    pygame.display.flip()
    clock.tick(60)

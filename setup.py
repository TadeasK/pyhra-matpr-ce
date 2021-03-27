import pygame
import sys
import os
import time

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
        # Vytvoření masky je důležité pro pozdější využití
        # v pixel-perfect kolizích
        self.mask = pygame.mask.from_surface(self.image)


class Player(Character):
    """
    Třída Player založená na tříde Character.
    Ve hře bude zastávat funkce hráčova charakteru.
    """

    def __init__(self, path, pos_x, pos_y, speed):
        """
        Díky funkci super() dědí vlastnosti path a pos_x, y z třídy Character.
        Dále dostává vlastnost speed, která bude určovat rychlost pohybu.
        """
        super().__init__(path, pos_x, pos_y)
        self.speed = speed
        self.movement_x = 0
        self.movement_y = 0

    def shoot(self):
        """
        Metoda shoot bude vytvářet projektily.
        """
        return Bullet('player_bullet.png', self.rect.centerx, self.rect.centery, characters)

    def constrain(self):
        """
        Metoda constrain zajišťuje, že nebude možné odejít z hracího pole nebo 
        vykročit mimo svou vymezenou plochu (projít řekou).
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
        self.is_hit(enemy_bullets)

    def is_hit(self, enemy_bullets):
        """
        Metoda is_hit kontroluje kolize hráče a nepřátelských projektilů.
        Využívá jednoduchou pygame builtin metodu sprite.spritecollide,
        která vrací seznam objektů, jejihž rect se střetli s rect hráče.
        Poté z tohoto listu vybere ty, u kterých vskutku došlo ke kolizi,
        na úrovni pixelů, pomocí metody collide_mask.
        """
        if pygame.sprite.spritecollide(self, enemy_bullets, False):
            hits = pygame.sprite.spritecollide(self, enemy_bullets, False)
            if pygame.sprite.collide_mask(self, hits[0]):
                enemy_bullets.remove(self, hits)
                # Game over - lost


class Bullet(Character):
    """
    Třída Bullet ve hře zastává funkčnost projektilů,
    které po sobě hráč a počítač střílí.
    """

    def __init__(self, path, pos_x, pos_y, characters):
        """
        Díky funkci super() dědí vlastnosti path a pos_x, y z třídy Character
        Dále dostává vlastnost characters, která nám poslouží kvůli kolizím 
        s hráčovým a počítačovým charakterem.
        """
        super().__init__(path, pos_x, pos_y)
        self.characters = characters

    def update(self, speed):
        """
        Metoda, která posouvá projektil.
        """
        self.rect.y += speed
        self.constrain()

    def constrain(self):
        """
        Metoda constrain smaže kulku, když opustí hrací pole (obrazovku),
        aby nedocházelo ke zpomalování hry v důsledku nekonečného množství
        kulek vykreslovaných mimo obraz.
        """
        if self.rect.top < -10 or self.rect.bottom > screen_height + 10:
            self.kill()


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
        Metoda zajišťující pohyb a střelbu oponenta.
        """
        if self.cooldown_time == 0:
            if self.rect.centerx == player.rect.centerx or abs(self.rect.centerx - player.rect.centerx) <= 64:
                enemy_bullets.add(opponent.shoot())
                self.cooldown_time = 1        
        
        if bool(player_bullets):
            for bullet in player_bullets:
                if (bullet.rect.centery <= (self.rect.centery + 200)) and (bullet.rect.centerx == self.rect.centerx or abs(bullet.rect.centerx - player.rect.centerx) <= 64):
                    if self.rect.centerx <= 640:
                        self.dodge("right")
                    if self.rect.centerx > 640:
                        self.dodge("left")
                else: 
                    if self.rect.centerx <= player.rect.centerx:
                        self.dodge("right")
                    else:
                        self.dodge("left")     
        else:
            if self.rect.centerx <= player.rect.centerx:
                self.dodge("right")
            else:
                self.dodge("left")
			
        self.constrain()
        self.is_hit(player_bullets)
        self.cooldown()

    def cooldown(self):
        """
        Metoda, která časově omezuje oponentovu střelbu, 
        jinak by mohl střílet nepřetržitě.
        """
        if self.cooldown_time >= self.CD:
            self.cooldown_time = 0
        elif self.cooldown_time > 0:
            self.cooldown_time += 1

    def shoot(self):
        """
        Metoda shoot vytvoří projektily, pokud
        metoda cooldown odpočte stanovený čas.
        """
        return Bullet('enemy_bullet.png', self.rect.centerx, self.rect.centery, characters)
        self.cooldown_time = 1

    def is_hit(self, enemy_bullets):
        """
        Metoda is_hit kontroluje kolize hráče a nepřátelských projektilů.
        Využívá jednoduchou pygame builtin metodu sprite.spritecollide,
        která vrací seznam objektů, jejihž rect se střetli s rect hráče.
        Poté z tohoto listu vybere ty, u kterých vskutku došlo ke kolizi,
        na úrovni pixelů, pomocí metody collide_mask.
        Nakonec také přičte hráči skóre.
        """
        if pygame.sprite.spritecollide(self, player_bullets, False):
            hits = pygame.sprite.spritecollide(self, player_bullets, False)
            if pygame.sprite.collide_mask(self, hits[0]):
                player_bullets.remove(self, hits)
                game_manager.score += 1000

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

    def dodge(self, direction):
        if direction == "left":
            self.rect.centerx -= self.speed
        if direction == "right":
            self.rect.centerx += self.speed

class Manager():
    score = 0
    running = True
    """
    Třída Manager dává všechno dohromady a stará se o fungování hry jako celku.
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
        Pro správné vykreslování je důležité pořadí,
        ve kterém objekty voláme.
        """
        # Kreslení pozadí
        screen.blit(bg_river, (0, 230))
        screen.blit(bg_grass, (0, 0))
        screen.blit(bg_grass, (0, 730))

        # Kreslení skupin objektů hráče, oponenta a kulek
        self.player_bullets.draw(screen)
        self.enemy_bullets.draw(screen)
        self.characters.draw(screen)

        # Volání funkce update ve skupinách objektů
        self.player_bullets.update(-8)
        self.enemy_bullets.update(+8)
        self.characters.update()

        # Vykresluje na obrazovku čas a skóre
        self.draw_score()
        self.draw_time()

    def draw_score(self):
        """
        Metoda, která bude počítat a vykreslovat skóre od začátku kola.
        Skóre bude stoupat lineárně a navíc za každé zabití oponenta.
        """
        final_score = (elapsed_time * 100) + self.score

        score_render = font.render(
            f"Score: {final_score:11.0f}", 1, font_color)

        screen.blit(score_render, (screen_width -
                    score_render.get_width() - 30, 30))
        
        if final_score >= 50000:
            # game over - won
            self.running = False


    def draw_time(self):
        """
        Metoda, která bude počítat čas od začátku kola.
        """
        time_render = font.render(f"Time: {elapsed_time:9.2f}", 1, font_color)

        screen.blit(time_render, (30, 30))

    def main_menu(self):
        run = True
        while run:
            menu_caption = menu_font.render("Main Menu", 1, menu_color)
            run_caption = font.render("To start the game press Enter ...", 1, menu_color)
            controls_caption = font.render("To see the controls press C ...", 1, menu_color)

            # Zpracování uživatelských vstupů
            for event in pygame.event.get():
                # Umožňuje vypnutí hry
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Převádí uživatelský vstup na akce v menu    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.main_loop()
                        run = False
                    if event.key == pygame.K_DOWN:
                        player.movement_y += player.speed
                    if event.key == pygame.K_LEFT:
                        player.movement_x -= player.speed


            screen.blit(bg_river_menu, (0, 230))
            screen.blit(bg_grass_menu, (0, 0))
            screen.blit(bg_grass_menu, (0, 730))
            screen.blit(menu_caption, (screen_width/2 - menu_caption.get_width()/2, 250))
            screen.blit(run_caption, (screen_width/2 - run_caption.get_width()/2, screen_height/2))
            screen.blit(controls_caption, (screen_width/2 - controls_caption.get_width()/2, screen_height/2 + 200))
            pygame.display.flip()
    
    def main_loop(self):
        elapsed_time = 0
        while self.running:
            """
            Hlavní loop, díky kterému hra poběží.
            """
            # Počítá čas od začátku hry
            elapsed_time = time.time() - start_time

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
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        player.movement_y += player.speed
                    if event.key == pygame.K_DOWN:
                        player.movement_y -= player.speed
                    if event.key == pygame.K_LEFT:
                        player.movement_x += player.speed
                    if event.key == pygame.K_RIGHT:
                        player.movement_x -= player.speed

            # Spouští procesy, díky kterým hra běží
            game_manager.run_game()

            # Obnovování okna, aby bylo možné pozorovat pohyb
            pygame.display.flip()
            clock.tick(60)


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
bg_river_menu = pygame.transform.scale(pygame.image.load(
    os.path.join('assets', 'river_bg_menu.png')), (screen_width, 500))
bg_grass_menu = pygame.transform.scale(pygame.image.load(
    os.path.join('assets', 'grass_bg_menu.png')), (screen_width, 230))

font = pygame.font.SysFont("Campus", 40)
menu_font = pygame.font.SysFont("Campus", 80)
font_color = (255, 255, 255)
menu_color = (0, 0, 0)
start_time = time.time()

"""
Vytvoření objektů.
"""
player = Player('player_char.png', screen_width/2 - 32, screen_height - 32, 4)
opponent = Opponent('enemy_char.png', (screen_width/2) - 32, 32, 4)
characters = pygame.sprite.Group()
characters.add(player)
characters.add(opponent)

player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()

game_manager = Manager(characters, player_bullets, enemy_bullets)


# Volá metodu main_menu ze třídy game_manager,
# čímž iniciuje spuštění hry.
game_manager.main_menu()
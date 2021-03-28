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
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.image = pygame.image.load(os.path.join('assets', path))
        self.rect = self.image.get_rect(center=(pos_x, pos_y))
        # Vytvoření masky je důležité pro pozdější využití
        # v pixel-perfect kolizích
        self.mask = pygame.mask.from_surface(self.image)

    def reset(self):
        """
        Metoda reset vrátí hráče a nepřítele na startovní pozici,
        zároveň resetne hráčův pohyb, kdyby při smrti/výhře
        stále držel tlačítko pro pohyb.
        """
        self.rect.centerx = self.pos_x
        self.rect.centery = self.pos_y

        self.movement_x = 0
        self.movement_y = 0

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
        # Proměnná a slovník pro obtížnost
        self.difficulty = {
            "easy": [45, 100],
            "medium": [30, 50],
            "hardcore": [0, 0],
        }
        self.diff = 0

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
                game_manager.lose_screen()


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

    def __init__(self, path, pos_x, pos_y, speed):
        """
        Díky funkci super() dědí vlastnosti path a pos_x, y z třídy Character
        Dále dostává vlastnost speed, která bude určovat rychlost pohybu.
        """
        super().__init__(path, pos_x, pos_y)
        self.speed = speed
        self.cooldown_time = 0
        self.CD = player.difficulty.get("easy")[0]

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
                if (bullet.rect.centerx - self.rect.centerx)**2 + (bullet.rect.centery - self.rect.centery)**2 <= 50000:
                    if bullet.rect.y > self.rect.centery:
                        if self.rect.centerx <= screen_width/2:
                            self.dodge("right")
                        else:
                            self.dodge("left")
                    else:
                        self.dodge_player()
        else:
            self.dodge_player()

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

    def dodge_player(self):
        if not self.rect.centerx in range(player.rect.centerx - 5, player.rect.centerx + 6):
            if self.rect.centerx < player.rect.centerx - 5:
                self.dodge("right")
            elif self.rect.centerx > player.rect.centerx + 5:
                self.dodge("left")

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
        self.start_time = time.time()
        self.elapsed_time = 0

    def run_game(self, elapsed_time):
        """
        Vykresluje a updatuje objekty.
        Pro správné vykreslování je důležité pořadí,
        ve kterém objekty voláme.
        """
        # Kreslení pozadí
        self.draw_background()

        # Kreslení skupin objektů hráče, oponenta a kulek
        self.player_bullets.draw(screen)
        self.enemy_bullets.draw(screen)
        self.characters.draw(screen)

        # Volání funkce update ve skupinách objektů
        self.player_bullets.update(-8)
        self.enemy_bullets.update(+8)
        self.characters.update()

        # Vykresluje na obrazovku čas, obtížnost a skóre
        self.draw_score()
        self.draw_time()
        self.draw_difficulty()

    def draw_score(self):
        """
        Metoda, která bude počítat a vykreslovat skóre od začátku kola.
        Skóre bude stoupat lineárně a navíc za každé zabití oponenta.
        """
        diffs = {
            0: "easy",
            1: "medium",
            2: "hardcore"
        }

        final_score = (
            self.elapsed_time * (100 + player.difficulty.get(diffs[player.diff])[1])) + self.score

        score_render = font.render(
            f"Score: {final_score: 1.0f}", 1, font_color)

        screen.blit(score_render, (screen_width -
                    score_render.get_width() - 30, 30))

        if final_score >= 50000:
            self.win_screen()

    def draw_time(self):
        """
        Metoda, která bude počítat a vykreslovat čas od začátku kola.
        """
        time_render = font.render(f"Time: {self.elapsed_time:9.2f}", 1, font_color)

        screen.blit(time_render, (30, 30))

    def draw_difficulty(self):
        """
        Metoda, která bude vykrelovat současnou obtížnost.
        """
        diffs = {
            0: "easy",
            1: "medium",
            2: "hardcore"
        }
        
        diff_render = font.render(f"Difficulty: {diffs.get(player.diff)}", 1, font_color)

        screen.blit(diff_render, (screen_width - diff_render.get_width() - 30, 90))

    def draw_background(self):
        screen.blit(bg_river, (0, 230))
        screen.blit(bg_grass, (0, 0))
        screen.blit(bg_grass, (0, 730))

    def draw_background_menus(self):
        screen.blit(bg_river_menu, (0, 230))
        screen.blit(bg_grass_menu, (0, 0))
        screen.blit(bg_grass_menu, (0, 730))

    def main_menu(self):
        """
        Metoda main_menu spouští herní menu.
        Je z něj možné zobrazit ovládání či zapnout hru.
        """
        if not self.elapsed_time == 0:
            self.start_time = time.time()
            self.score = 0
            self.enemy_bullets.empty()
            self.player_bullets.empty()

        while True:
            menu_caption = menu_font.render("Main Menu", 1, menu_color)
            run_caption = font.render(
                "To start the game press Enter ...", 1, menu_color)
            controls_caption = font.render(
                "To see the controls press C ...", 1, menu_color)

            # Zpracování uživatelských vstupů
            for event in pygame.event.get():
                # Umožňuje vypnutí hry
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Převádí uživatelský vstup na akce v menu
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.running = True
                        self.main_loop()
                    if event.key == pygame.K_c:
                        self.controls()

            self.draw_background_menus()
            screen.blit(menu_caption, (screen_width/2 -
                        menu_caption.get_width()/2, 250))
            screen.blit(run_caption, (screen_width/2 -
                        run_caption.get_width()/2, screen_height/2))
            screen.blit(controls_caption, (screen_width/2 -
                        controls_caption.get_width()/2, screen_height - 220))
            pygame.display.flip()

    def controls(self):
        """
        Metoda controls zobrazuje ovládání.
        Dá se z ní dostat zpět do main menu.
        """

        while True:
            controls_caption = menu_font.render("Controls", 1, menu_color)
            menu_caption = font.render(
                "To go back to the main menu press P ...", 1, menu_color)
            movement_caption = font.render(
                "To move your character use the arrow keys.", 1, menu_color)
            shoot_caption = font.render(
                "To shoot at the enemy use your spacebar.", 1, menu_color)

            # Zpracování uživatelských vstupů
            for event in pygame.event.get():
                # Umožňuje vypnutí hry
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Převádí uživatelský vstup na akce v menu
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.main_menu()
                        run = False

            self.draw_background_menus()
            screen.blit(controls_caption, (screen_width/2 -
                        controls_caption.get_width()/2, 250))
            screen.blit(menu_caption, (screen_width/2 -
                        menu_caption.get_width()/2, screen_height - 220))
            screen.blit(movement_caption, (screen_width/2 -
                        movement_caption.get_width()/2, 470))
            screen.blit(shoot_caption, (screen_width/2 -
                        shoot_caption.get_width()/2, 570))
            pygame.display.flip()

    def pause_menu(self):
        """
        Metoda pause menu se ukáže když hráč pozastaví hru.
        Může pokračovat zpět do hry nebo do main menu, čímž hru resetne.
        """

        while True:
            pause_caption = menu_font.render("Game Paused", 1, menu_color)
            run_caption = font.render(
                "To continue the game press Enter ...", 1, menu_color)
            reset_caption = font.render(
                "To go to the main menu and reset the game press P again...", 1, menu_color)

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
                    if event.key == pygame.K_p:
                        self.running = False
                        self.main_menu()

            self.draw_background_menus()
            screen.blit(pause_caption, (screen_width/2 -
                        pause_caption.get_width()/2, 250))
            screen.blit(run_caption, (screen_width/2 -
                        run_caption.get_width()/2, screen_height/2))
            screen.blit(reset_caption, (screen_width/2 -
                        reset_caption.get_width()/2, screen_height - 220))
            pygame.display.flip()

    def win_screen(self):
        """
        Win screen se ukáže pokud hráč vyhraje level.
        Může se z ní vrátit do main menu a pokračovat dalším levelem.
        """

        while True:
            win_caption = menu_font.render("You have won!", 1, menu_color)
            level_caption = font.render(
                "To continue to the next difficulty press Enter.", 1, menu_color)
            menu_caption = font.render(
                "To go back to the main menu press P ...", 1, menu_color)

            # Zpracování uživatelských vstupů
            for event in pygame.event.get():
                # Umožňuje vypnutí hry
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Převádí uživatelský vstup na akce v menu
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # next level
                        player.diff += 1
                        if player.diff >= 3:
                            player.diff = 0
                        diffs = {
                            0: "easy",
                            1: "medium",
                            2: "hardcore"
                        }
                        opponent.CD = player.difficulty[diffs[player.diff]][0]
                        player.reset()
                        opponent.reset()
                        self.main_menu()
                        

                    if event.key == pygame.K_p:
                        self.main_menu()

            self.draw_background_menus()
            screen.blit(win_caption, (screen_width/2 -
                        win_caption.get_width()/2, 250))
            screen.blit(level_caption, (screen_width/2 -
                        level_caption.get_width()/2, screen_height/2))
            screen.blit(menu_caption, (screen_width/2 -
                        menu_caption.get_width()/2, screen_height - 220))
            pygame.display.flip()

    def lose_screen(self):
        """
        Lose screen se ukáže, pokud nepřítel zasáhne hráče.
        """
        while True:
            lose_caption = menu_font.render(
                "You have been killed ...", 1, menu_color)
            menu_caption = font.render(
                "To go back to the main menu press P ...", 1, menu_color)

            # Zpracování uživatelských vstupů
            for event in pygame.event.get():
                # Umožňuje vypnutí hry
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Převádí uživatelský vstup na akce v menu
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        player.reset()
                        opponent.reset()
                        self.main_menu()

            self.draw_background_menus()
            screen.blit(lose_caption, (screen_width/2 -
                        lose_caption.get_width()/2, 250))
            screen.blit(menu_caption, (screen_width/2 -
                        menu_caption.get_width()/2, screen_height - 220))
            pygame.display.flip()

    def main_loop(self):
        self.elapsed_time = 0

        while self.running:
            """
            Hlavní loop, díky kterému hra poběží.
            """
            # Počítá čas od začátku hry
            self.elapsed_time = time.time() - self.start_time

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
                    if event.key == pygame.K_p:
                        self.pause_menu()
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
            game_manager.run_game(self.elapsed_time)

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

"""
Vytvoření objektů.
"""

player = Player('player_char.png', screen_width/2 - 32, screen_height - 32, 4)
opponent = Opponent('enemy_char.png', (screen_width/2) - 32, 32, 10)
characters = pygame.sprite.Group()
characters.add(player)
characters.add(opponent)

player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()

game_manager = Manager(characters, player_bullets, enemy_bullets)

# Volá metodu main_menu ze třídy game_manager,
# čímž iniciuje spuštění hry.
game_manager.main_menu()

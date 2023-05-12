from engine import *
import colorsys


def hsv2rgb(h, s, v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))


class Menu:
    def __init__(self, game, items, font, window):
        self.game = game
        self.items = items
        self.font = pg.font.Font(font, 36)
        self.window = window
        self.centerx = self.game.window.get_width() - (self.game.window.get_width() / 3)
        self.top = self.game.window.get_height() / 2
        self.gap = 50
        self.selected = 0

    def turn(self):
        self.game.interface_enabled = self.game.menu_active
        self.game.menu_active = not self.game.menu_active
        self.selected = 0

    def draw(self):
        font = pg.font.Font(None, 26)
        text = font.render("MissedCalls 0.0.2", 1, (255, 255, 255))
        textpos = text.get_rect(centerx=self.window.get_width() / 2, centery=self.window.get_height() - 30)
        self.window.blit(text, textpos)
        for i, item in enumerate(self.items):
            color = [150 * int(self.selected == i)]*3
            text = self.font.render(item, True, color)
            textpos = text.get_rect(centerx=self.centerx, centery=self.top + i * self.gap)
            self.window.blit(text, textpos)

    def handle_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_DOWN:
                self.selected = (self.selected + 1) % len(self.items)
            elif event.key == pg.K_UP:
                self.selected = (self.selected - 1) % len(self.items)
            elif event.key == pg.K_RETURN:
                if self.selected == 0:
                    self.turn()
                elif self.selected == 1:
                    pg.quit()

        pg.time.delay(50)


class Game:
    pg.init()
    config = eval(open('data/config.json', 'r').read())
    SCREEN = WIDTH, HEIGHT = config["RESOLUTION"]
    FPS = config["FPS"]
    center = WIDTH // 2, HEIGHT // 2
    window = pg.display.set_mode(SCREEN, eval('pg.' + config["MODE"]))
    pg.display.set_caption('Missed Calls')
    icon = pg.image.load('icon.png')
    pg.display.set_icon(icon)
    clock = pg.time.Clock()
    play = True
    frame = 0
    modifier = 4

    def __init__(self):
        self.LEVEL = Level(self, 'data/levels/test_1/main.dat')
        bgcolor = [0.3, 0.5, 0.3]
        self.menu = Menu(self, ["Continue", "Quit"], None, self.window)
        self.menu_active = False
        while self.play:
            self.interface_enabled = True
            pg.mouse.set_visible(self.menu_active)
            self.frame = (self.frame + 1) % 64
            keys = pg.key.get_pressed()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.play = False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 4:  # прокрутка колеса мыши вверх
                        self.modifier *= 1.2
                    elif event.button == 5:  # прокрутка колеса мыши вниз
                        self.modifier /= 1.2
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.menu_active = not self.menu_active

            if self.menu_active:
                self.menu.handle_event(event)
                self.window.fill(hsv2rgb(*bgcolor))
                bgcolor[0] = (bgcolor[0] + 0.0005) % 1
                self.LEVEL.draw()
                self.menu.draw()
                pg.display.update()
                continue

            self.LEVEL.update(keys)
            self.window.fill(hsv2rgb(*bgcolor))
            bgcolor[0] = (bgcolor[0] + 0.0005) % 1

            self.LEVEL.draw()

            pg.display.update()
            self.clock.tick(self.FPS)
        pg.quit()




Game()
from engine import *
import colorsys
def hsv2rgb(h,s,v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))


class Game():
    pg.init()
    SCREEN = WIDTH, HEIGHT = 1500, 700
    FPS = 60
    center = WIDTH // 2, HEIGHT // 2
    window = pg.display.set_mode(SCREEN, pg.SCALED)
    clock = pg.time.Clock()
    play = True
    frame = 0
    modifier = 4

    def __init__(self):
        self.LEVEL = Level(self, 'data/levels/test_1/main.dat')

        bgcolor = [0.3, 0.5, 0.3]
        while self.play:
            self.frame = (self.frame + 1) % 64
            keys = pygame.key.get_pressed()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.play = False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 4:  # прокрутка колеса мыши вверх
                        self.modifier *= 1.2
                    elif event.button == 5:  # прокрутка колеса мыши вниз
                        self.modifier /= 1.2
                self.modifier = max(min(self.modifier, 7.0), 2.5)

            self.LEVEL.update(keys)
            self.window.fill(hsv2rgb(*bgcolor))
            bgcolor[0] = (bgcolor[0] + 0.0005) % 1

            self.LEVEL.draw()

            pg.display.update()
            self.clock.tick(self.FPS)
        pg.quit()

Game()
import pygame as pg
from spritesheets import *
import os, sys, time
from math import atan2, degrees, pi

colorkey = pg.SRCALPHA


def get_angle_between(pos1, pos2):
    dx, dy = pos1[0] - pos2[0], pos1[1] - pos2[1]
    rads = atan2(-dy, dx)
    rads %= 2 * pi
    return degrees(rads) - 180


def game_clock():
    current_time = pygame.time.get_ticks()
    return current_time


def rot_center(image, angle, x, y):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(center=(x, y)).center)
    return rotated_image, new_rect


class Camera:
    def __init__(self, game, target, pos=[-1000, -1000]):
        self.game = game
        self.pos = pos
        self.target = target

    def update(self):
        slowing_factor = 0.1
        cursor_pos = self.game.LEVEL.cursor.pos[0] - self.game.SCREEN[0]/2, self.game.LEVEL.cursor.pos[1] - self.game.SCREEN[1]/2
        print(cursor_pos)
        self.pos = ((self.target.pos[0] - self.pos[0]) * slowing_factor + self.pos[0]) + cursor_pos[0] / self.game.SCREEN[0]*10, (
                (self.target.pos[1] - self.pos[1]) * slowing_factor + (self.pos[1])) + cursor_pos[1] / self.game.SCREEN[1]*10


class Entity:
    def __init__(self, game, sprites, state=None, anwait=0.1, size=(128, 128), direct=0, friction=0.9):
        self.game = game
        self.sprites = sprites
        self.anwait = anwait
        self.pos = [0, 0]
        self.state = state
        self.speed = [0, 0]
        self.friction = friction
        self.direct = direct
        self.anim = 0
        self.next_frame = game_clock() + self.anwait

    def get_anim_len(self):
        return len(self.sprites[self.state])

    def update(self, keys):
        if game_clock() >= self.next_frame:
            self.anim += 1
            self.next_frame = game_clock() + self.anwait
        self.anim = self.anim % self.get_anim_len()
        self.speed = [self.speed[0] * self.friction, self.speed[1] * self.friction]
        self.pos[0] += self.speed[0]
        self.pos[1] += self.speed[1]

    def draw(self):
        self.game.window.blit()


class Cursor(Entity):
    def __init__(self, game):
        self.game = game
        self.anwait = 100
        self.sprites = {'idle': spritesheet('data/sprites/UI/sprCursor.png').images_at([(0,0,11,11), (11, 0, 11, 11),
                                                                            (22, 0, 11, 11), (33, 0, 11, 11),
                                                                            (44, 0, 11, 11), (55, 0, 11, 11),
                                                                            (66, 0, 11, 11), (77, 0, 11, 11),
                                                                            (88, 0, 11, 11), (99, 0, 11, 11),
                                                                            ])}
        self.state = 'idle'
        self.anim = 0
        self.pos = list(pygame.mouse.get_pos())
        super(Cursor, self).__init__(game, self.sprites, self.state, anwait=self.anwait)


    def update(self, keys):
        self.pos = list(pygame.mouse.get_pos())
        super().update(keys)

    def draw(self):
        sprite = self.sprites[self.state][self.anim]
        sprite_scale = sprite.get_rect()[2:4]
        sprite = pg.transform.scale(sprite, (
            int(sprite_scale[0] * self.game.modifier), int(sprite_scale[1] * self.game.modifier)))
        pos = (self.pos[0]), (self.pos[1])
        sprite = rot_center(sprite, 0, *pos)
        self.game.window.blit(*sprite)


class Player(Entity):
    def __init__(self, game, sprites, state='idle', anwait=0.1, legs_state='idle', direct=0, friction=0.8):
        super().__init__(game, sprites, state=state, anwait=anwait, direct=direct, friction=friction)
        self.legs_state = 'idle'
        self.speed_mod = 0.8

    def update(self, keys):
        self.direct = get_angle_between(self.game.center, pg.mouse.get_pos())
        speedm = self.speed_mod
        if keys[pg.K_a]:
            self.speed[0] -= speedm
        if keys[pg.K_d]:
            self.speed[0] += speedm
        if keys[pg.K_w]:
            self.speed[1] -= speedm
        if keys[pg.K_s]:
            self.speed[1] += speedm
        super().update(keys)


class Biker(Player):
    def __init__(self, game):
        self.attacking = False
        biker = spritesheet('data/sprites/characters/biker.png')
        self.sprites = {'idle': (biker.image_at((210, 225, 32, 32)),),
                        'walking_meatcleaver': biker.images_at(((210, 225, 32, 32), (210, 258, 32, 32),
                                                                (210, 291, 32, 32), (210, 324, 32, 32),
                                                                (210, 357, 32, 32), (210, 390, 32, 32),
                                                                (210, 357, 32, 32), (210, 324, 32, 32),
                                                                )),
                        'walking_unarmed': biker.images_at(((240, 225, 31, 32), (240, 258, 31, 32),
                                                            (240, 291, 31, 32), (240, 324, 31, 32),
                                                            (240, 357, 31, 32), (240, 390, 31, 32))),
                        'attack_meatcleaver': biker.images_at(((67, 106, 41, 41), (67, 106, 41, 41), (67, 147, 41, 41),
                                                               (67, 188, 41, 41), (67, 229, 41, 41), (67, 270, 41, 41)))

                        }
        self.game = game
        super().__init__(game, self.sprites, state='idle', anwait=100)

    def update(self, keys):
        if pygame.mouse.get_pressed()[0] or self.attacking:
            if self.state != 'attack_meatcleaver':
                self.anim = 0
            self.state = 'attack_meatcleaver'
            self.attacking = True
            self.anwait = 50
            if self.anim >= self.get_anim_len() - 1:
                self.attacking = False
                self.anwait = 100
        elif (abs(self.speed[0] * self.speed_mod * 2) + abs(self.speed[1] * self.speed_mod * 2)) // 2 > 0:
            self.state = 'walking_meatcleaver'
        else:
            self.state = 'idle'
        super().update(keys)

    def draw(self):
        sprite = self.sprites[self.state][self.anim]
        sprite_scale = sprite.get_rect()[2:4]
        sprite = pg.transform.scale(sprite, (
            int(sprite_scale[0] * self.game.modifier), int(sprite_scale[1] * self.game.modifier)))
        pos = ((self.pos[0] - self.game.camera.pos[0]) * self.game.modifier + self.game.SCREEN[0] // 2,
               (self.pos[1] - self.game.camera.pos[1]) * self.game.modifier + self.game.SCREEN[1] // 2)
        sprite = rot_center(sprite, self.direct, *pos)
        self.game.window.blit(*sprite)


class Level():
    def __init__(self, game, folder):
        self.game = game
        self.layers = [[], [], []]
        self.entities = []
        self.load_level(folder)
        self.cursor = Cursor(self.game)

    def update(self, keys):
        for entity in self.entities:
            entity.update(keys)
        self.game.camera.update()
        self.cursor.update(keys)

    def draw(self):
        for layer in self.layers:
            for object in layer:
                object.draw()
        self.cursor.draw()

    def add(self, *items):
        for item in items:
            self.entities.append(item)

    def add_drawable(self, layer, *items):
        self.add(*items)
        if len(self.layers) >= layer:
            for item in items:
                self.layers[layer].append(item)

    def load_level(self, folder):
        with open(folder, 'r') as json:
            json = json.read()
            json = eval(json)
            self.player = eval(json['player'])
            for layer in range(len(json['layers'])):
                for item in range(len(json['layers'][layer])):
                    text = json['layers'][layer][item]
                    if text[0] == 'Tile':
                        if len(text) > 6:
                            self.layers[layer].append(eval(
                                f'Tile(self.game, {text[1]}, {text[2]}, spritesheet("{text[3]}").image_at({text[4]}, {text[5]}), {text[6]})'))
                        else:
                            self.layers[layer].append(eval(
                                f'Tile(self.game, {text[1]}, {text[2]}, spritesheet("{text[3]}").image_at({text[4]}, {text[5]}))'))
            self.layers[1].append(self.player)
            self.entities.append(self.player)
            self.game.camera = Camera(self.game, self.player)  # define a camera
            print(self.entities, self.layers, self.player)


class Tile():
    def __init__(self, game, x, y, sprite, transparency=255):
        self.game = game
        self.pos = [x, y]
        self.spritest = sprite
        self.t = transparency
        sprite_scale = sprite.get_rect()[2:4]
        sprite = pg.transform.scale(sprite,
                                    (sprite_scale[0] * self.game.modifier, sprite_scale[1] * self.game.modifier))
        self.sprite = sprite
        self.sprite.set_alpha(self.t)

    def update(self, keys):
        pass

    def draw(self):
        sprite_scale = self.spritest.get_rect()[2:4]
        self.sprite = pg.transform.scale(self.spritest,
                                         (int(sprite_scale[0] * self.game.modifier),
                                          int(sprite_scale[1] * self.game.modifier)))
        self.sprite.set_alpha(self.t)
        pos = ((self.pos[0] - self.game.camera.pos[0]) * self.game.modifier + self.game.SCREEN[0] // 2,
               (self.pos[1] - self.game.camera.pos[1]) * self.game.modifier + self.game.SCREEN[1] // 2)
        self.game.window.blit(self.sprite, pos)

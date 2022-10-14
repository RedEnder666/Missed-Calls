import pygame as pg
from spritesheets import *
import os, sys, time
from math import atan2, degrees, pi
colorkey = pg.SRCALPHA
modifier = 4

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

    def prepare(self):
        self.window = self.game.window

    def get_anim_len(self):
        return len(self.sprites[self.state])

    def update(self, keys):
        if game_clock() >= self.next_frame:
            self.anim +=  1
            self.next_frame = game_clock() + self.anwait
        self.anim = self.anim % self.get_anim_len()
        self.speed = [self.speed[0] * self.friction, self.speed[1] * self.friction]
        self.pos[0] += self.speed[0]
        self.pos[1] += self.speed[1]

    def draw(self):
        self.window.blit()


class Player(Entity):
    def __init__(self, game, sprites, state='idle', anwait=0.1, legs_state='idle', direct=0, friction=0.75):
        super().__init__(game, sprites, state, anwait, legs_state, direct, friction)
        self.legs_state='idle'


    def update(self, keys):
        self.direct = get_angle_between(self.game.center, pg.mouse.get_pos())
        speedm = 0.7
        if keys[pg.K_a]:
            self.speed[0] -= modifier * speedm
        if keys[pg.K_d]:
            self.speed[0] += modifier * speedm
        if keys[pg.K_w]:
            self.speed[1] -= modifier * speedm
        if keys[pg.K_s]:
            self.speed[1] += modifier * speedm
        super().update(keys)


class Biker(Player):
    def __init__(self, game):
        biker = spritesheet('data/sprites/characters/biker.png')
        self.sprites = {'idle': (biker.image_at((210, 225, 32, 32)),),
                        'walking_meatcleaver': biker.images_at(((210, 225, 32, 32), (210, 258, 32, 32),
                                                                              (210, 291, 32, 32), (210, 324, 32, 32),
                                                                              (210, 357, 32, 32), (210, 390, 32, 32),
                                                                              (210, 357, 32, 32), (210, 324, 32, 32),
                                                                              )),
                        'walking_unarmed': biker.images_at(((240, 225, 31, 32), (240, 258, 31, 32),
                                                                         (240, 291, 31, 32), (240, 324, 31, 32),
                                                                         (240, 357, 31, 32), (240, 390, 31, 32)))

                        }
        self.game = game
        super().__init__(game, self.sprites, state='idle', anwait=100)


    def update(self, keys):
        if (abs(self.speed[0])+abs(self.speed[1]))//2 > 0.5:
            self.state='walking_meatcleaver'
        else:
            self.sprites['idle'] = self.sprites[self.state][self.anim],
            self.state='idle'
        super().update(keys)


    def draw(self):
        sprite = self.sprites[self.state][self.anim]
        sprite_scale = sprite.get_rect()[2:4]
        sprite = pg.transform.scale(sprite, (sprite_scale[0]*modifier, sprite_scale[1]*modifier))
        sprite = rot_center(sprite, self.direct, self.game.center[0], self.game.center[1])
        self.game.window.blit(*sprite)


class Level():
    def __init__(self, game, folder):
        self.game = game
        self.layers = [[], [], []]
        self.entities = []
        self.load_level(folder)
        for i in self.entities:
            i.prepare()

    def update(self, keys):
        for entity in self.entities:
            entity.update(keys)

    def draw(self):
        for layer in self.layers:
            for object in layer:
                object.draw()

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
                    self.layers[layer].append(eval(f'{text[0]}(self.game, {text[1]}, {text[2]}, spritesheet("{text[3]}").image_at({text[4]}, {text[5]}))'))
            self.layers[1].append(self.player)
            self.entities.append(self.player)
            print(self.entities, self.layers, self.player)


class Tile():
    def __init__(self, game, x, y, sprite):
        self.game = game
        self.pos = [x, y]
        sprite_scale = sprite.get_rect()[2:4]
        sprite = pg.transform.scale(sprite, (sprite_scale[0]*modifier, sprite_scale[1]*modifier))
        self.sprite = sprite

    def update(self, keys):
        pass

    def draw(self):
        pos = self.pos[0] * modifier - self.game.LEVEL.player.pos[0], self.pos[1] * modifier - self.game.LEVEL.player.pos[1]
        self.game.window.blit(self.sprite, pos)


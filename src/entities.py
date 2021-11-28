#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
Ces classes ne sont pas fonctionnelles
Ce fichier a pour vocation de remplacer 'player.py' et 'npc.py'
"""


import pygame as pg


class Entity(pg.sprite.Sprite):
    def __init__(self, game):
        super().__init__()

        self.game = game
        self.spritesheet = pg.image.load('res/textures/player.png')
        self.rect = self.image.get_rect()

    def draw(self):
        self.game.screen.blit(self.image, self.rect)


class Player(Entity):
    def __init__(self, game):
        super().__init__(game)

    def move_right(self):
        self.position[0] += self.walk_speed

    def move_left(self):
        self.position[0] -= self.walk_speed

    def move_down(self):
        self.position[1] += self.walk_speed

    def move_up(self):
        self.position[1] -= self.walk_speed

    def update(self):
        pressed_keys = pg.key.get_pressed()
        if pressed[pg.K_UP]:
            self.player.move_up()
            self.player.change_animation('up')
        elif pressed[pg.K_DOWN]:
            self.player.move_down()
            self.player.change_animation('down')
        elif pressed[pg.K_LEFT]:
            self.player.move_left()
            self.player.change_animation('left')
        elif pressed[pg.K_RIGHT]:
            self.player.move_right()
            self.player.change_animation('right')
        else:
            self.player.is_animated = False


class Npc(Entity):
    def __init__(self, game):
        super().__init__(game)

    def talk(self):
        pass

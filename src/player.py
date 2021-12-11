#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Gère le joueur"""

import pygame as pg

class Player(pg.sprite.Sprite):

    SPEED_NORMALISATION = 1/(2**0.5)
    BASE_WALK_SPEED = 1.5 #Vitesse du joueur sans multiplicateur (en m/frame)
    SPRINT_WALK_SPEED_MULTIPLIER = 1.75 #Multiplicateur de vitesse en cas de sprint
    WALK_ANIMATION_COOLDOWN = 8 #Cooldown entre deux changements d'animations (en frames)
    SPRINT_ANIMATION_COOLDOWN = 3 #Cooldown entre deux changements d'animations (en frames)

    def __init__(self, x, y, game):
        super().__init__()
        self.game = game
        self.is_animated = False
        self.is_sprinting = False
        self.is_talking = False
        self.sprite_sheet = pg.image.load('res/textures/player.png')
        self.image = self.get_image(0, 0)  # en bas par défaut
        self.image.set_colorkey([0, 0, 0])  # transparence
        self.rect = self.image.get_rect()  # rectangle autour du joueur
        self.position = [x, y]
        self.feet = pg.Rect(0, 0, self.rect.width * 0.5, 12)
        self.old_position = self.position.copy()
        self.images = {
            'down': [self.get_image(0, 0), self.get_image(32, 0), self.get_image(64, 0)],
            'left': [self.get_image(0, 32), self.get_image(32, 32), self.get_image(64, 32)],
            'right': [self.get_image(0, 64), self.get_image(32, 64), self.get_image(64, 64)],
            'up': [self.get_image(0, 96), self.get_image(32, 96), self.get_image(64, 96)]
        }
        self.current_sprite = 0

    def change_animation(self, sens):  # change l'image en fonction du sens 'sens'
        self.image = self.images[sens][int(self.current_sprite)]
        self.image.set_colorkey([0, 0, 0])  # transparence

    def move(self, list_directions, sprinting):
        if not self.is_talking:
            number_directions = list_directions.count(True)
            speed_multiplier = self.SPRINT_WALK_SPEED_MULTIPLIER if sprinting else 1
            self.is_sprinting = True if sprinting else False
            speed_normalisation = self.SPEED_NORMALISATION if number_directions == 2 else 1
            self.is_animated = False if number_directions in [0,4] else True
            if list_directions[0]: #Haut
                self.position[1] -= self.BASE_WALK_SPEED*speed_multiplier*speed_normalisation
                self.change_animation('up')
            if list_directions[1]: #Droite
                self.position[0] += self.BASE_WALK_SPEED*speed_multiplier*speed_normalisation
                self.change_animation('right')
            if list_directions[2]: #Bas
                self.position[1] += self.BASE_WALK_SPEED*speed_multiplier*speed_normalisation
                self.change_animation('down')
            if list_directions[3]: #Gauche
                self.position[0] -= self.BASE_WALK_SPEED*speed_multiplier*speed_normalisation
                self.change_animation('left')

    def update(self):  # mettre à jour la position
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom
        animation_cooldown = self.SPRINT_ANIMATION_COOLDOWN if self.is_sprinting else self.WALK_ANIMATION_COOLDOWN
        if self.is_animated == True:
            self.current_sprite = (int(self.game.tick_count/animation_cooldown) % 3)

    # retourne un 'bout' de l'image 'player.png' en fonction de ses coordonées x,y
    def get_image(self, x, y):
        image = pg.Surface([32, 32])
        image.blit(self.sprite_sheet, (0, 0), (x, y, 32, 32))
        return image

    def save_location(self):
        self.old_position = self.position.copy()

    def update_player(self):  # est appelée à chaques tick
        self.save_location()

    def move_back(self):
        self.position = self.old_position
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom

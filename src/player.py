#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pygame as pg
from text import *


class Player(pg.sprite.Sprite):

    SPEED_NORMALISATION = 1/(2**0.5)
    BASE_WALK_SPEED = 1.5 #Vitesse du joueur sans multiplicateur (en m/frame)
    SPRINT_WALK_SPEED_MULTIPLIER = 1.75 #Multiplicateur de vitesse en cas de sprint
    WALK_ANIMATION_COOLDOWN = 5 #Cooldown entre deux changements d'animations (en frames)

    def __init__(self, x, y, game):
        super().__init__()
        self.game = game
        self.dialogue = game.dialogue
        self.is_animated = False
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
        number_directions = list_directions.count(True)
        speed_multiplier = self.SPRINT_WALK_SPEED_MULTIPLIER if sprinting else 1
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
        if self.is_animated == True:
            self.current_sprite = (int(self.game.tick_count/self.WALK_ANIMATION_COOLDOWN) % 3)

    # retourne un 'bout' de l'image 'player.png' en fonction de ses coordonées x,y
    def get_image(self, x, y):
        image = pg.Surface([32, 32])
        image.blit(self.sprite_sheet, (0, 0), (x, y, 32, 32))
        return image

    def save_location(self):
        self.old_position = self.position.copy()

    def update_player(self):  # est appelée à chaques tick
        self.save_location()
        self.dialogue.update_dialogue()

    def move_back(self):
        self.position = self.old_position
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom

    def space_pressed(self):  # quand espace est pressé
        self.dialogue.input_from_player()

    def can_talk(self):
        # si il est en collision avec un mec du groupe "group_target"
        if pg.sprite.spritecollide(self, self.game.map.group_npc, False):
            self.is_talking = True
            self.dialogue.init_dial(
                self.game.map.group_npc.sprites()[0])

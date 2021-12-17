#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Gère le joueur"""

import pygame as pg
import save

class Player(pg.sprite.Sprite):

    TEXTURE_FILE_LOCATION = 'res/textures/player.png'

    SPEED_NORMALISATION = 1/(2**0.5)
    SPRINT_WALK_SPEED_MULTIPLIER = 1.75 #Multiplicateur de vitesse en cas de sprint
    WALK_ANIMATION_COOLDOWN = 8 #Cooldown entre deux changements d'animations (en frames)
    SPRINT_ANIMATION_COOLDOWN = 3 #Cooldown entre deux changements d'animations (en frames)

    FEET_SIZE = 12

    ANIMATION_DICT = {
    "1,1" : "down-right",
    "1,0" : "right",
    "0,1" : "down",
    "1,-1" : "up-right",
    "0,-1" : "up",
    "-1,1" : "down-left",
    "-1,0" : "left",
    "-1,-1" : "up-left"}

    def __init__(self, game):
        super().__init__()
        self.game = game

        #Etat
        self.is_animated = False
        self.is_sprinting = False
        self.is_talking = False

        config = save.load_player_config()
        self.position = config["position"]
        self.base_walk_speed = config["speed"] #Vitesse du joueur sans multiplicateur (en pixel/frame)

        #Graphique
        self.sprite_sheet = pg.image.load(self.TEXTURE_FILE_LOCATION)
        self.image = self.get_image(0, 0)  # en bas par défaut
        self.image.set_colorkey([0, 0, 0])  # transparence
        self.rect = self.image.get_rect()  # rectangle autour du joueur
        self.feet = pg.Rect(0, 0, self.rect.width * 0.5, self.FEET_SIZE)

        self.current_sprite = 0

        self.IMAGES = {
        'down': [self.get_image(0, 0), self.get_image(32, 0), self.get_image(64, 0)],
        'down-left': [self.get_image(0, 0), self.get_image(32, 0), self.get_image(64, 0)],
        'down-right': [self.get_image(0, 0), self.get_image(32, 0), self.get_image(64, 0)],
        'left': [self.get_image(0, 32), self.get_image(32, 32), self.get_image(64, 32)],
        'right': [self.get_image(0, 64), self.get_image(32, 64), self.get_image(64, 64)],
        'up': [self.get_image(0, 96), self.get_image(32, 96), self.get_image(64, 96)],
        'up-left': [self.get_image(0, 96), self.get_image(32, 96), self.get_image(64, 96)],
        'up-right': [self.get_image(0, 96), self.get_image(32, 96), self.get_image(64, 96)]
        }

    def close(self):
        save.save_player_config(self.game.map_manager.map_id, self.position, self.base_walk_speed)

    def change_animation(self, direction):  # change l'image en fonction du sens 'sens'
        animation = self.ANIMATION_DICT[str(direction[0])+","+str(direction[1])]
        self.image = self.IMAGES[animation][int(self.current_sprite)]
        self.image.set_colorkey([0, 0, 0])  # transparence

    def is_colliding(self):
        return True if self.feet.collidelist(self.game.map_manager.walls) > -1 else False

    def move(self, list_directions, sprinting):
        if list_directions.count(True) > 0:
            if not self.is_talking:
                speed_multiplier = self.SPRINT_WALK_SPEED_MULTIPLIER if sprinting else 1
                self.is_sprinting = True if sprinting else False
                deplacement = [0, 0]
                if list_directions[0]: #Haut
                    deplacement[1] -= 1
                if list_directions[1]: #Droite
                    deplacement[0] += 1
                if list_directions[2]: #Bas
                    deplacement[1] += 1
                if list_directions[3]: #Gauche
                    deplacement[0] -= 1

                if deplacement[0] != 0 or deplacement[1] != 0:

                    if deplacement[0] != 0 and deplacement[1] != 0:
                        speed_normalisation = self.SPEED_NORMALISATION
                    else:
                        speed_normalisation = 1

                    for coord_id in [0, 1]:
                        self.position[coord_id] += deplacement[coord_id]*self.base_walk_speed*speed_multiplier*speed_normalisation
                        self.rect.topleft = self.position
                        self.feet.midbottom = self.rect.midbottom

                        # Si il y a collision, on annule le dernier déplacement
                        if self.is_colliding():
                            self.position[coord_id] -= deplacement[coord_id]*self.base_walk_speed*speed_multiplier*speed_normalisation

                            self.rect.topleft = self.position
                            self.feet.midbottom = self.rect.midbottom
                    else:
                        self.is_animated = True
                        self.change_animation(deplacement)
            else:
                self.is_animated = False

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

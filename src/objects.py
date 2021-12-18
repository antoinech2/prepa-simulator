#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Gestion des objets"""

import pygame as pg
import player

class ObjectManager():
    def __init__(self, map):
        self.obj_group = pg.sprite.Group()
        self.map = map

        # Chargement de la liste des objets
        obj_list = self.map.game.game_data_db.execute("select objects.id, objects.name, x_coord, y_coord from objects join maps on objects.map_id = maps.id where maps.id = ?", (map.map_id,)).fetchall()
        for obj in obj_list:
            new_object = Object(map, obj[0], obj[1], (obj[2], obj[3]))
            self.obj_group.add(new_object)
            self.map.object_group.add(new_object)
    
    def pickup_check(self):
        obj_collide_list = pg.sprite.spritecollide(self.map.game.player, self.obj_group, False)
        if len(obj_collide_list) != 0:
            pass        # TODO Ramasser l'objet s'il existe, et le mettre dans le Sac


class Object(pg.sprite.Sprite):
    OBJ_TEX_FOLDER = "res/textures/objects/"
    OVERWORLD_TEX = "res/textures/objects/overworld.png"
    
    def __init__(self, map, id, name, coords, exists = True):
        super().__init__()
        self.map = map
        self.id = id
        self.name = name
        self.path = f"{self.OBJ_TEX_FOLDER}placeholder.png"         # TODO à remplacer par {self.name}.png lorsque le Sac sera implémenté
        self.exists = True # Temporaire. TODO Fichier events.yaml recensant les objets, ainsi self.exists pourra varier

        # Affichage du sprite, les variables sont similaires à celles de la classe Npc
        self.bag_sprite = pg.image.load(self.path)                  # Le sprite dans le sac
        self.overworld_sprite = pg.image.load(self.OVERWORLD_TEX)   # Le sprite sur la carte du monde
        self.image = pg.Surface([16, 16])
        self.image.set_colorkey([0, 0, 0])
        self.rect = self.image.get_rect()
        self.rect.topleft = coords
        self.image.blit(self.overworld_sprite, (0, 0),
                        (0, 0, 16, 16))                             # Affichage du sprite sur la carte
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Gère les NPC du jeu"""

import pygame as pg
import dialogue

#Temporaire : liste des npc
NPC_LIST = [
        {"id" : 1, "map" : "carte", "coords" : (1500, 1200)},
        {"id" : 2, "map" : "carte", "coords" : (1500, 1300)},
        {"id" : 3, "map" : "carte", "coords" : (1500, 1400)}
        ]

class NpcManager():
    def __init__(self, map):
        self.npc_group = pg.sprite.Group()
        self.map = map

        #On charge les Npc de la map
        for npc in NPC_LIST:
            if npc["map"] == map.current_map:
                new_npc = Npc(map, npc["id"], npc["coords"])
                self.npc_group.add(new_npc)
                self.map.get_group().add(new_npc)

    def check_talk(self):
        npc_collide_list = pg.sprite.spritecollide(self.map.game.player, self.npc_group, False)
        if len(npc_collide_list) != 0:
            self.map.game.dialogue = dialogue.Dialogue(self.map.game, npc_collide_list[0])


class Npc(pg.sprite.Sprite):
    TEXTURE_FILE_LOCATION = 'res/textures/player.png'

    def __init__(self, map, id, coords):
        super().__init__()
        self.map = map
        self.id = id

        #Graphique
        self.sprite_sheet = pg.image.load(self.TEXTURE_FILE_LOCATION)
        self.image = pg.Surface([32, 32])  # creation d'une image
        self.image.set_colorkey([0, 0, 0])  # transparence
        self.rect = self.image.get_rect()  # rectangle autour du joueur
        self.rect.topleft = coords  # placement du npc
        self.image.blit(self.sprite_sheet, (0, 0),
                        (0, 0, 32, 32))  # affichage du npc
        self.feet = pg.Rect(0, 0, self.rect.width * 0.5, 12)

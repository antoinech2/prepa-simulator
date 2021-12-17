#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Gère les NPC du jeu"""

import pygame as pg
import dialogue

class NpcManager():
    def __init__(self, map):
        self.npc_group = pg.sprite.Group()
        self.map = map

        #On charge les Npc de la map
        npcs = self.map.game.game_data_db.execute("SELECT npc.id, npc.nom, x_coord, y_coord, default_dia FROM npc JOIN maps ON npc.map_id = maps.id WHERE maps.id = ?", (map.map_id,)).fetchall()

        for npc in npcs:
            new_npc = Npc(map, npc[0], npc[1], (npc[2], npc[3]), npc[4])
            self.npc_group.add(new_npc)
            self.map.object_group.add(new_npc)

    def check_talk(self):
        npc_collide_list = pg.sprite.spritecollide(self.map.game.player, self.npc_group, False)
        if len(npc_collide_list) != 0:
            self.map.game.dialogue = dialogue.Dialogue(self.map.game, npc_collide_list[0])


class Npc(pg.sprite.Sprite):
    TEXTURE_FILE_LOCATION = 'res/textures/player.png'

    def __init__(self, map, id, name, coords, default_dia):
        super().__init__()
        self.map = map
        self.id = id
        self.name = name
        self.default_dia = default_dia

        #Graphique
        self.sprite_sheet = pg.image.load(self.TEXTURE_FILE_LOCATION)
        self.image = pg.Surface([32, 32])  # creation d'une image
        self.image.set_colorkey([0, 0, 0])  # transparence
        self.rect = self.image.get_rect()  # rectangle autour du joueur
        self.rect.topleft = coords  # placement du npc
        self.image.blit(self.sprite_sheet, (0, 0),
                        (0, 0, 32, 32))  # affichage du npc
        self.feet = pg.Rect(0, 0, self.rect.width * 0.5, 12)

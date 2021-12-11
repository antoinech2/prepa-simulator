#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Gère les NPC du jeu"""

import pygame as pg

#Temporaire : liste des npc
NPC_LIST = [{"map" : "carte", "coords" : (1500, 1200)}]

class NpcManager():
    def __init__(self, map):
        self.npc_group = pg.sprite.Group()
        for npc in NPC_LIST:
            if npc["map"] == map.current_map:
                new_npc = Npc(map, npc["coords"])
                self.npc_group.add()
                map.get_group().add(new_npc)

class Npc(pg.sprite.Sprite):
    def __init__(self, map, coords):
        super().__init__()
        self.map = map
        self.sprite_sheet = pg.image.load('res/textures/player.png')
        #self.dialogue = self.game.dialogue
        self.image = pg.Surface([32, 32])  # creation d'une image
        self.image.set_colorkey([0, 0, 0])  # transparence
        self.rect = self.image.get_rect()  # rectangle autour du joueur
        self.rect.topleft = coords  # placement du npc
        self.image.blit(self.sprite_sheet, (0, 0),
                        (0, 0, 32, 32))  # affichage du npc
        self.feet = pg.Rect(0, 0, self.rect.width * 0.5, 12)
        # sql : recuperation des dialogues
        self.dial = []
        #for d in self.dialogue.db_cursor.execute("SELECT texte FROM npc_1 WHERE lieu = 'debut'"):
        #    self.dial.append(d[0])

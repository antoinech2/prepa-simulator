#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
Aucune idee de comment fonctionne cette classe
J'ai juste recopie ce qu'il y avait dans game.py
Si quelqu'un veut commenter c'est pas de refus
"""


import pygame as pg
from pytmx import *
from pyscroll import *
from npc import *


class Map:
    def __init__(self, game, mapTiles: str, npcList: list):
        self.game = game
        self.tmx_data = util_pygame.load_pygame(mapTiles)
        self.map_data = data.TiledMapData(self.tmx_data)
        self.map_layer = orthographic.BufferedRenderer(self.map_data,
                                                       self.game.screen.get_size())
        self.map_layer.zoom = 2

        self.walls = []
        for obj in self.tmx_data.objects:
            if obj.type == "mur":
                self.walls.append(pg.Rect(obj.x, obj.y, obj.width, obj.height))

        self.group_npc = pg.sprite.Group()
        for npc in npcList:
            self.group_npc.add(npc)

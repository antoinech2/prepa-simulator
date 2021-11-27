#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
Aucune idee de comment fonctionne cette classe
J'ai juste recopie ce qu'il y avait dans game.py
Si quelqu'un veut commenter c'est pas de refus
"""


from pytmx import *
from pyscroll import *


class Map:
    def __init__(self, game, mapTiles:str):
        self.game = game
        self.tmx_data = util_pygame.load_pygame(mapTiles)
        self.map_data = data.TiledMapData(self.tmx_data)
        self.map_layer = orthographic.BufferedRenderer(self.map_data,
        self.game.screen.get_size())
        self.map_layer.zoom = 2

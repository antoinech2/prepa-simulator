#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pygame as pg
import pytmx , pyscroll
from dataclasses import dataclass

# for sprite in self.group.sprites():
#    if sprite.feet.collidelist(self.walls) > -1:
#        sprite.move_back()


"""
Aucune idee de comment fonctionne cette classe
J'ai juste recopie ce qu'il y avait dans game.py
Si quelqu'un veut commenter c'est pas de refus
"""
"""
 cc c'est djess je suis là pour le ménage

"""
@dataclass
class Map:
    name : str
    walls : list[pg.Rect]
    group : pyscroll.PyscrollGroup

class MapManager :

    def __init__ (self,screen,player):
        self.player = player
        self.screen = screen
        self.maps = dict()
        self.current_map = "niv_1"

        self.register_map("niv_1")
        self.register_map("chambre")
        self.register_map("carte")


    def register_map (self,name):
        tmx_data = pytmx.util_pygame.load_pygame( f"res/maps/{name}.tmx")
        map_data = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())

        walls = []
        for obj in tmx_data.objects:
            if obj.type == "mur":
                walls.append(pg.Rect(obj.x , obj.y , obj.width , obj.height ))

        group = pyscroll.PyscrollGroup(map_layer = map_layer , default_layer = 1)
        group.add(self.player)

        # créer un obj map
        self.maps[name] = Map(name, walls, group)

    def get_map(self): return self.maps[self.current_map]

    def get_group(self): return self.get_map().group

    def get_walls(self): return self.get_map().walls

    def draw(self):
        self.get_group().draw(self.screen)
        self.get_group().center(self.player.rect.center)

    def update(self):
        self.get_group().update()

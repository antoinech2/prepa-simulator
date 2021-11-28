#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pygame as pg
import pytmx , pyscroll
from dataclasses import dataclass

"""
Aucune idee de comment fonctionne cette classe
J'ai juste recopie ce qu'il y avait dans game.py
Si quelqu'un veut commenter c'est pas de refus
"""
"""
 cc c'est djess je suis là pour le ménage

"""
@dataclass
class Map:  #Classe de données pour référencer les différentes cartes
    name : str
    walls : list[pg.Rect]
    group : pyscroll.PyscrollGroup
    tmx_data : pytmx.TiledMap

class MapManager :  # aka le Patron ou bien Le Contre-Maître

    def __init__ (self,screen,player):
        self.player = player
        self.screen = screen
        self.maps = dict()   #les dictionnaires c'est bien, surtout pour y ranger des cates
        self.current_map = "carte"  # La map à charger par défault ( mais sert aussi d'indicateur sur la map actuellement utilisée)

        self.register_map("niv_1")  # référencement des différentes cartes (voir fonction d'après)
        self.register_map("chambre")
        self.register_map("carte")

        self.teleport_player("spawn")

    def check_collision(self):
        'condition de colision'
        for sprite in self.get_group().sprites():
            if sprite.feet.collidelist(self.get_walls()) > -1:
                sprite.move_back()

    def teleport_player(self, name):
        'tp le joueur sur les coordonées de l objet name'
        point = self.get_object(name)
        self.player.position[0] = point.x
        self.player.position[1] = point.y
        self.player.save_location()

    def register_map (self, name):
        #chargement normal des elts d'une carte sur Tiled
        tmx_data = pytmx.util_pygame.load_pygame( f"res/maps/{name}.tmx")  # name doit bien entendu correspondre au nom du fichier
        map_data = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
        map_layer.zoom = 1.5
        #liste des murs
        walls = []
        for obj in tmx_data.objects:
            if obj.type == "mur":
                walls.append(pg.Rect(obj.x , obj.y , obj.width , obj.height ))
        #groupe de calques
        group = pyscroll.PyscrollGroup(map_layer = map_layer , default_layer = 1)
        group.add(self.player)

        # créer un obj map dans le dico maps
        self.maps[name] = Map(name, walls, group, tmx_data)

    def get_map(self):
        'renvoi la carte utilisée'
        return self.maps[self.current_map]

    def get_group(self):
        'renvoi le groupe de claque utilisé'
        return self.get_map().group

    def get_walls(self):
        'renvoi la liste des murs affichés'
        return self.get_map().walls

    def get_object(self, name):
        'renvoi la liste d objets par nom'
        return self.get_map().tmx_data.get_object_by_name(name)

    def draw(self):
        'affiche la carte et la centre sur le joueur'
        self.get_group().draw(self.screen)
        self.get_group().center(self.player.rect.center)

    def update(self):
        self.get_group().update()
        self.check_collision()
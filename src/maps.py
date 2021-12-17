#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame as pg
import pytmx, pyscroll
from dataclasses import dataclass

import npc
import save

"""
Gère les différentes cartes du jeu et ses accès respectifs
"""

class MapManager :  # aka le Patron ou bien Le Contre-Maître
    ZOOM = 1.5
    VOLUME = 0.1

    def __init__ (self,screen,game):
        self.game = game
        self.screen = screen

        config = save.load_config("player")
        self.load_map(config["map_id"])

    def load_map(self, map_id):
        self.map_id = map_id

        #On récupère le nom de fichier map et musique
        [map_file, self.music_file] = self.game.game_data_db.execute("SELECT file, music FROM maps WHERE id = ?", (self.map_id,)).fetchall()[0]

        #On charge la map de Tiled
        self.tmx_data = pytmx.util_pygame.load_pygame(f"res/maps/{map_file}.tmx")
        map_data = pyscroll.data.TiledMapData(self.tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
        map_layer.zoom = self.ZOOM

        # liste des murs
        self.walls = []
        for obj in self.tmx_data.objects:
            if obj.type == "mur":
                self.walls.append(pg.Rect(obj.x , obj.y , obj.width , obj.height ))

        # Liste des portails
        portals = self.game.game_data_db.execute("SELECT id, from_point FROM portals WHERE from_world = ?", (self.map_id,)).fetchall()
        self.portals = []
        self.portals_id = []

        for portal in portals :
            point = self.tmx_data.get_object_by_name(portal[1])
            self.portals.append(pg.Rect(point.x-2, point.y-2, point.width+4, point.height+4))
            self.portals_id.append(portal[0])

        # groupe de calques
        self.object_group = pyscroll.PyscrollGroup(map_layer = map_layer , default_layer = 1)
        self.object_group.add(self.game.player)

        # Gérant des NPC
        self.npc_manager = npc.NpcManager(self)
        self.music_manager() # le Dj fait son taf ( TODO : peut être metttre un décompte pour changer de musique moins brusquement)

    def check_collision(self):
        'condition de colision'
        index = self.game.player.feet.collidelist(self.portals)
        if index >= 0:   # le joueur entre dans un portal
            # On récupère l'endroit où téléporter le joueur
            [to_world, to_point] = self.game.game_data_db.execute("SELECT to_world, to_point FROM portals WHERE id = ?", (self.portals_id[index],)).fetchall()[0]
            self.load_map(to_world)
            self.teleport_player(to_point)  # on téléporte le j sur le spawn d'arriver

    def teleport_player(self, name):
        'tp le joueur sur les coordonées de l objet name'
        point = self.tmx_data.get_object_by_name(name)
        self.game.player.position[0] = point.x       # réaffectation des coordonées
        self.game.player.position[1] = point.y

    def music_manager(self):
        'Le DJ qui change de son quand on lui fait coucou'
        pg.mixer.music.load(f"res/sounds/music/{self.music_file}.mp3")
        pg.mixer.music.set_volume(self.VOLUME)
        pg.mixer.music.play(-1) # boucle musicale

    def draw(self):
        'affiche la carte et la centre sur le joueur'
        self.object_group.draw(self.screen)
        self.object_group.center(self.game.player.rect.center)

    def tick(self):
        'appelée, elle met à jour les elts suivants'
        self.object_group.update()
        self.check_collision()

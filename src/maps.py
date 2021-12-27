#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import externe
import pygame as pg
import pytmx, pyscroll
from dataclasses import dataclass

# Import interne
import npc
import objects
import save

"""
Gère les différentes cartes du jeu et ses accès respectifs
"""

class MapManager :
    ZOOM = 1.5
    VOLUME = 0.1 #Volume général du son

    def __init__ (self,screen,game):
        self.game = game
        self.screen = screen

        config = save.load_config("player")
        self.load_map(config["map_id"]) # Charge la carte où est le joueur

    def load_map(self, map_id):
        """Charge une carte"""
        self.map_id = map_id

        # Récupération du fichier de la carte et la musique associée
        [self.map_file, self.music_file] = self.game.game_data_db.execute("SELECT file, music FROM maps WHERE id = ?", (self.map_id,)).fetchall()[0]

        # Chargement de la map avec Tiled
        self.tmx_data = pytmx.util_pygame.load_pygame(f"res/maps/{self.map_file}.tmx")
        map_data = pyscroll.data.TiledMapData(self.tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
        map_layer.zoom = self.ZOOM

        # Création de la liste des murs
        self.walls = []
        for obj in self.tmx_data.objects:
            if obj.type == "mur":
                self.walls.append(pg.Rect(obj.x , obj.y , obj.width , obj.height ))

        # Création de la liste des portails
        portals = self.game.game_data_db.execute("SELECT id, from_point FROM portals WHERE from_world = ?", (self.map_id,)).fetchall()
        self.portals = []
        self.portals_id = []

        for portal in portals :
            point = self.tmx_data.get_object_by_name(portal[1])
            self.portals.append(pg.Rect(point.x, point.y, point.width, point.height))
            self.portals_id.append(portal[0])

        # Création des groupes calques
        self.object_group = pyscroll.PyscrollGroup(map_layer = map_layer , default_layer = 1)
        self.object_group.add(self.game.player)

        # Objets associés
        self.npc_manager = npc.NpcManager(self)
        # Gérant des objets
        self.object_manager = objects.ObjectManager(self)
        self.music_manager()
        # TODO : peut être metttre un décompte pour changer de musique moins brusquement

    def teleport_player(self, name):
        """Téléporte le joueur à un objet de Tiled"""
        point = self.tmx_data.get_object_by_name(name)
        self.game.player.position[0] = point.x
        self.game.player.position[1] = point.y

    def music_manager(self):
        """Joue la musique dans la carte"""
        pg.mixer.music.load(f"res/sounds/music/{self.music_file}.mp3")
        pg.mixer.music.set_volume(self.VOLUME)
        pg.mixer.music.play(-1) # Boucle la musique

    def draw(self):
        """Met à jour l'affichage de la carte"""
        self.object_group.draw(self.screen)
        self.object_group.center(self.game.player.rect.center)

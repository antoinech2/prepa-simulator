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
import sound as sd # Pour éviter la confusion avec le module Sound de pg
import scripts as sc

"""
Gère les différentes cartes du jeu et ses accès respectifs
"""

class MapManager:
    """Gestionnaire des maps et de leurs éléments"""
    ZOOM = 2.2

    def __init__ (self,screen,game):
        self.game = game
        self.screen = screen

        config = save.load_config("player")
        self.load_map(config["map_id"]) # Charge la carte où est le joueur

    def load_map(self, map_id, old_bgm = None):
        """Charge une carte"""
        self.map_id = map_id
        self.map_name = self.game.game_data_db.execute("select file from maps where id = ?;", (self.map_id,)).fetchall()[0][0]
        
        # Chargement du script de la map courante
        try:
            self.map_script = self.game.script_manager.find_script_from_name(f"{self.map_name}_mapscript")
        except:
            self.map_script = None
        self.script_is_rerunnable = self.game.game_data_db.execute("select script_is_rerunnable from maps where id = ?;", (self.map_id,)).fetchall()[0][0]

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

        for portal in portals:
            point = self.tmx_data.get_object_by_name(portal[1])
            self.portals.append(pg.Rect(point.x, point.y, point.width, point.height))
            self.portals_id.append(portal[0])

        # Création des groupes calques
        self.object_group = pyscroll.PyscrollGroup(map_layer = map_layer, default_layer = 1)
        self.object_group.add(self.game.player)

        # Objets associés
        self.npc_manager = npc.NpcManager(self)
        # Gérant des objets
        self.object_manager = objects.ObjectManager(self)
        self.sound_manager = sd.SoundManager(self, old_bgm)
        # TODO : peut être metttre un décompte pour changer de musique moins brusquement

        # Exécution du script en entrée de la map
        if self.map_script is not None:
            self.game.script_manager.execute_script(self.map_script)

    def teleport_player(self, tp_point):
        """Téléporte le joueur à un objet de Tiled ou à des coordonnées spécifiées"""
        if type(tp_point) != list:       # tp_point n'est pas un objet tiled
            point = self.tmx_data.get_object_by_name(tp_point)
            self.game.player.position[0] = point.x
            self.game.player.position[1] = point.y
        else:                           # tp_point est la liste des coordonnées d'un point
            self.game.player.position = tp_point

    def player_layer(self, layer):
        """Change le calque d'affichage du joueur.\n
        Arguments possibles : "bg" pour l'arrière-plan, "fg" pour le premier plan"""
        self.object_group.change_layer(self.game.player, layer)

    def draw(self):
        """Met à jour l'affichage de la carte"""
        self.object_group.draw(self.screen)
        self.object_group.center(self.game.player.rect.center)

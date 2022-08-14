#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import externe
import pygame as pg
import pytmx, pyscroll
import copy

# Import interne
import npc
import objects
import save
import sound as sd # Pour éviter la confusion avec le module Sound de pg

"""
Gère les différentes cartes du jeu et ses accès respectifs
"""

class MapManager:
    """Gestionnaire des maps et de leurs éléments"""
    ZOOM = 2.2

    def __init__ (self,screen,game):
        self.game = game
        self.screen = screen

        config = save.load_config("entities")["player"]
        self.load_map(config["map_id"]) # Charge la carte où est le joueur

    def load_map(self, map_id, old_bgm = None):
        """Charge une carte"""
        self.map_id = map_id
        self.map_name = self.game.game_data_db.execute("select file from maps where id = ?;", (self.map_id,)).fetchall()[0][0]
        
        # Réinitialisation de l'état du joueur
        self.game.player.is_sprinting = False

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
                self.walls.append(pg.Rect(obj.x, obj.y, obj.width, obj.height))

        # Création de la liste des portails
        portals = self.game.game_data_db.execute("SELECT id, from_point FROM portals WHERE from_world = ?", (self.map_id,)).fetchall()
        self.portals = []
        self.portals_id = []

        for portal in portals:
            point = self.tmx_data.get_object_by_name(portal[1])
            if point.type == "portal":
                self.portals.append(pg.Rect(point.x, point.y, point.width, point.height))
                self.portals_id.append(portal[0])
        print(self.portals_id)

        # Création de la liste des portes
        self.doors = []
        self.doors_id = []
        for obj in self.tmx_data.objects:
            if obj.type == "door":
                self.doors.append(pg.Rect(obj.x, obj.y, obj.width, obj.height))
                self.doors_id.append(self.game.game_data_db.execute("select id from portals where from_world = ? and from_point = ?;", (self.map_id, obj.name)).fetchall()[0][0])
        print(self.doors_id)

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
            acc = copy.deepcopy(self.game.script_tree)
            for sc in range(len(acc)):                     # Suppression des scripts permanents en cours d'exécution
                if "persistent" in acc[sc][0].name:
                    acc[sc] = None
            self.game.script_tree = []
            for script in acc:
                self.game.script_tree.append(script) if script is not None else ()
            self.game.script_manager.execute_script(self.map_script, "front")
    
    def get_warps(self):
        """Vérifie si le joueur touche un objet Tiled associé à une porte"""
        index = self.game.player.feet.collidelist(self.game.map_manager.doors)
        print(index)
        if index >= 0:   # Le joueur est dans un portail
            # On récupère l'endroit où téléporter le joueur
            [to_world, to_point] = self.game.game_data_db.execute("SELECT to_world, to_point FROM portals WHERE id = ?", (self.doors_id[index],)).fetchall()[0]
            direction = self.game.game_data_db.execute("select spawn_direction from Portals where id = ?", (self.doors_id[index],)).fetchall()[0][0]
            if direction is None:
                direction = "up"    # Valeur par défaut
            old_bgm = self.game.map_manager.sound_manager.music_file
            self.game.script_manager.sfx('door')        # Effet sonore
            self.game.player.warp(to_world, to_point, direction, old_bgm)
            self.game.player.is_warping = True

    def teleport_player(self, tp_point):
        """Téléporte le joueur à un objet de Tiled ou à des coordonnées spécifiées"""
        if len(tp_point) != 2:       # tp_point n'est pas une liste, un tuple, ou un array numpy
            point = self.tmx_data.get_object_by_name(tp_point)
            self.game.player.position = [point.x, point.y]
        else:                        # On repasse à la liste pour pouvoir changer les coordonnées du joueur
            self.game.player.position = list(tp_point)

    def player_layer(self, layer):
        """Change le calque d'affichage du joueur.\n
        Arguments possibles : "bg" pour l'arrière-plan, "fg" pour le premier plan"""
        self.object_group.change_layer(self.game.player, layer)

    def draw(self):
        """Met à jour l'affichage de la carte"""
        self.object_group.draw(self.screen)
        self.object_group.center(self.game.player.rect.center)

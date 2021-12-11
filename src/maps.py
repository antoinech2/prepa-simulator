#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pygame as pg
import pytmx, pyscroll
from dataclasses import dataclass

"""
Gère les différentes cartes du jeu et ses accès respectifs
"""

@dataclass  # classe de donées, pas besoin de faire d'__init__
class Portal:            # les poratilles entre les mondes
    from_world : str     # monde d'origine
    origin_point : str   # coordonées du portail du monde d'origine
    to_world : str       # monde d'arrivé
    next_point : str     # coordonées du spawn d'arrivé

@dataclass
class Map:  # Classe de données pour référencer les différentes cartes
    name : str                      # nom de la map
    walls : list[pg.Rect]           # murs de la map
    group : pyscroll.PyscrollGroup  # claques de la map
    tmx_data : pytmx.TiledMap       # carte Tiled de la map
    portals : list[Portal]          # portails de la map
    music : str                     # musique de la map

class MapManager :  # aka le Patron ou bien Le Contre-Maître

    def __init__ (self,screen,player):
        self.player = player
        self.screen = screen
        self.maps = dict()                  # les dictionnaires c'est bien, surtout pour y ranger des cates
        self.current_map = "carte"          # La map à charger par défault ( mais sert aussi d'indicateur sur la map actuellement utilisée)
        self.current_music = "titleVer2"    # resp musique
        self.music_manager()                # lancement de la musique
                                            # référencement des différentes cartes (voir fonction d'après)
        self.register_map("niv_1", "spring",
        portals =[
                Portal (from_world = "niv_1", origin_point = "to_main", to_world = "carte", next_point = "spawn_lycée"),
                Portal (from_world = "niv_1", origin_point = "to_l101", to_world = "l101", next_point = "spawn_l101_main"),
                Portal (from_world = "niv_1", origin_point = "to_i104", to_world = "i104", next_point = "spawn_i104"),
                Portal (from_world = "niv_1", origin_point = "to_i105", to_world = "i105", next_point = "spawn_i105"),
                Portal (from_world = "niv_1", origin_point = "to_i108", to_world = "i108", next_point = "spawn_i108"),
                Portal (from_world = "niv_1", origin_point = "to_i109", to_world = "i109", next_point = "spawn_i109")
        ])
        self.register_map("chambre", "la_kro",
        portals = [
                Portal (from_world = "chambre", origin_point = "to_dk3", to_world = "dk3", next_point = "spawn_chambre")
        ])
        self.register_map("carte", "titleVer2",
        portals = [
                Portal (from_world = "carte", origin_point = "to_lycée", to_world = "niv_1", next_point = "spawn_lycée") ,
                Portal (from_world = "carte", origin_point = "to_dk3", to_world = "dk3", next_point = "spawn_test")
        ])
        self.register_map("dk3", "proto_musique",
        portals = [
                Portal (from_world = "dk3", origin_point = "to_chambre", to_world = "chambre", next_point = "spawn_chambre"),
                Portal (from_world = "dk3", origin_point = "to_carte", to_world = "carte", next_point = "spawn_dk3")
        ])
        self.register_map("l101", "la_kro",
        portals = [
                Portal (from_world = "l101", origin_point = "to_niv1", to_world = "niv_1", next_point = "exit_l101" )
        ])
        self.register_map("i104", "la_kro",
        portals = [
                Portal (from_world = "i104", origin_point = "to_niv1", to_world = "niv_1", next_point = "exit_i104")
        ])
        self.register_map("i105", "la_kro",
        portals = [
                Portal (from_world = "i105", origin_point = "to_niv1", to_world = "niv_1", next_point = "exit_i105")
        ])
        self.register_map("i108", "trk8",
        portals = [
                Portal (from_world = "i108", origin_point = "to_niv1", to_world = "niv_1", next_point = "exit_i108")
        ])
        self.register_map("i109", "la_kro",
        portals = [
                Portal (from_world = "i109", origin_point = "to_niv1", to_world = "niv_1", next_point = "exit_i109")
        ])

        self.teleport_player("spawn_1")    # Tp le j au spawn de base ( soit ici celui de carte.tmx)

    def check_collision(self):
        'condition de colision'
        # aux portals
        for portal in self.get_map().portals :
            if portal.from_world == self.current_map :                           # enregistrement des coordonées des portal de la current_map
                point = self.get_object(portal.origin_point)
                rect = pg.Rect(point.x, point.y, point.width, point.height)

                if self.player.feet.colliderect(rect):                           # le joueur entre dans un portal
                    copy_portal = portal                                         # comme on va changer de portal, on garde les données en mémoire
                    self.current_map = portal.to_world                           # changement de monde
                    self.current_music = self.get_music_from(portal.to_world)    # changement de musique
                    self.teleport_player(copy_portal.next_point)                 # on téléporte le j sur le spawn d'arriver
                    self.music_manager()                                         # le Dj fait son taf ( TODO : peut être metttre un décompte pour changer de musique moins brusquement)
        # aux murs
        for sprite in self.get_group().sprites():
            if sprite.feet.collidelist(self.get_walls()) > -1:
                sprite.move_back()

    def teleport_player(self, name):
        'tp le joueur sur les coordonées de l objet name'
        point = self.get_object(name)
        self.player.position[0] = point.x       # réaffectation des coordonées
        self.player.position[1] = point.y
        self.player.save_location()             # pour éviter les bugs de loop de tp

    def register_map (self, name_map , name_music, portals = [] ):
        'enregistre une carte sur le ditionnaire self.maps de la classe MapManager'

        # chargement normal des elts d'une carte sur Tiled
        tmx_data = pytmx.util_pygame.load_pygame(f"res/maps/{name_map}.tmx")    # name_map doit bien entendu correspondre au nom du fichier tmx (resp pour name_music en mp3)
        map_data = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
        map_layer.zoom = 1.5

        # liste des murs
        walls = []
        for obj in tmx_data.objects:
            if obj.type == "mur":
                walls.append(pg.Rect(obj.x , obj.y , obj.width , obj.height ))

        # groupe de calques
        group = pyscroll.PyscrollGroup(map_layer = map_layer , default_layer = 1)
        group.add(self.player)

        # créer un obj map dans le dico maps
        self.maps[name_map] = Map(name_map, walls, group, tmx_data, portals, name_music)

    def music_manager(self):
        'Le DJ qui change de son quand on lui fait coucou'
        pg.mixer.music.load(f"res/sounds/music/{self.current_music}.mp3")
        pg.mixer.music.play(-1) # boucle musicale

    def get_map(self):
        'renvoie la carte utilisée'
        return self.maps[self.current_map]

    def get_group(self):
        'renvoie le groupe de calque utilisé'
        return self.get_map().group

    def get_walls(self):
        'renvoie la liste des murs affichés'
        return self.get_map().walls

    def get_music_from(self,name):
        'renvoie la musique d une carte'
        return self.maps[name].music

    def get_object(self, name):
        'renvoie la liste d objets par nom'
        return self.get_map().tmx_data.get_object_by_name(name)

    def draw(self):
        'affiche la carte et la centre sur le joueur'
        self.get_group().draw(self.screen)
        self.get_group().center(self.player.rect.center)

    def update(self):
        'appelée, elle met à jour les elts suivants'
        self.get_group().update()
        self.check_collision()

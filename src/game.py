#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Gère le jeu dans sa globalité, notemment la boucle principale"""

import pygame as pg
import pyscroll
import sqlite3 as sql
import yaml
import os

import player
import maps
import inputs

class Game:
    CONFIGURATION_FILE_LOCATION = "sav/window.yaml"
    DEFAULT_WINDOW_SIZE = (1000, 600) # FIXME: Passer en variable locale, trouver comment faire
    DATABASE_LOCATION = "res/game_data.db"
    GAME_NAME = "Prepa Simulator"

    def __init__(self):
        # Gestion de l'écran

        #Taille de l'écran
        #Création du dossier de sauvegarde s'il n'existe pas
        if not os.path.isdir("sav"):
            os.makedirs("sav")

        if os.path.isfile(self.CONFIGURATION_FILE_LOCATION):
            # On charge la configuration de l'écran
            window_config = yaml.safe_load(open(self.CONFIGURATION_FILE_LOCATION, 'r'))
            self.window_size = (window_config.get("size").get("width"), window_config.get("size").get("height"))
            self.is_fullscreen = window_config.get("fullscreen")
        else:
            # Creation d'une nouvelle configuration vierge
            self.window_size = self.DEFAULT_WINDOW_SIZE
            self.is_fullscreen = False
            open(self.CONFIGURATION_FILE_LOCATION, 'w').close()
            self.change_window_size(self.DEFAULT_WINDOW_SIZE[1], self.DEFAULT_WINDOW_SIZE[0])

        # Gestion de l'écran
        if self.is_fullscreen:
            #Mode plein écran
            self.screen = pg.display.set_mode((0,0), pg.RESIZABLE | pg.FULLSCREEN) # taille de la fenêtre
        else:
            #Mode normal
            self.screen = pg.display.set_mode((self.window_size), pg.RESIZABLE) # taille de la fenêtre
        pg.display.set_caption("jeu") # le petit nom du jeu

        #BDD
        self.db_connexion = sql.connect(self.DATABASE_LOCATION)
        self.game_data_db = self.db_connexion.cursor()

        self.tick_count = 0
        self.restart = True #Pour gérer la redimension
        self.resizable = False #La fenêtre peut être redimensionnée

        self.is_running = False #Statut général

    def change_window_size(self, height, width, fullscreen = False):
        if self.resizable:
            # On modifier la configuration
            new_window_config = {"size" : {"width" : width, "height" : height}, "fullscreen" : fullscreen}
            with open(self.CONFIGURATION_FILE_LOCATION, 'w') as file:
                yaml.dump(new_window_config, file) #Ecriture du fichier de config
            self.quit_game() #On redémarre le jeu
            self.restart = True
        else:
            self.resizable = True
    
        #Objets associés
        self.player = player.Player(0, 0, self)
        self.map_manager = maps.MapManager(self.screen, self)
        self.dialogue = None

    def tick(self):
        """Fonction principale de calcul du tick"""
        inputs.handle_pressed_key(self)
        self.map_manager.tick()
        self.map_manager.draw()
        if self.dialogue != None:
            self.dialogue.update()

    def run(self):
        """Boucle principale"""
        clock = pg.time.Clock()
        running = True

        while running:
            self.tick()
            pg.display.flip()  # update l'ecran

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.KEYDOWN:
                    inputs.handle_key_down_event(self, event)
                    if event.key == pg.K_F11: #Temporaire, à traiter ailleurs
                        size = pg.display.get_surface().get_size()
                        self.change_window_size(size[1], size[0], (not self.is_fullscreen))
                    elif event.key == pg.K_SPACE: #si Espace est pressée
                        self.player.space_pressed()
                elif event.type == pg.VIDEORESIZE:
                    self.change_window_size(event.h, event.w)
                elif event.type == pg.VIDEOEXPOSE:
                    size = pg.display.get_surface().get_size()
                    self.change_window_size(size[1], size[0])
            self.tick_count += 1
            clock.tick(60)  # 60 fps psk ça va trop vite
        pg.quit()
        self.game_data_db.close()
        self.db_connexion.close()

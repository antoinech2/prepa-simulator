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
import save

class Game:
    DATABASE_LOCATION = "res/game_data.db"
    GAME_NAME = "Prepa Simulator"

    def __init__(self):
        # Gestion de l'écran
        self.restart = False #Pour gérer la redimension

        self.is_running = False #Statut général

        #Taille de l'écran
        #Création du dossier de sauvegarde s'il n'existe pas
        if not os.path.isdir("sav"):
            os.makedirs("sav")

        config = save.load_config("window")
        self.window_size = config["size"]
        self.is_fullscreen = config["fullscreen"]

        # Gestion de l'écran
        if self.is_fullscreen:
            #Mode plein écran
            self.resizable = False #La fenêtre peut être redimensionnée
            self.screen = pg.display.set_mode((0,0), pg.RESIZABLE | pg.FULLSCREEN) # taille de la fenêtre
        else:
            #Mode normal
            self.resizable = True
            self.screen = pg.display.set_mode((self.window_size), pg.RESIZABLE) # taille de la fenêtre
        pg.display.set_caption("Prepa Simulator") # le petit nom du jeu

        #BDD
        self.db_connexion = sql.connect(self.DATABASE_LOCATION)
        self.game_data_db = self.db_connexion.cursor()

        self.tick_count = 0

        #Objets associés
        self.player = player.Player(self)
        self.map_manager = maps.MapManager(self.screen, self)
        self.dialogue = None


    def change_window_size(self, size = None, fullscreen = None):
        if self.resizable:
            save.save_window_config(size, fullscreen)
            self.is_running = False #On redémarre le jeu
            self.restart = True
        else:
            self.resizable = True

    def quit_game(self):
        pg.quit()
        self.game_data_db.close()
        self.db_connexion.close()
        self.player.close()

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
        self.is_running = True

        while self.is_running:
            self.tick()
            pg.display.flip()  # update l'ecran

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.restart = False
                    self.is_running = False
                elif event.type == pg.KEYDOWN:
                    inputs.handle_key_down_event(self, event)
                elif event.type == pg.VIDEORESIZE:
                    self.change_window_size(size = (event.w, event.h))
            self.tick_count += 1
            clock.tick(60)  # 60 fps psk ça va trop vite
        self.quit_game()

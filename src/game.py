#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Gère le jeu dans sa globalité, notemment la boucle principale"""

# Import externe
import pygame as pg
import pyscroll
import sqlite3 as sql
import yaml
import os

# Import interne
import player
import maps
import inputs
import save
import bag
import menu
import debug

class Game:
    DATABASE_LOCATION = "res/game_data.db"
    GAME_NAME = "Prepa Simulator"
    TICK_PER_SECOND = 60
    DEFAULT_FONT = menu.Font("consolas")

    def __init__(self):
        self.is_running = False #Statut général
        self.tick_count = 0 # Compteur général de tick
        self.debug = False

        self.restart = False #Si le jeu doit redémarrer suite à un redimensionnement de la fenêtre

        # Création du dossier de sauvegarde s'il n'existe pas
        if not os.path.isdir("sav"):
            os.makedirs("sav")
        # Dossier de paramètres
        if not os.path.isdir("stg"):
            os.makedirs("stg")

        # Chargement de la configuration de l'écran
        config = save.load_config("window")
        self.window_size = config["size"]
        self.is_fullscreen = config["fullscreen"]

        inputs.init()

        # Gestion de l'écran
        if self.is_fullscreen:
            # Mode plein écran
            self.resizable = False #La fenêtre peut être redimensionnée
            self.screen = pg.display.set_mode((0,0), pg.RESIZABLE | pg.FULLSCREEN) # taille de la fenêtre
        else:
            # Mode normal
            self.resizable = True
            self.screen = pg.display.set_mode((self.window_size), pg.RESIZABLE) # taille de la fenêtre

        # Définition du nom du jeu
        pg.display.set_caption(self.GAME_NAME)

        # Initialisation de la base de donnée
        self.db_connexion = sql.connect(self.DATABASE_LOCATION)
        self.game_data_db = self.db_connexion.cursor()

        self.tick_count = 0

        #Objets associés
        self.player = player.Player(self, bag.Bag())
        self.map_manager = maps.MapManager(self.screen, self)
        self.menu_manager = menu.MenuManager(self.screen, self)
        self.dialogue = None # Contient le dialogue s'il existe
        self.player.objects_state = save.load_config("objects")


    def change_window_size(self, **args):
        """Redimensionne la fenêtre"""
        if self.resizable:
            save.save_config("window", **args) #Sauvegarde de la nouvelle dimension
            # Redémarrage du jeu
            self.is_running = False
            self.restart = True
        else:
            self.resizable = True

    def quit_game(self):
        """Ferme le jeu"""
        pg.quit()
        self.player.save()
        # Fermeture de la base de donnée
        self.game_data_db.close()
        self.db_connexion.close()

    def tick(self):
        """Fonction principale de calcul du tick"""
        inputs.handle_pressed_key(self) # Gestion de toutes les touches préssées
        self.map_manager.draw()
        self.menu_manager.draw()
        self.player.update()
        if self.dialogue != None:
            self.dialogue.update() # Met à jour le dialogue
        if self.debug:
            debug.show_debug_menu(self)

    def run(self):
        """Boucle principale"""
        self.clock = pg.time.Clock()
        self.is_running = True

        while self.is_running:
            self.tick()
            pg.display.flip()  # Mise à jour de l'écran

            # Gestion des évènements
            for event in pg.event.get():
                if event.type == pg.QUIT: # Ferme le jeu
                    self.restart = False
                    self.is_running = False
                elif event.type == pg.KEYDOWN:
                    inputs.handle_key_down_event(self, event) # Gestion des touches préssées
                elif event.type == pg.VIDEORESIZE: # Gestion de la redimension de fenêtre
                    self.change_window_size(size = (event.w, event.h))

            self.tick_count += 1
            self.clock.tick(self.TICK_PER_SECOND)  # Attente jusqu'à la prochaine image

        self.quit_game() # Fermeture du jeu

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Gère le jeu dans sa globalité, notemment la boucle principale"""

# Import externe
import pygame as pg
import sqlite3 as sql
import os

# Import interne
import internalclock as ic
import entities
import maps
import inputs
import save
import bag
import menu
import debug
import scriptmanager as sm
import minigame as mgm
import mission as mi

class Game:
    DATABASE_LOCATION = "res/game_data.db"
    GAME_NAME = "Prepa Simulator"
    TICK_PER_SECOND = 60

    def __init__(self):
        self.is_running = False # Statut général
        self.debug = False  # Etat du menu de debug
        self.menu_is_open = False   # Etat du menu latéral
        self.input_lock = False # Blocage du clavier

        # Variables de scripting
        self.script_tree = []   # Arbre d'appel des scripts composé des listes [script_courant, commande_en_cours_d_exécution]
                                # le dernier élément est celui en cours de traitement
        self.running_script = None  # Script courant
        self.executing_moving_script = False    # Le joueur est en train de bouger suite à un script
        self.moving_people = {}                 # ID des entités et paramètres des mouvements en cours
        self.movement_mem = []                  # Prochains mouvements
        self.persistent_move = {}               # Mouvements permanents des PNJ
        self.persistent_move_index = {}         # Index du mouvement permanent en cours d'exécution

        self.default_font = menu.Font("consolas")

        self.restart = False                    # Si le jeu doit redémarrer suite à un redimensionnement de la fenêtre

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
        save.load_config("entities")        # Création des données du joueur
        self.save = save.init_save_database()

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

        # Objets associés
        self.player = entities.Player(self, 'player', 'm2')
        self.bag = bag.Bag(self.save)
        self.mission_manager = mi.MissionManager(self)
        self.script_manager = sm.ScriptManager(self)
        self.internal_clock = ic.InternalClock(self)
        self.map_manager = maps.MapManager(self.screen, self)
        self.menu_manager = menu.MenuManager(self.screen, self)
        self.mgm_manager = mgm.MGManager(self)

        self.dialogue = None # Contient le dialogue s'il existe
        self.map_manager.npc_manager.flip()


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
        try:
            # Fermeture de la base de donnée
            self.save.close()
            self.game_data_db.close()
            self.db_connexion.close()
        except sql.ProgrammingError:
            print("Impossible d'accéder à la base de donnée lors de la sauvegarde. Cela peut être dû à une réinitialisation des données...")
        pg.display.quit()
        pg.quit()

    def tick(self):
        """Fonction principale de calcul du tick"""
        inputs.handle_pressed_key(self) # Gestion de toutes les touches préssées
        self.internal_clock.update()
        self.map_manager.draw()
        self.menu_manager.draw()
        self.player.update()
        for npc in self.map_manager.npc_manager.npc_group:
            npc.update()
        self.script_manager.update() # Actualisation du mouvement d'un script : toutes commandes bloquées
        self.mgm_manager.update()
        if self.dialogue != None:
            self.dialogue.update() # Met à jour le dialogue
        if self.debug:
            debug.show_debug_menu(self)

    def run(self):
        """Boucle principale"""
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

            self.internal_clock.pgclock.tick(self.TICK_PER_SECOND)  # Attente jusqu'à la prochaine image

        self.quit_game() # Fermeture du jeu

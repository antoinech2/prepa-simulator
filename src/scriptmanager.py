#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Gestion des scripts"""

import pygame as pg

import scripts
from copy import copy

class ScriptManager():
    """Classe de gestion des scripts du jeu"""
    def __init__(self, game):
        self.game = game
        self.list_of_scripts = []
        self.current_command = 0

        # Caractéristiques du script de mouvement
        self.movement_boundary = None # Longueur du déplacement
        self.moving_direction = None

        # Chargement de la liste des scripts
        raw_scripts = self.game.game_data_db.execute("select id, name, is_rerunnable from scripts;").fetchall()
        for scr in raw_scripts:
            # Obtention du contenu du script lié
            name = scr[1]
            contents = scripts.get_script_contents(name)
            self.list_of_scripts.append(scripts.Script(scr[0], scr[1], scr[2], contents))

    def get_script_from_id(self, ident):
        """Retourne un script étant donné un identifiant"""
        pos = [script.id for script in self.list_of_scripts].index(ident)
        return(self.list_of_scripts[pos])
    
    def find_script_from_name(self, name):
        """Retourne l'ID d'un script étant donné son nom"""
        pos = [script.name for script in self.list_of_scripts].index(name)
        return(self.list_of_scripts[pos])

    def execute_script(self, script):
        """Exécution d'un script"""
        assert type(script) is scripts.Script, "Erreur : l'objet source n'est pas un script"
        self.game.running_script = script
    
    # Définition des fonctions utilisées dans les scripts
    def movingscript(self, direction, pix, sprint = False):
        """Exécution d'un script de déplacement"""
        self.game.executing_moving_script = True
        self.initial_coords = copy(self.game.player.position)
        self.moving_direction = direction
        self.movement_boundary = pix
        self.sprint_during_script = sprint
    
    def exit_movingscript(self):
        """Terminaison d'un script de déplacement"""
        self.game.executing_moving_script = False

    def update(self):
        if self.game.running_script is not None:
            if self.game.executing_moving_script:
                if self.moving_direction == "right":
                    self.game.player.move([False, True, False, False], self.sprint_during_script)
                if self.moving_direction == "down":
                    self.game.player.move([False, False, True, False], self.sprint_during_script)
                dist = ((self.initial_coords[0] - self.game.player.position[0])**2 + (self.initial_coords[1] - self.game.player.position[1])**2) ** 0.5 # Distance totale parcourue pendant le script
                if dist > self.movement_boundary:
                    self.exit_movingscript()
            elif self.current_command >= len(self.game.running_script.contents):
                self.game.running_script = None # Fin du script atteinte
            else: # Le jeu est disponible pour passer à l'étape suivante
                eval(self.game.running_script.contents[self.current_command])
                self.current_command += 1

    def infobox(self, text):
        """Ouverture d'une infobulle"""
        pass

    def get_object(self, object_id, qty):
        """Obtention d'un objet en une quantité donnée"""
        self.game.bag.increment_item(object_id, qty)

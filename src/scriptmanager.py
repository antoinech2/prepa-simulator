#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Gestion des scripts"""

import pygame as pg
from copy import copy
from random import randint

import scripts
import dialogue as dia

class ScriptManager():
    """Classe de gestion des scripts du jeu"""
    def __init__(self, game):
        self.game = game
        self.list_of_scripts = []
        self.current_command = 0
        self.current_npc = None

        # Mémoire interne du gestionnaire de scripts
        self.boolacc = False # Accumulateur booléen utilisé lors des comparaisons
        self.acc = 0 # Accumulateur entier
        self.infobox_contents = [] # Accumulateur de l'infobox, pourra être modifié si un script nécessite une accumulation d'éléments

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

    def execute_script(self, script, npc = None):
        """Exécution d'un script"""
        if type(script) is not scripts.Script:
            raise TypeError("Erreur : l'objet source n'est pas un script")
        self.current_npc = npc
        self.game.running_script = script
    
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
                if self.moving_direction == "up":
                    self.game.player.move([True, False, False, False], self.sprint_during_script)
                if self.moving_direction == "right":
                    self.game.player.move([False, True, False, False], self.sprint_during_script)
                if self.moving_direction == "down":
                    self.game.player.move([False, False, True, False], self.sprint_during_script)
                if self.moving_direction == "left":
                    self.game.player.move([False, False, False, True], self.sprint_during_script)
                dist = ((self.initial_coords[0] - self.game.player.position[0])**2 + (self.initial_coords[1] - self.game.player.position[1])**2) ** 0.5 # Distance totale parcourue pendant le script
                if dist > self.movement_boundary or self.game.player.boop: # Le mouvement s'est déroulé normalement ou le joueur s'est pris un mur
                    self.exit_movingscript()
            elif self.current_command >= len(self.game.running_script.contents):
                self.game.running_script = None # Fin du script atteinte
                self.current_command = 0
            else: # Le jeu est disponible pour passer à l'étape suivante
                command = "self." + self.game.running_script.contents[self.current_command] # Correction syntaxique
                eval(command)
                self.current_command += 1


    ###################################
    # Définition du langage des scripts

    def loadtext(self, text):
        """Chargement du texte d'une infobox dans la mémoire"""
        self.infobox_contents.append(text)

    def infobox(self):
        """Ouverture d'une infobulle"""
        self.game.dialogue = dia.Dialogue(self.game, None, True, -1, self.infobox_contents)
        self.infobox_contents = []

    def dialogue(self, talking, dialogue_id):
        """Ouverture d'une boîte de dialogue"""
        self.game.dialogue = dia.Dialogue(self.game, talking, False, dialogue_id)

    # Fonctions avec l'accumulateur booléen

    def compare_obj_qty(self, obj_id, operator, qty):
        """Opération logique sur la quantité d'un objet. Le résultat est stocké dans l'accumulateur sous forme de booléen"""
        if obj_id not in self.game.bag.contents:
            self.boolacc = False
        else:
            comp = self.game.bag.contents[obj_id]
            if operator == "sup":
                self.boolacc = True if comp >= qty else False
            elif operator == "inf":
                self.boolacc = True if comp <= qty else False
            elif operator == "eq":
                self.boolacc = True if comp == qty else False
    
    def iftrue(self, command):
        """Exécution d'une commande si l'accumulateur booléen est True"""
        if self.boolacc:
            corrected_comm = "self." + command
            eval(corrected_comm)
    
    def iffalse(self, command):
        """Exécution d'une commande si l'accumulateur booléen est False"""
        if not self.boolacc:
            corrected_comm = "self." + command
            eval(corrected_comm)
    
    # Fonctions avec l'accumulateur numérique
    def ran(self, inf, sup):
        """Place un entier aléatoire dans l'accumulateur"""
        self.acc = randint(inf, sup)
    
    def compare(self, operator, qty):
        """Opération logique sur la valeur de acc. Le résultat est stocké dans l'accumulateur booléen"""
        if operator == "sup":
            self.boolacc = (self.acc >= qty)
        elif operator == "inf":
            self.boolacc = (self.acc <= qty)
        elif operator == "eq":
            self.boolacc = (self.acc == qty)
    
    # Fonctions sonores
    def chg_music(self, track):
        """Changement de la musique courante"""
        self.game.map_manager.sound_manager.play_music(track)
    
    def sfx(self, fx):
        """Joue un effet sonore"""
        self.game.map_manager.sound_manager.play_sfx(fx)
    

    # Fonctions des NPC
    def checkflag(self, npc, flag_id):
        """Vérification d'un flag d'un NPC"""
        self.boolacc = npc.flags[flag_id]
    
    def setflag(self, npc, flag_id, state):
        """Mise à jour du flag d'un NPC"""
        npc.flags[flag_id] = state
    
    # Fonctions des objets
    def get_object(self, object_id, qty):
        """Obtention d'un objet en une quantité donnée"""
        self.game.bag.increment_item(object_id, qty)
    
    def toss_object(self, object_id, qty):
        """Destruction d'un objet en une quantité donnée, ne fait rien s'il n'y en a pas assez"""
        if self.game.bag.contents[object_id] >= qty:
            self.game.bag.increment_item(object_id, -qty)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Gestion des scripts"""

import pygame as pg

import scripts

class ScriptManager():
    """Classe de gestion des scripts du jeu"""
    def __init__(self, game):
        self.game = game
        self.list_of_scripts = []

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
        for function_str in script.contents:
            eval(function_str)
    
    # Définition des fonctions utilisées dans les scripts
    def displacement(self, direction, pix, sprint = False):
        """Déplacement du joueur dans la direction voulue en degrés, sur une distance donnée"""
        initial_x = self.game.player.position[0]
        initial_y = self.game.player.position[1]
        if direction == "up":
            pass
        if direction == "upright":
            pass
        if direction == "right":
            pass
        if direction == "downright":
            pass
        if direction == "down":
            while self.game.player.position[0] - initial_x < pix:
                self.game.player.move([False, False, True, False], sprint)
                # TODO Trouver un moyen d'animer le mouvement du joueur
        if direction == "downleft":
            pass
        if direction == "left":
            pass
        if direction == "upleft":
            pass
        
    
    def infobox(self,text):
        """Ouverture d'une infobulle"""
        pass

    def get_object(self,object_id, qty):
        """Obtention d'un objet en une quantité donnée"""
        self.game.bag.increment_item(object_id, qty)

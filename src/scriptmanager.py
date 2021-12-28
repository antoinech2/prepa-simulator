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
            self.list_of_scripts.append(scripts.Script(scr[0], scr[1], scr[2]))

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
        for function in script.contents:
            function
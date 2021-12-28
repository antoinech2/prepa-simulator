#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Gestion des fonctions associées aux scripts"""

import pygame as pg

class Script():
    """Classe des scripts"""
    # Classe où l'on met toutes les fonctions appelables dans un script.
    # Un script comporte obligatoirement des fonctions de sa classe ou certains de ses attributs.
    def __init__(self, id, name, is_rerunnable, contents):
        self.id = id
        self.is_running = False
        self.name = name
        self.contents = contents
        try:
            self.function = eval(name)
        except:
            print(f"Erreur : la fonction demandée, {name}, n'existe pas.")
            print("Utilisation du script dummyScript à la place...")
            self.function = dummyScript
        self.is_rerunnable = bool(is_rerunnable)


def get_script_contents(name):
    """Obtention du contenu d'un script étant donné son nom"""
    return(eval(name)())

# Définition des différents scripts
def dummyScript():
    return(["self.get_object(1, 500)"])
    #return(["""self.displacement("down", 100)"""])
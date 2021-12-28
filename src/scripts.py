#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Gestion des fonctions associées aux scripts"""

import pygame as pg

class Script():
    """Classe des scripts"""
    # Classe où l'on met toutes les fonctions appelables dans un script.
    # Un script comporte obligatoirement des fonctions de sa classe ou certains de ses attributs.
    def __init__(self, id, name, is_rerunnable):
        self.id = id
        self.is_running = False
        self.name = name
        try:
            self.function = eval(name)
        except:
            print(f"Erreur : la fonction demandée, {name}, n'existe pas.")
            print("Utilisation du script dummyScript à la place...")
            self.function = dummyScript
        self.is_rerunnable = bool(is_rerunnable)

    
    # Définition des fonctions
    # Les fonctions sont appelées par le Script Manager. Les variables sont donc relatives à celui-ci
    def move(self,direction, pix):
        """Déplacement du joueur dans la direction voulue en degrés, sur une distance donnée"""
        pass
    
    def infobox(self,text):
        """Ouverture d'une infobulle"""
        pass

    def get_object(self,object_id, qty):
        """Obtention d'un objet en une quantité donnée"""
        self.game.bag.increment_item(object_id, qty)

# Définition des différents scripts
def dummyScript():
    return(["get_object(1, 500)"])
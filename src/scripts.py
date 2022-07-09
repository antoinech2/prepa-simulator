#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Gestion des fonctions associées aux scripts"""

class Script():
    """Classe des scripts"""
    # Classe où l'on met toutes les fonctions appelables dans un script.
    # Un script comporte obligatoirement des fonctions de sa classe ou certains de ses attributs.
    def __init__(self, id, name, contents):
        self.id = id
        self.is_running = False
        self.name = name
        self.contents = contents
        self.labels = self.search_labels()      # Dictionnaire dont les clés sont les noms des labels et les valeurs sont leurs lignes d'apparition
    
    def search_labels(self):
        """Construction du dictionnaire des labels"""
        res = {}
        for command in range(len(self.contents)):
            if self.contents[command][0:5] == "label":
                label_tag = self.contents[command][7:-2]    # Extraction du nom du label
                res[label_tag] = command
        return(res)

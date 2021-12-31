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
            print("Utilisation du script ordinaryNpc à la place...")
            self.function = ordinaryNpc
        self.is_rerunnable = bool(is_rerunnable)


def get_script_contents(name):
    """Obtention du contenu d'un script étant donné son nom"""
    return(eval(name)())

# Définition des différents scripts
def dummyScript():
    #return(["self.get_object(1, 500)"])
    #return(["""self.movingscript("down", 40)""",
    #        """self.movingscript("right", 20)""",
    #        """self.movingscript("down", 10)"""])
    return(["""self.compare_obj_qty(1, "sup", 1)""",
            """self.iffalse(\"\"\"self.dialogue(self.current_npc, 1)\"\"\")""",
            """self.iftrue(\"\"\"self.dialogue(self.current_npc, 2)\"\"\")"""
            ])

# TODO : Enlever le self à chaque instruction pour le rajouter lors du traitement, pour un script plus lisible

def randomdummy():
    return(["""self.ran(1, 4)""",
            """self.compare("eq", 1)""",
            """self.iftrue(\"\"\"self.dialogue(self.current_npc, 1)\"\"\")""",
            """self.compare("eq", 2)""",
            """self.iftrue(\"\"\"self.dialogue(self.current_npc, 2)\"\"\")""",
            """self.compare("eq", 3)""",
            """self.iftrue(\"\"\"self.dialogue(self.current_npc, 3)\"\"\")""",
            """self.compare("eq", 4)""",
            """self.iftrue(\"\"\"self.dialogue(self.current_npc, 4)\"\"\")"""])

def ordinaryNpc():
    """Script des NPC banals"""
    return(["""self.dialogue(self.game, self.current_npc)"""])
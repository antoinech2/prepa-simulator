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

# Définition des scripts ponctuels
def ordinaryNpc():
    """Script des NPC banals"""
    return(["""dialogue(self.current_npc, 1)"""])

def debug():
    return(["""loadtext('→')""",
            """infobox()"""])

def dummyScript():
    #return(["self.get_object(1, 500)"])
    #return(["""self.movingscript("down", 40)""",
    #        """self.movingscript("right", 20)""",
    #        """self.movingscript("down", 10)"""])
    return(["""compare_obj_qty(1, "sup", 1)""",
                """iffalse('dialogue(self.current_npc, 1)')""",
                """iftrue('dialogue(self.current_npc, 2)')""",
            """movingscript("up", 60)""",
            """movingscript("right", 800)"""
            ])

def randomdummy():
    return(["""ran(1, 4)""",
            """get_object(0, 1)""",
            """compare("eq", 1)""",
                """iftrue('dialogue(self.current_npc, 1)')""",
            """compare("eq", 2)""",
                """iftrue('dialogue(self.current_npc, 2)')""",
            """compare("eq", 3)""",
                """iftrue('dialogue(self.current_npc, 3)')""",
            """compare("eq", 4)""",
                """iftrue('dialogue(self.current_npc, 4)')"""
            ])

def getitemtest():
    return(["""compare_obj_qty(0, "sup", 1)""",
                """iftrue('dialogue(self.current_npc, 1)')""",
                """iftrue('toss_object(0, 1)')""",
                """iffalse('dialogue(self.current_npc, 2)')"""
            ])

def mightybutton():
    return(["""loadtext("Je suis le Père Noël ! lentsch lentsch lentsch lentsch lentsch lentsch lentsch lentsch lentsch lentsch lentsch lentsch lentsch lentsch lentsch lentsch lentsch lentsch lentsch lentsch lentsch lentsch lentsch ")""",
            """loadtext("lentsch lentsch")""",
            """infobox()""",
            """sfx("mighty_button")"""])

def brrr():
    """Script exemple pour Skler"""
    return(["""dialogue(self.current_npc, 2)""",
            """loadtext("ln(1-1/n) est équivalent à 1-1/n.")""",
            """loadtext("Oh non !")""",
            """infobox()""",
            """dialogue(self.current_npc, 3)""",
            """runscript('denis_brogniart')""",
            """movingscript('right', 8000, True)"""])

def denis_brogniart():
    return(["""loadtext("AH !")""",
            """infobox()""",
            """sfx("mighty_button")"""])

def infinitepower():
    return(["""put(2)""",
            """math("/", 0)"""])

def accprint():
    return(["""loadtext(f'{self.acc}')""",
            """infobox()"""])

def lionelisation():
    return(["""runscript('accprint')""",
            """runscript('infinitepower')""",
            """runscript('accprint')"""])


def sign1():
    """Panneau en sortie de l'escalier de la I, niveau 1"""
    return(["""loadtext("↑ COUR D'HONNEUR")""",
            """loadtext("← SALLES I104 À I110")""",
            """loadtext("→ SALLES H009 À H010 - T001 À T003")""",
            """loadtext("↓ SALLE L101 - VIE SCOLAIRE")""",
            """infobox()"""])

# Définition des scripts de surface (pouvant se déclencher lorsque le joueur marche desus)
def i104_mapscript():
    return(["""loadtext("aaaaaaaaaa")""",
            """infobox()"""])
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
        self.labels = self.search_labels()      # Dictionnaire dont les clés sont les noms des labels et les valeurs sont leurs lignes d'apparition
        
        try:
            self.function = eval(name)
        except:
            print(f"Erreur : la fonction demandée, {name}, n'existe pas.")
            print("Utilisation du script ordinaryNpc à la place...")
            self.function = ordinaryNpc
        self.is_rerunnable = bool(is_rerunnable)
    
    def search_labels(self):
        """Construction du dictionnaire des labels"""
        res = {}
        for command in range(len(self.contents)):
            if self.contents[command][0:5] == "label":
                label_tag = self.contents[command][7:-2]    # Extraction du nom du label
                res[label_tag] = command
        return(res)


def get_script_contents(name):
    """Obtention du contenu d'un script étant donné son nom"""
    return(eval(name)())

# Définition des scripts majeurs (sauvegarde, etc.)
def explode():
    """Script fermant de force le jeu sans sauvegarde"""
    return(["""game.quit_game()"""])

def save():
    """Script effectuant une sauvegarde de la partie"""
    return(["""loadtext('Voulez-vous sauvegarder la partie ?')""",
            """infobox()""",
            """opencb()""",
            """cb_result()""",
            """compare('eq', 0)""",
                """iffalse('false()')""",       # La sauvegarde a été annulée
                """iffalse('goto("end")')""",   # On passe l'étape de sauvegarde
            """true()""",       # La sauvegarde a réussi
            """save()""",
            """loadtext('Partie sauvegardée.')""",
            """infobox()""",
            
            """label("end")"""])

def object():
    """Script d'obtention d'un objet unique selon son identifiant stocké dans l'acc"""
    return(["""sfx('jingleV2')""",
            """loadtext(f'Obtenu : {self.game.map_manager.object_manager.list_of_objects[self.acc].name} !')""",
            """infobox()""",
            """get_object(self.acc, 1)"""])

def quiz():
    """Script qui lance le mini-jeu quiz"""
    return(["""ran(60, 68)""",
            """launchmgm("select", self.acc)"""])


# Définition des scripts ponctuels
def void():
    """Script vide"""
    return([])

def ordinaryNpc():
    """Script des NPC banals"""
    return(["""dialogue(self.current_npc, 1)"""])

def debug():
    return(["""chg_music("it's concours time")""",

            """label('main')""",
            """ran(1, 23)""",    # TODO Longueur du fichier yaml associé au mini-jeu
            """launchmgm("select", self.acc)""",
            """checkevent('passedSelectMG')""",
                """iftrue("loadtext('''bravo''')")""",
                """iffalse("sfx('mighty_button')")""",
                """iffalse("loadtext('''t'es nul''')")""",
            """infobox()""",
                """iftrue("goto('main')")""",
            """chg_music(-1)"""])

def debug():
    return(["""loadtext('''coucou''')""",
            """infobox()""",
            """chg_music("it's concours time")""",
            """goto('main')""",

            """label('fail')""",
            """ran(1, 2)""",
            """compare('eq', 1)""",
                """iftrue("loadtext('''tg recommence''')")""",
                """iftrue("goto('next')")""",
            """compare('eq', 2)""",
                """iftrue("loadtext('''tg t'es nul''')")""",
            
            """label('next')""",
            """infobox()""",
            """goto('main')""",
            
            """label('main')""",
            """runscript('quiz')""",
            """checkevent('passedSelectMG')""",
                """iffalse("goto('fail')")""",
            """runscript('quiz')""",
            """checkevent('passedSelectMG')""",
                """iffalse("goto('fail')")""",
            """runscript('quiz')""",
            """checkevent('passedSelectMG')""",
                """iffalse("goto('fail')")""",
            
            """loadtext('''c'est bien tu connais ton cours''')""",
            """infobox()""",
            """chg_music(-1)"""
            ])

def dummyScript():
    return(["""testflag(12101, 0)""",
                """iftrue("loadtext('''Le flag 0 de la L101 a été levé''')")""",
                """iffalse("loadtext('''Le flag 0 de la L101 est encore baissé''')")""",
            """infobox()""",
            """checknpcflag(self.current_npc, 0)""",
                """iftrue("loadtext('''Mon flag 0 a été levé''')")""",
                """iftrue("setnpcflag(self.current_npc, 0, 0)")""",
                """iffalse("loadtext('''Mon flag 0 est encore baissé''')")""",
                """iffalse("setnpcflag(self.current_npc, 0, 1)")""",
            """infobox()""",
            """checknpcflag(self.current_npc, 0)""",
                """iftrue("loadtext('''Mon flag 0 est maintenant levé''')")""",
                """iffalse("loadtext('''Mon flag 0 est maintenant baissé''')")""",
            """infobox()"""
            ])

def randomdummy():
    return(["""label('stuck')""",
            """loadtext("Tu es coincé")""",
            """infobox()""",
            """goto('stuck')"""
            ])

def getitemtest():
    return(["""compare_obj_qty(0, "sup", 1)""",
                """iftrue('dialogue(self.current_npc, 1)')""",
                """iftrue('toss_object(0, 1)')""",
                """iffalse('dialogue(self.current_npc, 2)')"""
            ])

def mightybutton():
    return(["""loadtext(2)""",
            """loadtext(3)""",
            """infobox()""",
            """sfx("mighty_button")"""])

def brrr():
    """Script exemple pour Skler"""
    return(["""move('right', 50)""",
            """move('up', 200)""",
            """dialogue(self.current_npc, 2)""",
            """loadtext(4)""",
            """loadtext(5)""",
            """infobox()""",
            """dialogue(self.current_npc, 3)""",
            """runscript('denis_brogniart')""",
            """move('right', 8000, True)"""])

def denis_brogniart():
    return(["""loadtext(6)""",
            """infobox()""",
            """sfx("mighty_button")"""])

def infinitepower():
    return(["""put(2)""",
            """math("/", 0)"""])

def accprint():
    return([])

def lionelisation():
    return(["""checknpcflag(self.current_npc, 0)""",
                """iftrue("goto('end')")""",
            """loadtext("Tu es en quelle classe ?")""",
            """infobox()""",
            """opencb(['MP', 'MP*'])""",
            """cb_result()""",
            """compare('eq', 0)""",
                """iftrue("raiseevent('isMP')")""",
                """iftrue("lowerevent('isMPStar')")""",
                """iffalse("lowerevent('isMP')")""",
                """iffalse("raiseevent('isMPStar')")""",
            """setnpcflag(self.current_npc, 0, 1)""",
            
            """label('end')""",
            """checkevent('isMP')""",
                """iftrue("loadtext('''Tu es en MP !''')")""",
            """checkevent('isMPStar')""",
                """iftrue("loadtext('''Tu es en MP* !''')")""",
            """infobox()"""])

def licite():
    return(["""checkevent('isMP')""",
                """iffalse("loadtext('tg')")""",
                """iffalse("infobox()")""",
                """iffalse("interrupt()")""",
            """loadtext('coucou')""",
            """infobox()""",
            """put(21)""",
            """runscript('object')"""])

def horodat():
    return(["""getday()""",
            """compare('eq', 0)""",
                """iftrue("loadtext('''Nous sommes lundi''')")""",
                """iffalse("loadtext('''Nous ne sommes pas lundi''')")""",
            """infobox()"""])

def testporte():
    return(["""loadtext("background")""",
            """infobox()""",
            """changelayer("bg")""",
            """loadtext("foreground")""",
            """infobox()""",
            """changelayer("fg")"""])

def flaginator():
    return(["""testflag(-1,0)""",
                """iftrue("lowerflag(-1,0)")""",
                """iftrue("loadtext('''Le flag 0 de la L101 va être baissé''')")""",
                """iffalse("raiseflag(-1,0)")""",
                """iffalse("loadtext('''Le flag 0 de la L101 va être levé''')")""",
            """infobox()"""])

def testsave():
    return(["""dialogue(self.current_npc, 1)""",
            """runscript('save')""",
                """iftrue('dialogue(self.current_npc, 2)')""",
                """iffalse('dialogue(self.current_npc, 3)')"""
            ])

def hdmi():
    """Petite mission pour le PC de la H009"""
    return(["""testflag(-1, 0)""",
                """iftrue("loadtext('''Le câble HDMI est branché à l'ordinateur.''')")""",
                """iftrue("infobox()")""",
                """iftrue("interrupt()")""",
            """loadtext('''Il y a de la place pour un câble HDMI derrière la tour.''')""",
            """infobox()""",
            """compare_obj_qty(10, 'sup', 1)""",    # Est-ce que le joueur a un câble HDMI ?
                """iffalse("interrupt()")""",
            """loadtext('''Voulez-vous brancher le câble HDMI ?''')""",
            """infobox()""",
            """opencb()""",
            """cb_result()""",
            """compare('eq', 0)""" ,     # Est-ce que le joueur a répondu oui ?
                """iffalse("loadtext('''Le port HDMI prend la poussière.''')")""",
                """iffalse("infobox()")""",
                """iffalse("interrupt()")""",
            """loadtext('''Vous branchez le câble HDMI à l'ordinateur.''')""",
            """loadtext('''La souris marche maintenant depuis l'autre côté de la salle !''')""",
            """infobox()""",
            """toss_object(10, 'all')""",
            """raiseflag(-1, 0)"""])

def jecompte():
    """Démonstration d'une boucle for en script"""
    return(["""loadtext('''Regarde je sais compter jusqu'à 10 !''')""",
            """infobox()""",
            """put(0)""",
            
            """label('incr')""",
            """math('+', 1)""",
            """loadtext(str(self.acc))""",
            """infobox()""",
            """compare('sup', 10)""",
                """iffalse("goto('incr')")""",
            
            """loadtext('''Voilà''')""",
            """infobox()"""])

def testcolle():
    """Petites questions fermées qui font planter le jeu en cas de réponse fausse"""
    return(["""loadtext('''Question !''')""",
            """infobox()""",
            """loadtext('''Il existe une L003 au lycée ?''')""",
            """infobox()""",
            """opencb()""",
            """cb_result()""",
            """compare('eq', 1)""",
                """iftrue("loadtext('''faux''')")""",
                """iftrue("infobox()")""",
                """iftrue("runscript('explode')")""",
            """loadtext('''Correct !''')""",
            """loadtext('''Une matrice symétrique est forcément diagonalisable ?''')""",
            """infobox()""",
            """opencb()""",
            """cb_result()""",
            """compare('eq', 0)""",
                """iftrue("loadtext('''faux''')")""",
                """iftrue("infobox()")""",
                """iftrue("runscript('explode')")""",
            """loadtext('''Correct !''')""",
            """infobox()"""])

def missingno():
    return(["""loadtext('''tg''')""",
            """infobox()""",
            """runscript('explode')"""])

# Scripts des panneaux
def sign1():
    """Panneau en sortie de l'escalier de la I, niveau 1"""
    return(["""loadtext(7)""",
            """loadtext(8)""",
            """loadtext(9)""",
            """loadtext(10)""",
            """infobox()"""])

# Définition des scripts de surface (pouvant se déclencher lorsque le joueur marche desus)
def i104_mapscript():
    return(["""loadtext(1)""",
            """infobox()"""])
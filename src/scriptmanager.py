#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Gestion des scripts"""

import pygame as pg
from copy import copy
from random import randint
import sqlite3 as sql

import menu
import scripts
import dialogue as dia

class ScriptManager():
    """Classe de gestion des scripts du jeu"""
    # TODO Supprimer les save.commit()
    def __init__(self, game):
        self.game = game
        self.list_of_scripts = []
        self.current_command = 0
        self.current_npc = None

        self.abort = False # Arrêt forcé d'un script

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
        if self.current_npc is None:
            self.current_npc = npc      # Si le SM gère déjà un PNJ alors on n'y touche pas
        self.game.input_lock = True     # Blocage du clavier jusqu'à la fin du script
        self.game.script_tree.append([script, 0])
    
    # Fonctions de lecture et d'écriture de la sauvegarde
        
    def read_flags(self, map_id):
        """Obtient l'état des flags de la map d'ID donnée. -1 pour la map actuelle"""
        corrected_map_id = self.game.map_manager.map_id if map_id == -1 else map_id
        return(eval(self.game.save.execute("select flags from maps where map_id = ?;", (corrected_map_id,)).fetchall()[0][0]))
    
    def write_flags(self, map_id, flag_id, value):
        """Modifie la valeur d'un flag d'une map donnée"""
        mapscript_trig = self.game.save.execute("select mapscript_triggered from maps where map_id = ?;", (map_id,)).fetchall()[0][0] # Valeur inchangée
        new_flags = [self.read_flags(map_id)[flag] if flag != flag_id else value for flag in range(len(self.read_flags(map_id)))]
        self.game.save.execute("replace into maps values (?,?,?);", (map_id, mapscript_trig, f"{new_flags}"))
        self.game.save.commit()
    
    def read_npcflags(self, npc_id):
        """Obtient l'état des flags du PNJ d'ID donné"""
        return(eval(self.game.save.execute("select flags from npc where npc_id = ?;", (npc_id,)).fetchall()[0][0]))
    
    def write_npcflags(self, npc_id, flag_id, value):
        """Modifie la valeur d'un flag d'un NPC donné"""
        new_flags = [self.read_npcflags(npc_id)[flag] if flag != flag_id else value for flag in range(len(self.read_npcflags(npc_id)))]
        self.game.save.execute("replace into npc values (?,?);", (npc_id, f"{new_flags}"))
    
    def read_event(self, event_tag):
        """Retourne l'état de l'event spécifié (chiffre binaire), None s'il n'existe pas"""
        try:
            st = self.game.save.execute("select state from events where tag = ?;", (event_tag,)).fetchall()[0][0]
            return(st)
        except:
            return(None)

    def change_event(self, event_tag, state):
        """Commute l'état du drapeau d'un event étant donné son nom.\n
        Si l'event n'existe pas, il est créé et son état est initialisé.\n
        state est un chiffre binaire"""
        try:
            self.game.save.execute("insert into events values (?, ?);", (event_tag, state))
        except:
            self.game.save.execute("update events set state = ? where tag = ?;", (state, event_tag))
    
    def exit_movingscript(self):
        """Terminaison d'un script de déplacement"""
        self.game.executing_moving_script = False
    
    def current_script_command(self):
        """N° de la commande en cours d'exécution dans le script courant"""
        return(self.game.script_tree[-1][1])

    def update(self):
        if self.game.running_script is None and self.game.script_tree != []:
            self.game.running_script = self.game.script_tree[0][0] # Premier élément de la liste qui en comporte un seul à l'appel d'un script
        if self.game.running_script is not None:
            self.game.running_script = self.game.script_tree[-1][0] # Vérification de l'appel ou non d'un sous-script
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
            elif self.game.dialogue is not None or self.game.menu_manager.choicebox is not None:    # On laisse le dialogue défiler s'il existe, ou ou attend les résultats de la choicebox
                pass
            elif self.current_script_command() >= len(self.game.running_script.contents) or self.abort: # Le script courant est terminé ou on force l'arrêt
                del(self.game.script_tree[-1])
                if len(self.game.script_tree) > 0: # Le script a appelé un autre script entretemps
                    self.game.running_script = self.game.script_tree[-1]
                else: # Fin des appels de scripts
                    self.game.running_script = None # Fin du script de départ atteinte
                    self.current_npc = None         # On a fini de traiter le NPC actuel
                    self.abort = False
                    self.game.input_lock = False    # Déblocage du clavier
            else: # Le jeu est disponible pour passer à l'étape suivante
                start = self.game.running_script
                command = "self." + self.game.running_script.contents[self.current_script_command()] # Correction syntaxique
                eval(command)
                if self.game.script_tree[-1][0] == start: # Le script en cours de traitement est le même
                    self.game.script_tree[-1][1] += 1 # Augmentation du n° de la commande courante
                else: # Le script en cours de traitement vient d'être appelé
                    self.game.script_tree[-2][1] += 1

    ###################################
    # Définition du langage des scripts

    # Fonctions générales
    def runscript(self, script):
        """Exécution d'un autre script"""
        self.execute_script(self.find_script_from_name(script))
    
    def interrupt(self):
        """Interruption de l'exécution du script courant"""
        self.abort = True
    
    def label(self, name):
        """Commande indiquant un label accessible via la fonction goto. Ne fait rien en elle-même"""
        pass

    def goto(self, label_tag):
        """Saut vers un label"""
        if label_tag in self.game.running_script.labels:
            self.game.script_tree[-1][1] = self.game.running_script.labels[label_tag]
    
    def save(self):
        """Sauvegarde de la partie"""
        try:
            self.game.player.save()
            self.game.bag.save()
            self.game.save.commit()
        except sql.ProgrammingError:
            print("Impossible d'accéder à la base de donnée lors de la sauvegarde. Cela peut être dû à une réinitialisation des données...")


    # Fonctions graphiques
    def changelayer(self, layer):
        """Déplacement du sprite du joueur sur un nouveau calque"""
        if layer == "bg":
            self.game.map_manager.player_layer(-9)
        if layer == "fg":
            self.game.map_manager.player_layer(1)

    def move(self, direction, pix, sprint = False):
        """Exécution d'un script de déplacement"""
        self.game.executing_moving_script = True
        self.initial_coords = copy(self.game.player.position)
        self.moving_direction = direction
        self.movement_boundary = pix
        self.sprint_during_script = sprint

    # Fonctions des menus (boîtes contenant du texte)
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
    
    def opencb(self, choices = ["OUI", "NON"]):         # Temporaire : uniquement des boîtes Oui / Non
        """Ouverture d'une boîte à choix multiples"""
        self.game.menu_manager.open_choicebox(choices)
    
    def cb_result(self):
        """Obtention de l'option choisie à la choicebox précédente.\n
        Le résultat est stocké dans l'accumulateur numérique"""
        self.acc = self.game.menu_manager.choicebox_result[0]

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
    
    def true(self):
        """Changement de la valeur de l'accumulateur booléen en True"""
        self.boolacc = True
    
    def false(self):
        """Changement de la valeur de l'accumulateur booléen en False"""
        self.boolacc = False
    
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
    
    def put(self, value):
        """Place un entier défini dans l'accumulateur"""
        self.acc = value
    
    def compare(self, operator, qty):
        """Opération logique sur la valeur de acc. Le résultat est stocké dans l'accumulateur booléen"""
        if operator == "sup":
            self.boolacc = (self.acc >= qty)
        elif operator == "inf":
            self.boolacc = (self.acc <= qty)
        elif operator == "eq":
            self.boolacc = (self.acc == qty)
    
    def math(self, operator, operand):
        """Opération arithmétique sur la valeur de acc"""
        if operator == "/" and operand == 0:
            self.acc = 10**30 # Valeur arbitraire pour désigner l'infini
            print(self.acc)
        else:
            eval(f"self.acc {operator}= {operand}")


    # Fonctions sonores
    def chg_music(self, track):
        """Changement de la musique courante"""
        self.game.map_manager.sound_manager.play_music(track)
    
    def sfx(self, fx):
        """Joue un effet sonore"""
        self.game.map_manager.sound_manager.play_sfx(fx)

    # Fonctions des objets
    def get_object(self, object_id, qty):
        """Obtention d'un objet en une quantité donnée"""
        self.game.bag.increment_item(object_id, qty)
    
    def toss_object(self, object_id, qty):
        """Destruction d'un objet en une quantité donnée, les supprime tous s'il n'y en a pas assez"""
        corrected_qty = self.game.bag.contents[object_id] if qty == "all" else qty     # Valeur arbitrairement grande
        if self.game.bag.contents[object_id] >= corrected_qty:
            self.game.bag.increment_item(object_id, -corrected_qty)
    
    
    # Fonctions des drapeaux des salles
    def testflag(self, map_id, flag_id):
        """Obtention de l'état d'un drapeau\n
        Passer -1 en tant que valeur de map_id retourne l'état du flag de la map actuelle"""
        if map_id == -1:
            self.boolacc = True if self.read_flags(self.game.map_manager.map_id)[flag_id] == 1 else False
        else:
            self.boolacc = True if self.read_flags(map_id)[flag_id] == 1 else False
    
    def raiseflag(self, map_id, flag_id):
        """Lève le drapeau d'une salle\n
        Passer -1 en tant que valeur de map_id lève le drapeau de la map actuelle\n
        Sans effet sur les flags déjà levés"""
        if map_id == -1:
            self.write_flags(self.game.map_manager.map_id, flag_id, 1)
        else:
            self.write_flags(map_id, flag_id, 1)
    
    def lowerflag(self, map_id, flag_id):
        """Baisse le drapeau d'une salle\n
        Passer -1 en tant que valeur de map_id baisse le drapeau de la map actuelle\n
        Sans effet sur les flags déjà baissés"""
        if map_id == -1:
            self.write_flags(self.game.map_manager.map_id, flag_id, 0)
        else:
            self.write_flags(map_id, flag_id, 0)
    
    # Fonctions des drapeaux généraux "events"
    def checkevent(self, event_tag):
        """Met dans l'accumulateur booléen l'état de l'event spécifié, ou False s'il est inexistant"""
        res = self.read_event(event_tag)
        self.boolacc = res if res is not None else False

    def raiseevent(self, event_tag):
        """Lève le drapeau lié à l'event\n
        Si l'event n'existe pas, un nouveau est créé"""
        self.change_event(event_tag, 1)
    
    def lowerevent(self, event_tag):
        """Baisse le drapeau lié à l'event"""
        self.change_event(event_tag, 0)
    
    # Fonctions des PNJ
    def checknpcflag(self, npc, flag_id):
        """Vérification d'un flag d'un NPC"""
        self.boolacc = True if self.read_npcflags(npc.id)[flag_id] == 1 else False
    
    def setnpcflag(self, npc, flag_id, state):
        """Mise à jour du flag d'un NPC"""
        self.write_npcflags(npc.id, flag_id, state)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Gestion des scripts"""

from random import randint
import sqlite3 as sql
import copy
import os
import pygame as pg

import scripts
import dialogue as dia
import menu

class ScriptManager():
    """Classe de gestion des scripts du jeu"""
    SCRIPTS_FOLDER = "res/scripts/"

    def __init__(self, game):
        self.game = game
        self.list_of_scripts = []
        self.current_command = 0
        self.current_npc = None

        self.abort = False # Arrêt forcé d'un script
        self.unlocking = False      # Déverrouillage des commandes
        self.perblock = False       # Régulation de l'exécution des scripts permanents
        self.scripts_are_permanent = False    # Statut des scripts en cours d'exécution

        # Mémoire ROM
        self.permanent_scripts = []        # Liste des scripts s'exécutant à chaque game tick

        # Mémoire interne du gestionnaire de scripts
        self.boolacc = False # Accumulateur booléen utilisé lors des comparaisons
        self.acc = 0 # Accumulateur entier
        self.saved_position = (-1, -1)   # Accumulateur des coordonnées
        self.saved_map = None            # Accumulateur de l'ID de la map actuelle
        self.infobox_contents = [] # Accumulateur de l'infobox, pourra être modifié si un script nécessite une accumulation d'éléments
        self.tick_counter = 0      # Compteur de ticks pour la fonction nop
        self.is_counting_ticks = False     # Drapeau de comptage des ticks
        self.noping_time = 0               # Durée de la fonction nop

        # Caractéristiques du script de mouvement
        self.movement_boundary = None # Longueur du déplacement
        self.moving_direction = None
        self.wait_movements = False     # Attente de la terminaison de tous les mouvements pour continuer

        # Chargement de la liste des scripts
        self.parse_scripts()
    
    def parse_scripts(self):
        for filename in os.listdir(self.SCRIPTS_FOLDER):
            filepath = os.path.join(self.SCRIPTS_FOLDER, filename)
            if os.path.isfile(filepath):
                file = open(filepath, 'r', encoding = 'utf-8')
                script = []
                while True:
                    line = file.readline().strip()
                    if line == "eof":
                        break
                    elif line == "" or line[0:1] == "//":     # Ligne vide ou commentaire
                        pass
                    elif line[0] == '$':
                        name = line[1:]
                        try:
                            id = self.game.game_data_db.execute("select id from scripts where name = ?;", (name, )).fetchall()[0][0]
                        except IndexError:
                            print(f"Le script {name} n'a pas d'identifiant. Modifier la BDD afin d'inclure ce script !")
                        command = file.readline().strip()
                        while command != "$$$":
                            if command != "" and command[:2] != "//":
                                script.append(command)
                            command = file.readline().strip()
                        self.list_of_scripts.append(scripts.Script(id, name, script))
                        if "persistent" in filepath:
                            self.permanent_scripts.append(scripts.Script(id, name, script))
                        script = []

    def get_script_from_id(self, ident):
        """Retourne un script étant donné un identifiant"""
        pos = [script.id for script in self.list_of_scripts].index(ident)
        return(self.list_of_scripts[pos])
    
    def find_script_from_name(self, name):
        """Retourne l'ID d'un script étant donné son nom"""
        pos = [script.name for script in self.list_of_scripts].index(name)
        return(self.list_of_scripts[pos])

    def execute_script(self, script, side, npc = None):
        """Exécution d'un script"""
        if type(script) is not scripts.Script:
            raise TypeError("Erreur : l'objet source n'est pas un script")
        if self.current_npc is None:
            self.current_npc = npc      # Si le SM gère déjà un PNJ alors on n'y touche pas
        if script not in self.permanent_scripts:
            self.game.input_lock = True     # Blocage du clavier jusqu'à la fin du script s'il n'est pas permanent
            self.scripts_are_permanent = False
        else:
            self.scripts_are_permanent = True
        if side == "back":
            self.game.script_tree.insert(0, [script, 0])    # Priorité aux autres scripts (appel d'un script dans un script...)
        if side == "front":
            self.game.script_tree.append([script, 0])       # Priorité à ce script (appel d'un script permanent...)
    
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
        self.game.input_lock = False
    
    def current_script_command(self):
        """N° de la commande en cours d'exécution dans le script courant"""
        return(self.game.script_tree[-1][1])
    
    def ask_unlock(self):
        self.unlocking = True
    
    def wait(self):
        self.wait_movements = True

    def update(self):
        if self.game.running_script is None and self.game.script_tree != []:
            self.game.running_script = self.game.script_tree[0][0]  # Premier élément de la liste qui en comporte un seul à l'appel d'un script
        if self.game.running_script is not None:
            self.perblock = True                                    # Blocage de l'exécution des scripts permanents
            self.game.running_script = self.game.script_tree[-1][0] # Vérification de l'appel ou non d'un sous-script
            if self.is_counting_ticks:                              # Temps de latence
                self.tick_counter += 1
                if self.tick_counter >= self.noping_time:           # Fin du temps de latence
                    self.is_counting_ticks = False
                    self.tick_counter = 0
            elif self.game.dialogue is not None or self.game.menu_manager.choicebox is not None or self.game.mgm_manager.running_mg is not None or self.wait_movements:    # Attente d'une action extérieure à l'exécution
                pass
            elif self.current_script_command() >= len(self.game.running_script.contents) or self.abort: # Le script courant est terminé ou on force l'arrêt
                del(self.game.script_tree[-1])
                if len(self.game.script_tree) > 0:  # Le script a appelé un autre script entretemps
                    self.game.running_script = self.game.script_tree[-1]
                else: # Fin des appels de scripts
                    self.game.running_script = None # Fin du script de départ atteinte
                    self.current_npc = None         # On a fini de traiter le NPC actuel
                    self.abort = False
                    self.scripts_are_permanent = False
                    self.perblock = False           # Autorisation d'exécuter les scripts permanents
                    self.game.input_lock = False    # Déblocage du clavier
                    self.game.map_manager.npc_manager.flip()    # Rotation des PNJ d'origine
                    self.game.map_manager.npc_manager.talking_npcs = []    # On a fini de parler aux PNJ
            else: # Le jeu est disponible pour passer à l'étape suivante
                start = self.game.running_script
                command = f"self.{self.game.running_script.contents[self.current_script_command()]}" # Correction syntaxique
                eval(command)
                if self.game.script_tree[-1][0] == start: # Le script en cours de traitement est le même
                    self.game.script_tree[-1][1] += 1 # Augmentation du n° de la commande courante
                else: # Le script en cours de traitement vient d'être appelé
                    self.game.script_tree[-2][1] += 1
        if self.game.executing_moving_script:       # Déplacements en cours
            if self.game.persistent_move != {}:
                for id in self.game.persistent_move:
                    if id not in self.game.moving_people:
                        self.game.moving_people[id] = copy.deepcopy(self.game.persistent_move[id][self.game.persistent_move_index[id]])
                        if self.game.persistent_move_index[id] < len(self.game.persistent_move[id]) - 1:
                            self.game.persistent_move_index[id] += 1
                        else:
                            self.game.persistent_move_index[id] = 0
            moving = copy.deepcopy(self.game.moving_people)
            for person in self.game.moving_people:      #! à optimiser
                try:
                    if person != "player":
                        npc = self.game.map_manager.npc_manager.find_npc(person)
                    if self.unlocking and "player" not in self.game.moving_people and "player" not in [data[0] for data in self.game.movement_mem]:
                        self.game.input_lock = False
                        self.unlocking = False
                    if person == "player":
                        self.game.input_lock = True
                        self.perblock = True
                    if self.game.dialogue is None:
                        if self.game.moving_people[person]["moving_direction"] == "up" and person == "player":
                            self.game.player.move([True, False, False, False], self.game.moving_people[person]["sprint_during_script"])
                        elif self.game.moving_people[person]["moving_direction"] == "right" and person == "player":
                            self.game.player.move([False, True, False, False], self.game.moving_people[person]["sprint_during_script"])
                        elif self.game.moving_people[person]["moving_direction"] == "down" and person == "player":
                            self.game.player.move([False, False, True, False], self.game.moving_people[person]["sprint_during_script"])
                        elif self.game.moving_people[person]["moving_direction"] == "left" and person == "player":
                            self.game.player.move([False, False, False, True], self.game.moving_people[person]["sprint_during_script"])
                        else:
                            if self.game.moving_people[person]["moving_direction"] == "up":
                                npc.move([True, False, False, False], self.game.moving_people[person]["sprint_during_script"])
                            if self.game.moving_people[person]["moving_direction"] == "right":
                                npc.move([False, True, False, False], self.game.moving_people[person]["sprint_during_script"])
                            if self.game.moving_people[person]["moving_direction"] == "down":
                                npc.move([False, False, True, False], self.game.moving_people[person]["sprint_during_script"])
                            if self.game.moving_people[person]["moving_direction"] == "left":
                                npc.move([False, False, False, True], self.game.moving_people[person]["sprint_during_script"])
                    if person == "player":
                        dist = ((self.game.moving_people["player"]["initial_coords"][0] - self.game.player.position[0])**2 + (self.game.moving_people["player"]["initial_coords"][1] - self.game.player.position[1])**2) ** 0.5 # Distance totale parcourue pendant le script
                    else:
                        dist = ((self.game.moving_people[person]["initial_coords"][0] - npc.position[0])**2 + (self.game.moving_people[person]["initial_coords"][1] - npc.position[1])**2) ** 0.5 # Distance totale parcourue pendant le script
                        
                    if self.game.player.boop and person == "player": # Arrêt du mouvement suite à une collision (joueur)
                        print("debug : script_boop")
                        del(moving[person])
                        for mov in range(len(self.game.movement_mem)):
                            if self.game.movement_mem[mov][0] == "player":
                                moving["player"] = copy.deepcopy(self.game.movement_mem[mov][1])
                                moving["player"]["initial_coords"] = self.game.player.position
                                del(self.game.movement_mem[mov])
                                break
                    elif dist > self.game.moving_people[person]["movement_boundary"]: # Le mouvement s'est déroulé normalement ou le joueur s'est pris un mur
                        del(moving[person])
                        for mov in range(len(self.game.movement_mem)):
                            if self.game.movement_mem[mov][0] == person:
                                moving[person] = copy.deepcopy(self.game.movement_mem[mov][1])          # Mise à jour du mouvement du personnage
                                if person == "player":
                                    moving["player"]["initial_coords"] = self.game.player.position
                                else:
                                    moving[person]["initial_coords"] = npc.position            # Actualisation des coordonnées de démarrage du mouvement
                                del(self.game.movement_mem[mov])
                                break
                    elif npc.boop:          # Arrêt du mouvement suite à une collision (pnj)
                        del(moving[npc.id])
                        for mov in range(len(self.game.movement_mem)):
                            if self.game.movement_mem[mov][0] == npc.id:
                                moving[npc.id] = copy.deepcopy(self.game.movement_mem[mov][1])          # Mise à jour du mouvement du personnage
                                moving[npc.id]["initial_coords"] = npc.position            # Actualisation des coordonnées de démarrage du mouvement
                                del(self.game.movement_mem[mov])
                                break
                except:
                    pass
                if moving == {} and self.game.movement_mem == [] and self.game.persistent_move == {}:
                    self.exit_movingscript()
                    self.wait_movements = False
            self.game.moving_people = copy.deepcopy(moving)
            

    ###################################
    # Définition du langage des scripts

    # Fonctions générales
    def nop(self, ticks):
        """Fonction qui ne fait rien pendant un nombre donné de ticks"""
        self.noping_time = ticks
        self.is_counting_ticks = True

    def runscript(self, script, side = "front"):
        """Exécution d'un autre script"""
        self.execute_script(self.find_script_from_name(script), side)
    
    def interrupt(self):
        """Interruption de l'exécution de tous les scripts en mémoire"""
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
            self.game.internal_clock.save()
            self.game.player.save()
            self.game.bag.save()
            self.game.mission_manager.save()
            self.game.save.commit()
        except sql.ProgrammingError:
            print("Impossible d'accéder à la base de donnée lors de la sauvegarde. Cela peut être dû à une réinitialisation des données...")

    def inputlock(self):
        """Verrouillage des commandes"""
        self.game.input_lock = True
    
    def freeinputs(self):
        """Déverrouillage des commandes"""
        self.ask_unlock()
    
    def blockpersistents(self):
        """Empêche l'exécution des scripts persistents"""
        self.perblock = True
    
    def unblockpersistents(self):
        """Permet à nouveau l'exécution des scripts persistents"""
        self.perblock = False
    
    def print(self, text):
        """Fonction print de Python"""
        print(text)


    # Fonctions graphiques et de mouvement
    def changelayer(self, layer):
        """Déplacement du sprite du joueur sur un nouveau calque"""
        if layer == "bg":
            self.game.map_manager.player_layer(-9)
        if layer == "fg":
            self.game.map_manager.player_layer(1)
    
    def emotion(self, boxname, entity):
        """Déclenchement de l'apparition d'une émoticône au-dessus du sprite d'une entité"""
        #TODO Voir comment faire apparaître une minibox au dessus du sprite d'un pnj. Coordonnées touça touça
        verticaloffset = 35
        if entity == "player":
            center = (self.game.screen.get_size()[0]/2, self.game.screen.get_size()[1]/2 + verticaloffset)
        self.game.menu_manager.minibox = menu.MiniBox(self.game, boxname, "player")
    
    def clearboxes(self):
        self.game.menu_manager.minibox = None
    
    def setdirection(self, id, direction):
        """Change la direction dans laquelle pointe un PNJ"""
        if id == "player":
            if direction == "up":
                self.game.player.fix_direction([0, -1])
            if direction == "down":
                self.game.player.fix_direction([0, 1])
            if direction == "left":
                self.game.player.fix_direction([-1, 0])
            if direction == "right":
                self.game.player.fix_direction([1, 0])
        else:
            npc = self.game.map_manager.npc_manager.find_npc(id)
            if npc is not None:
                if direction == "up":
                    npc.fix_direction([0, -1])
                if direction == "down":
                    npc.fix_direction([0, 1])
                if direction == "left":
                    npc.fix_direction([-1, 0])
                if direction == "right":
                    npc.fix_direction([1, 0])

    def startmoving(self):
        """Démarrage des mouvements mis en mémoire"""
        self.game.executing_moving_script = True
    
    def waitforstop(self):
        """Attente de la terminaison de tous les mouvements avant de continuer l'exécution du script"""
        self.wait()

    def move(self, id, direction, pix, sprint = False):
        """Mise en mémoire du déplacement d'une entité"""
        if id == "player" and "player" not in self.game.moving_people:
            self.game.moving_people["player"] = {"initial_coords" : copy.deepcopy(self.game.player.position),
                                                 "moving_direction" : direction,
                                                 "movement_boundary" : pix,
                                                 "sprint_during_script" : sprint}
        elif id == "player":
            self.game.movement_mem.append(["player", {"initial_coords" : copy.deepcopy(self.game.player.position),
                                                      "moving_direction" : direction,
                                                      "movement_boundary" : pix,
                                                      "sprint_during_script" : sprint}])
        else:
            npc = self.game.map_manager.npc_manager.find_npc(id)
            if npc is not None:
                if id not in self.game.moving_people:
                    self.game.moving_people[id] = {"initial_coords" : npc.position,
                                                   "moving_direction" : direction,
                                                   "movement_boundary" : pix,
                                                   "sprint_during_script" : sprint}
                else:
                    self.game.movement_mem.append([id, {"initial_coords" : npc.position,
                                                        "moving_direction" : direction,
                                                        "movement_boundary" : pix,
                                                        "sprint_during_script" : sprint}])
    
    def compx(self, op, coord):
        """Comparaison de la coordonnée x du joueur"""
        if op == "sup":
            self.boolacc = True if self.game.player.position[0] > coord else False
        if op == "inf":
            self.boolacc = True if self.game.player.position[0] < coord else False
    
    def compy(self, op, coord):
        """Comparaison de la coordonnée y du joueur"""
        if op == "sup":
            self.boolacc = True if self.game.player.position[1] > coord else False
        if op == "inf":
            self.boolacc = True if self.game.player.position[1] < coord else False
    
    def watchroom(self, id):
        """Comparaison de l'ID de la salle actuelle"""
        self.boolacc = True if self.game.map_manager.map_id == id else False

    def persistent(self, id, direction, pix, sprint = False):
        """Mise en mémoire du mouvement permanent d'un PNJ"""
        assert type(id) is int, "Erreur : persistent prend en entrée l'ID d'un PNJ uniquement."
        npc = self.game.map_manager.npc_manager.find_npc(id)
        if id not in self.game.persistent_move:
            self.game.persistent_move[id] = {}
        self.game.persistent_move[id][len(self.game.persistent_move[id])] = {"initial_coords" : npc.position,
                                         "moving_direction" : direction,
                                         "movement_boundary" : pix,
                                         "sprint_during_script" : sprint}
        self.game.persistent_move_index[id] = 0         # Initialisation du mouvement permanent
    
    def stopnpc(self, id):
        """Suppression du mouvement permanent d'un PNJ"""
        assert type(id) is int, "Erreur : seul le mouvement d'un PNJ peut être arrêté."
        npc = self.game.map_manager.npc_manager.find_npc(id)
        if id in self.game.persistent_move:
            del(self.game.persistent_move[id])

    def offrails(self, id):
        """Suppression du mouvement permanent d'un PNJ"""
        if id in self.game.persistent_move:
            del(self.game.persistent_move[id])
    
    def warp(self, target_map, target_coords, direction = "up"):
        """Téléportation du joueur vers une nouvelle map"""
        self.game.player.warp(target_map, target_coords, direction, self.game.map_manager.sound_manager.music_file)
        self.game.player.is_warping = True
    

    # Fonctions du temps
    def getday(self):
        """Obtention du numéro du jour courant"""
        self.acc = self.game.internal_clock.weekday
    
    def advance(self, minutes):
        """Passage d'un nombre donné de minutes"""
        self.game.internal_clock.minute += minutes
        self.game.internal_clock.hour += self.game.internal_clock.minute // 60
        self.game.internal_clock.weekday += self.game.internal_clock.hour // 24
        self.game.internal_clock.weekday = self.game.internal_clock.weekday % 7
        self.game.internal_clock.hour = self.game.internal_clock.hour % 24
        self.game.internal_clock.minute = self.game.internal_clock.minute % 60

    def passtime(self):
        """Passage au jour suivant"""
        if self.game.internal_clock.hour >= 7:
            self.game.internal_clock.weekday = (self.game.internal_clock.weekday + 1) % 6
        self.game.internal_clock.hour = 7
        self.game.internal_clock.minute = 0
        self.game.internal_clock.find_dayname()
    
    def comphour(self, op, hour):
        """Opération de comparaison avec l'heure courante"""
        if op == 'sup':
            self.boolacc = True if self.game.internal_clock.hour > hour else False
        if op == 'inf':
            self.boolacc = True if self.game.internal_clock.hour < hour else False
        if op == 'eq':
            self.boolacc = True if self.game.internal_clock.hour == hour else False
    
    def compmin(self, op, min):
        """Opération de comparaison avec les minutes courantes"""
        if op == 'sup':
            self.boolacc = True if self.game.internal_clock.minute > min else False
        if op == 'inf':
            self.boolacc = True if self.game.internal_clock.minute < min else False
        if op == 'eq':
            self.boolacc = True if self.game.internal_clock.minute == min else False


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
        elif operator == "+":
            self.acc += operand
        elif operator == "-":
            self.acc -= operand
        elif operator == "/":
            self.acc /= operand
        elif operator == "*":
            self.acc *= operand


    # Fonctions sonores
    def chg_music(self, track):
        """Changement de la musique courante"""
        self.game.map_manager.sound_manager.play_music(track, track)
    
    def sfx(self, fx):
        """Joue un effet sonore"""
        self.game.map_manager.sound_manager.play_sfx(fx)


    # Fonctions des objets
    def get_object(self, object_id, qty):
        """Obtention d'un objet en une quantité donnée"""
        self.game.bag.increment_item(object_id, qty)
        self.game.menu_manager.sidemenu.bagmenu.refresh_groups()                    # Actualisation de l'affichage
        print(self.game.menu_manager.sidemenu.bagmenu.groups)
    
    def toss_object(self, object_id, qty):
        """Destruction d'un objet en une quantité donnée, les supprime tous s'il n'y en a pas assez"""
        try:
            corrected_qty = self.game.bag.contents[object_id] if qty == "all" else qty
            if self.game.bag.contents[object_id] >= corrected_qty:
                self.game.bag.increment_item(object_id, -corrected_qty)
                print("c")
        except KeyError:        # L'objet en question est inexistant
            pass
        self.game.menu_manager.sidemenu.bagmenu.refresh_groups()                    # Actualisation de l'affichage


    # Fonctions des caractéristiques du joueur
    def energy(self, op, qty):
        """Comparaison de l'énergie actuelle du joueur"""
        if op == 'sup':
            self.boolacc = True if self.game.player.stamina > qty else False
        if op == 'inf':
            self.boolacc = True if self.game.player.stamina < qty else False
        if op == 'eq':
            self.boolacc = True if self.game.player.stamina == qty else False
    
    def energize(self, qty):
        """Changement de l'énergie du joueur"""
        self.game.player.stamina += qty
    
    def set_energy(self, qty):
        """Changement de l'énergie du joueur (valeur fixe)"""
        self.game.player.stamina = qty
    
    def pospoint(self):
        """Sauvegarde de la position actuelle du joueur"""
        self.saved_position = copy.deepcopy(self.game.player.position)
        self.saved_map = self.game.map_manager.map_id
    
    def recallpos(self):
        """Warp aux coordonnées enregistrées"""
        self.warp(self.saved_map, self.saved_position, "up")
    
    def compcash(self, op, qty):
        """Comparaison de la qté d'argent du joueur"""
        if op == 'sup':
            self.boolacc = True if self.game.player.cash > qty else False
        if op == 'inf':
            self.boolacc = True if self.game.player.cash < qty else False
        if op == 'eq':
            self.boolacc = True if self.game.player.cash == qty else False
    
    def givecash(self, qty):
        """Changement de la qté d'argent du joueur"""
        self.game.player.cash += qty


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


    # Fonctions des minijeux
    # ! WIP
    def launchmgm(self, mgm, *args):
        """Lancement d'un mini-jeu"""
        self.game.mgm_manager.launch(mgm, *args)
    
    # Fonctions des missions
    def mistate(self, id, state):
        """Change la progression générale d'une mission"""
        if id not in [mission.id for mission in list(self.game.mission_manager.dict_of_missions.values())]:
            print("L'ID demandé ne correspond à aucune mission !")
        elif state not in (0, 1, 2, 3, 4):
            print("L'état demandé n'est pas un état valide.")
        else:
            self.game.mission_manager.dict_of_missions[id].current_status = ["blank", "new", "inprogress", "claim", "done"][state]
            if state == 1:
                self.raiseevent(f"discoveredMission{id}")
            if state == 3:
                self.raiseevent(f"unclaimedMission{id}")
            if state == 4:
                self.raiseevent(f"clearedMission{id}")        # Levage du drapeau correspondant
    
    def miadv(self, id, adv):
        """Change l'étape en cours d'une mission"""
        if id not in [mission.id for mission in list(self.game.mission_manager.dict_of_missions.values())]:
            print("L'ID demandé ne correspond à aucune mission !")
        else:
            mission = self.game.mission_manager.dict_of_missions[id]
            if adv > mission.max_adv:
                print("L'avancement demandé est invalide.")
            else:
                mission.current_adv = adv
    
    def checkadv(self, id, op, adv):
        """Vérifie si un avancement est atteint pour une mission donnée"""
        if op == 'sup':
            self.boolacc = True if self.game.mission_manager.dict_of_missions[id].current_adv >= adv else False
        if op == 'eq':
            self.boolacc = True if self.game.mission_manager.dict_of_missions[id].current_adv == adv else False
        if op == 'inf':
            self.boolacc = True if self.game.mission_manager.dict_of_missions[id].current_adv <= adv else False
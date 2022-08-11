#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gestion de l'affichage de bulles de texte
"""

# Import externe
import pygame as pg
import sqlite3 as sql
import numpy as np

import locale


class Dialogue():
    TALKBOX_TEX_LOCATION = "res/textures/talk_box_next.png"
    INFOBOX_TEX_LOCATION = "res/textures/infobox.png"

    SOUND_LOCATION = "res/sounds/fx/typewriter.wav"
    NAMETAG_POSITION = (30, 45)
    TEXT_POSITION = (30, 100)
    FONT = "consolas" # TODO Appel de la police depuis menu
    FONT_SIZE = 16

    def __init__(self, game, npc, is_infobox, dialogue_id = 2, infobox_text = []):
        # Objets liés
        self.game = game
        self.current_npc = npc # TODO Implémenter mieux les infobox, au lieu de passer en argument un NPC "fantôme"
        self.dialogue_id = dialogue_id # TODO Dialogue "fantôme"
        self.is_infobox = is_infobox

        # Etat
        self.is_writing = True
        self.game.player.can_move = False

        # Graphique
        if self.is_infobox:
            self.box_surf = pg.image.load(self.INFOBOX_TEX_LOCATION).convert()
        else:
            self.box_surf = pg.image.load(self.TALKBOX_TEX_LOCATION).convert()
        self.box_x = int(self.box_surf.get_width()*0.75)
        self.box_y = int(self.box_surf.get_height()*0.75)
        self.box_img = pg.transform.scale(self.box_surf, (self.box_x, self.box_y))
        self.box_img.set_colorkey([255, 255, 255])
        self.tw_sound = pg.mixer.Sound(self.SOUND_LOCATION)

        # Gestion de l'affichage partiel du texte
        self.lettre_cooldown = 5
        self.current_text = ""                                   # texte actuel
        self.current_text_id = -1                                # id du texte actuel
        self.current_letter_id = -1                              # lettre actuelle
        self.current_row = 0                                     # ligne actuelle

        # Texte
        self.texts = []
        if self.is_infobox:
            for line in infobox_text:
                if type(line) == int:       # Chaîne du fichier locale
                    self.texts.append(locale.get_substring("infobox", line))
                if type(line) == str:       # Chaîne en brut
                    self.texts.append(line)
        else:
            self.texts = self.game.game_data_db.execute("SELECT text_id FROM npc_dialogue WHERE id_npc = ? AND id_dialogue = ? ORDER BY ligne_dialogue ASC", (self.current_npc.id, self.dialogue_id)).fetchall()
            for id in range(len(self.texts)):
                text = locale.get_substring("dialogue", self.texts[id][0])
                self.texts[id] = text  # Conversion de l'ID en texte
            if len(self.texts) == 0: # Le dialogue demandé n'existe pas
                raise ValueError(f"Erreur : le dialogue d'ID {self.dialogue_id} du NPC {self.current_npc.id} n'existe pas ou est vide")

        # Police TODO Utilisation de la classe Font (menu)
        self.font = pg.font.SysFont(self.FONT, self.FONT_SIZE)
        self.font_width = max([metric[1] for metric in self.font.metrics("azertyuiopqsdfghjklmwxcvbnAZERTYUIOPQSDFGHJKLMWXCVBN")]) # Chasse maximale pour la police choisie

        self.row_length = self.box_x / self.font_width - 7       # longueur max d'une ligne de texte. TODO enlever le -7, solution temporaire
        self.row_height = self.font.get_linesize()
        self.text_position = [self.TEXT_POSITION[0], self.TEXT_POSITION[1] + self.current_row * self.row_height]        # position du texte à afficher

        #Affichage du début du texte
        self.new_line()

    def refresh_text_position(self):
        """Actualisation de la position du texte à afficher"""
        self.text_position = [self.TEXT_POSITION[0], self.TEXT_POSITION[1] + self.current_row * self.row_height]

    def format(self, text):
        """Découpage d'un texte en plusieurs lignes de taille adéquate"""
        formatted_text = []
        splitted_text = text.split()
        text_line = ""
        line_length = 0
        while splitted_text != []:
            word_length = len(splitted_text[0])
            if line_length + word_length > self.row_length:
                formatted_text.append(text_line)
                text_line = ""
                line_length = 0
            text_line += splitted_text[0] + " "
            line_length += word_length + 1
            del(splitted_text[0])
        formatted_text.append(text_line)
        return(formatted_text)

    def empty_box(self):
        """Suppression de tout texte présent dans la boîte de dialogue"""
        self.box_img = pg.transform.scale(self.box_surf, (self.box_x, self.box_y))
        self.box_img.set_colorkey([255, 255, 255])

    def close(self):
        """Fermeture du dialogue"""
        self.game.player.can_move = True
        self.game.dialogue = None

    def update(self):
        """Fonction de mise à jour générale"""
        # Affichage de la boîte de dialogue
        self.show_box()
        if self.is_writing:
            # Affichage d'une nouvelle lettre à la fin du cooldown
            if self.game.internal_clock.ticks_since_epoch % self.lettre_cooldown == 0:
                self.new_letter()

    def nametag_show(self):
        """Ecrit le nom du NPC dans la case au dessus de la boîte de dialogue"""
        self.ecrire(self.current_npc.name, self.NAMETAG_POSITION)
        # FIXME : clignotement lors du rafraîchissement de la boîte de dialogue

    def next_dialogue(self):
        """Passe au dialogue suivant lorsque le joueur presse la touche"""
        # Efface le texte précédent
        self.empty_box()
        if not self.is_infobox:
            self.nametag_show()
        if self.is_writing:
            # Cas où le texte est encore en cours d'écriture : on affiche toute la ligne d'un coup
            self.is_writing = False
            self.current_letter_id = -1
            self.current_row = 0
            self.refresh_text_position()
            for line in range(len(self.current_text)):
                self.ecrire(self.current_text[line], self.text_position)
                self.current_row += 1
                self.refresh_text_position()
        else:
            # Cas où tout le texte est écrit : on passe au dialogue suivant
            self.new_line()

    def new_line(self):
        """Passe à la ligne suivante du dialogue"""
        # Efface le texte précédent
        self.empty_box()
        if not self.is_infobox:
            self.nametag_show()
        if self.current_text_id < len(self.texts) - 1:
            # Passage à la ligne de texte suivante
            self.current_text_id += 1
            self.current_text = self.format(self.texts[self.current_text_id])
            self.current_row = 0
            self.refresh_text_position()
            self.is_writing = True
        else:
            # Plus de texte, on ferme la boîte de dialogue
            self.close()

    def new_letter(self):
        """Affiche une nouvelle lettre du texte"""
        if self.current_letter_id < len(self.current_text[self.current_row]) - 1:
            # Nouvelle lettre sur la ligne
            self.current_letter_id += 1
            self.ecrire(self.current_text[self.current_row][:self.current_letter_id+1], self.text_position)

            pg.mixer.Sound.play(self.tw_sound)
            if self.current_letter_id >= len(self.current_text[self.current_row]) - 1 and self.current_row < len(self.current_text) - 1:
                self.current_letter_id = 0
                self.current_row += 1
                self.refresh_text_position()
        else:
            # Tout le texte est écrit, on arrête d'écrire
            self.current_letter_id = -1
            self.is_writing = False

    def ecrire(self, texte, pos, color=(0, 0, 0)):
        """
        Affiche le texte sur le cadre de dialogue
        """
        # FIXME Empêcher l'accumulation de texte
        text_affiche = self.font.render(texte, True, color)
        self.box_img.blit(text_affiche, pos)

    def show_box(self):
        """Affichage graphique de la boîte"""
        rect = self.box_img.get_rect(center=(self.game.screen.get_size()[0]/2, self.game.screen.get_size()[1]-self.box_img.get_height()/2))
        self.game.screen.blit(self.box_img, rect)

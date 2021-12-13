#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gestion des dialogues entre le joueur et les NPC
"""

import pygame as pg
import sqlite3 as sql
import numpy as np

class Dialogue():
    IMAGE_LOCATION = "res/textures/talk_box_next.png"
    SOUND_LOCATION = "res/sounds/sound_effect/typewriter.wav"

    def __init__(self, game, npc):
        self.game = game
        self.current_npc = npc

        #Etat
        self.is_writing = True
        self.game.player.is_talking = True

        #Graphique
        self.talk_box_surf = pg.image.load(self.IMAGE_LOCATION).convert()
        self.talk_box_x = int(self.talk_box_surf.get_width()*0.75)
        self.talk_box_y = int(self.talk_box_surf.get_height()*0.75)
        self.talk_box_img = pg.transform.scale(self.talk_box_surf, (self.talk_box_x, self.talk_box_y))
        self.talk_box_img.set_colorkey([255, 255, 255])
        self.tw_sound = pg.mixer.Sound(self.SOUND_LOCATION)

        #Gestion de l'affichage partiel du texte
        self.lettre_cooldown = 5
        self.current_text = ""                                   # text actuel
        self.current_text_id = -1                                # id du text actuel
        self.current_letter_id = -1                              # lettre actuelle
        self.current_row = 0                                     # ligne actuelle

        #Texte
        self.dialogue_id = 1 #TEMPORAIRE
        self.texts = np.array(self.game.game_data_db.execute("SELECT texte FROM npc_dialogue WHERE id_npc = ? AND id_dialogue = ? ORDER BY ligne_dialogue ASC", (self.current_npc.id, self.dialogue_id)).fetchall())[:,0]
        #Police
        self.font_size = 16
        self.font = pg.font.SysFont("consolas", self.font_size)
        self.font_width = max([metric[1] for metric in self.font.metrics("azertyuiopqsdfghjklmwxcvbnAZERTYUIOPQSDFGHJKLMWXCVBN")]) # Chasse maximale pour la police choisie
        self.row_length = self.talk_box_x / self.font_width - 7       # longueur max d'une ligne de texte. TODO enlever le -7, solution temporaire
        self.row_height = self.font.get_linesize()
        self.text_position = [30, 100 + self.current_row * self.row_height]        # position du texte à afficher

        self.new_line()

    def refresh_text_position(self):
        """Actualisation de la position du texte à afficher"""
        self.text_position = [30, 100 + self.current_row * self.row_height]

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

    def close(self):
        """Fermeture du dialogue"""
        self.game.player.is_talking = False
        self.game.dialogue = None

    def update(self):
        """Fonction de mise à jour générale"""
        self.show_talk_box()  # on affiche limage de la boite de dialgue
        if self.is_writing:
            if self.game.tick_count % self.lettre_cooldown == 0:
                self.new_letter()

    def next_dialogue(self):
        """Passe au dialogue suivant lorsque le joueur presse la touche"""
        self.talk_box_img = pg.transform.scale(
            self.talk_box_surf, (self.talk_box_x, self.talk_box_y))
        self.talk_box_img.set_colorkey([255, 255, 255])
        if self.is_writing:
            self.is_writing = False
            self.current_letter_id = -1
            self.current_row = 0
            self.refresh_text_position()
            for line in range(len(self.current_text)):
                self.ecrire(self.current_text[line], self.text_position)
                self.current_row += 1
                self.refresh_text_position()
        else:
            self.new_line()

    def new_line(self):
        """Passe à la ligne suivante du dialogue"""
        # on "efface" le dialogue precedent
        self.talk_box_img = pg.transform.scale(
            self.talk_box_surf, (self.talk_box_x, self.talk_box_y))
        self.talk_box_img.set_colorkey([255, 255, 255])
        # dans la suite à chaques appels de cette fonction on ajoute 1 à l'id du dialogue actuel sauf si c'est le dernier
        # si c'est le dernier alors le player ne parle plus
        if self.current_text_id < len(self.texts) - 1:
            self.current_text_id += 1
            self.current_text = self.format(self.texts[self.current_text_id])
            self.current_row = 0
            self.refresh_text_position()
            self.is_writing = True
        else:
            self.close()

    def new_letter(self):
        """Affiche une nouvelle lettre du texte"""
        if self.current_letter_id < len(self.current_text[self.current_row]) - 1:
            self.current_letter_id += 1
            self.ecrire(self.current_text[self.current_row][:self.current_letter_id+1], self.text_position)
            pg.mixer.Sound.play(self.tw_sound)
            if self.current_letter_id >= len(self.current_text[self.current_row]) - 1 and self.current_row < len(self.current_text) - 1:
                self.current_letter_id = 0
                self.current_row += 1
                self.refresh_text_position()
        else:
            self.current_letter_id = -1
            self.is_writing = False

    def ecrire(self, texte, pos, color=(0, 0, 0)):
        """Affiche le texte sur le cadre de dialogue"""
        text_affiche = self.font.render(texte, False, color)
        self.talk_box_img.blit(text_affiche, pos)

    def show_talk_box(self):
        """Affichage graphique de la boîte"""
        rect = self.talk_box_img.get_rect(center=(self.game.screen.get_size()[0]/2, self.game.screen.get_size()[1]-self.talk_box_img.get_height()/2))
        self.game.screen.blit(self.talk_box_img, rect)

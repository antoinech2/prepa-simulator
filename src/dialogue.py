#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
Gestion des dialogues entre le joueur et les NPC
"""


import pygame as pg
import sqlite3 as sql
import numpy as np


class Dialogue():
    DATABASE_LOCATION = "res/text/dialogues.db"
    def __init__(self, game, npc):
        self.game = game

        #Graphique
        self.talk_box_surf = pg.image.load(
            "res/textures/talk_box_next.png").convert()
        # FIXME Passage en relatif
        self.talk_box_x = int(self.talk_box_surf.get_width()*0.75)
        self.talk_box_y = int(self.talk_box_surf.get_height()*0.75)
        self.talk_box_img = pg.transform.scale(
            self.talk_box_surf, (self.talk_box_x, self.talk_box_y))
        self.talk_box_img.set_colorkey([255, 255, 255])

        #BDD
        self.db_connexion = sql.connect(self.DATABASE_LOCATION)
        self.db_cursor = self.db_connexion.cursor()

        self.lettre_cooldown = 5
        self.current_npc = npc
        self.current_text = ""  # text actuel
        self.current_text_id = -1  # id du text actuel
        self.current_letter_id = -1  # lettre actuelle

        #Texte
        self.texts = np.array(self.db_cursor.execute("SELECT texte FROM npc_dialogue WHERE id_npc = ? AND id_dialogue = ? ORDER BY ligne_dialogue ASC", (self.current_npc.id, 1)).fetchall())[:,0]
        #Police
        self.font = pg.font.SysFont("comic sans ms", 16)


        self.tw_sound = pg.mixer.Sound(
            "res/sounds/sound_effect/typewriter.wav")
        self.is_writing = True
        self.game.player.is_talking = True
        self.new_line()

    def close(self):
        self.db_cursor.close()
        self.db_connexion.close()
        self.game.player.is_talking = False
        self.game.dialogue = None

    def update(self):  # cette fonction s'execute à chaques ticks
        self.show_talk_box()  # on affiche limage de la boite de dialgue
        if self.is_writing:
            if self.game.tick_count % self.lettre_cooldown == 0:
                self.new_letter()

    def next_dialogue(self):
        if self.is_writing:
            self.is_writing = False
            self.current_letter_id = -1
            self.ecrire(self.current_text,30,100)
        else:
            self.new_line()

    def new_line(self):  # on passe au dialogue suivant
        # on "efface" le dialogue precedent
        self.talk_box_img = pg.transform.scale(
            self.talk_box_surf, (self.talk_box_x, self.talk_box_y))
        self.talk_box_img.set_colorkey([255, 255, 255])
        # dans la suite à chaques appels de cette fonction on ajoute 1 à l'id du dialogue actuel sauf si c'est le dernier
        # si c'est le dernier alors le player ne parle plus
        if self.current_text_id < len(self.texts) - 1:
            self.current_text_id += 1
            self.current_text = self.texts[self.current_text_id]
            self.is_writing = True
        else:
            self.close()

    def new_letter(self):  # cette fonction ecrit une lettre de plus à chaques fois qu'elle est appelée
        # meme principe que dans dial_suiv mais avec des lettres
        if self.current_letter_id < len(self.current_text) - 1:
            self.current_letter_id += 1
            self.ecrire(self.current_text[:self.current_letter_id+1], 30, 100)
            pg.mixer.Sound.play(self.tw_sound)
        else:
            self.current_letter_id = -1
            self.is_writing = False

    def ecrire(self, texte, x, y, color=(0, 0, 0)):  # cette fonction affiche un text
        text_affiche = self.font.render(texte, False, color)
        self.talk_box_img.blit(text_affiche, (x, y))

    def show_talk_box(self):  # cette fonction affiche l'image de la boite de dialgue
        a = self.game.screen.get_size()[0]/2
        b = self.game.screen.get_size()[1]
        c = self.talk_box_img.get_width()/2
        d = self.talk_box_img.get_height()
        self.game.screen.blit(self.talk_box_img, (a-c, b-d))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Gère les NPC du jeu"""

import pygame as pg


class Npc(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.sprite_sheet = pg.image.load('res/textures/player.png')
        self.dialogue = self.game.dialogue
        self.image = pg.Surface([32, 32])  # creation d'une image
        self.image.set_colorkey([0, 0, 0])  # transparence
        self.rect = self.image.get_rect()  # rectangle autour du joueur
        self.rect.topleft = [x, y]  # placement du npc
        self.image.blit(self.sprite_sheet, (0, 0),
                        (0, 0, 32, 32))  # affichage du npc
        self.feet = pg.Rect(0, 0, self.rect.width * 0.5, 12)
        # sql : recuperation des dialogues
        self.dial = []
        for d in self.dialogue.db_cursor.execute("SELECT texte FROM npc_1 WHERE lieu = 'debut'"):
            self.dial.append(d[0])

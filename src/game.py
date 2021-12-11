#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Gère le jeu dans sa globalité, notemment la boucle principale"""

import pygame as pg
import pyscroll
import sqlite3 as sql

import player
import maps
import dialogue
import inputs


class Game:
    def __init__(self):
        # Gestion de l'écran
        self.screen = pg.display.set_mode((800,600)) # taille de la fenêtre
        pg.display.set_caption("Prepa Simulator") # le petit nom du jeu

        self.tick_count = 0
        self.dialogue = dialogue.Dialogue(self)

        self.player = player.Player(0, 0, self)
        self.map_manager = maps.MapManager(self.screen, self.player)

    def tick(self):
        inputs.handle_pressed_key(self)
        self.map_manager.update()
        self.map_manager.draw()
        self.player.update_player()

    def run(self):

        clock = pg.time.Clock()

        running = True

        while running:

            self.tick()
            pg.display.flip()  # update l'ecran

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.KEYDOWN:
                    inputs.handle_key_down_event(self, event)
            self.tick_count += 1
            clock.tick(60)  # 60 fps psk ça va trop vite
        pg.quit()

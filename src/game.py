#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pygame as pg
import pyscroll
import sqlite3 as sql

from player import *
from npc import *
from text import *
from maps import *


class Game:
    def __init__(self):
        # BDD
        self.db_connexion = sql.connect(
            "res/text/dialogues/dial_prepa_simulator.db")
        self.db_cursor = self.db_connexion.cursor()

        # Gestion de l'écran
        self.screen = pg.display.set_mode((800, 600))  # taille de la fenêtre
        pg.display.set_caption("jeu")  # le petit nom du jeu

        # charger la carte
        self.dialogue = Dialogue(self)
        self.map = Map(self, 'res/maps/carte.tmx', [Npc(self,300, 100)])


        # génération d'un joueur
        # TODO: Calcul a faire en init joueur
        player_position = self.map.tmx_data.get_object_by_name("spawn")

        self.player = Player(player_position.x, player_position.y, self)

        self.tick_count = 0

        # dessiner le grp de calques
        self.group = pyscroll.PyscrollGroup(
            map_layer=self.map.map_layer, default_layer=1)
        self.group.add(self.player)  # player à la couche default_layer

        # generation du groupe qui contient les npc
        # generation  d'un npc
        # TODO: Npc chargé par la map
        self.group.add(self.map.group_npc.sprites()[0])
        pg.mixer.music.load('res/sounds/music/proto_musique.mp3')
        # pg.mixer.music.play(-1)

    def CloseGame(self):
        self.db_connexion.commit()
        self.db_cursor.close()
        self.db_connexion.close()

    # TODO: A terme : classe Inputs pour gérer les clic et clavier
    def handle_input(self):  # les flèches du clavier
        pressed = pg.key.get_pressed()
        if not self.player.is_talking:
            # On envoie le statut des 4 touches de déplacement pour être traité
            self.player.move([pressed[pg.K_UP], pressed[pg.K_RIGHT], pressed[pg.K_DOWN], pressed[pg.K_LEFT]], pressed[pg.K_RCTRL] or pressed[pg.K_LCTRL])

    def update(self):
        self.group.update()
        # vérif collision
        # TODO: --> Classe Player
        for sprite in self.group.sprites():
            if sprite.feet.collidelist(self.map.walls) > -1:
                sprite.move_back()

    def run(self):

        clock = pg.time.Clock()

        running = True

        while running:

            self.handle_input()
            self.update()
            self.group.center(self.player.rect)
            self.group.draw(self.screen)
            self.player.update_player()
            pg.display.flip()  # update l'ecran

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.KEYDOWN:
                    # TODO: Classe inputs
                    if event.key == pg.K_SPACE:  # si Espace est pressée
                        self.player.space_pressed()
            self.tick_count += 1
            clock.tick(60)  # 60 fps psk ça va trop vite
        pg.quit()

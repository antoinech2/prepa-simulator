#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Gère le jeu dans sa globalité, notemment la boucle principale"""

import pygame as pg
import pyscroll
import sqlite3 as sql

import player
import npc
import maps
import dialogue
import inputs


class Game:
    def __init__(self):
        # Gestion de l'écran
        self.screen = pg.display.set_mode((800, 600))  # taille de la fenêtre
        pg.display.set_caption("jeu")  # le petit nom du jeu

        # TODO: Les dialogues doivent etres rattachés au NPC, pas au jeu
        self.dialogue = dialogue.Dialogue(self)

        # charger la carte
        self.map = maps.Map(self, 'res/maps/carte.tmx', [npc.Npc(self,300, 100)])


        # génération d'un joueur
        # TODO: Calcul a faire en init joueur
        player_position = self.map.tmx_data.get_object_by_name("spawn")

        self.player = player.Player(player_position.x, player_position.y, self)

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

            inputs.handle_pressed_key(self)
            self.update()
            self.group.center(self.player.rect)
            self.group.draw(self.screen)
            self.player.update_player()
            pg.display.flip()  # update l'ecran

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.KEYDOWN:
                    inputs.handle_key_down_event(self, event)
            self.tick_count += 1
            clock.tick(60)  # 60 fps psk ça va trop vite
        pg.quit()

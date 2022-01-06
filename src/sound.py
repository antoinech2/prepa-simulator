#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame as pg

class SoundManager():
    """Gestionnaire des sons"""
    VOLUME = 0.1 #Volume général du son
    SOUNDS_FOLDER = "res/sounds/"

    def __init__(self, map):
        self.map = map
        self.channel1 = pg.mixer.Channel(1)
        self.music_file = self.map.game.game_data_db.execute("select music from maps where id = ?;", (self.map.map_id,)).fetchall()[0][0]
        
        self.play_music(self.music_file)

    def play_music(self, music_file):
        """Joue une nouvelle musique"""
        pg.mixer.music.load(f"{self.SOUNDS_FOLDER}music/{music_file}.mp3")
        pg.mixer.music.set_volume(self.VOLUME)
        pg.mixer.music.play(-1) # Boucle la musique
    
    def play_sfx(self, sfx_file, channel = 1):
        """Joue un effet sonore"""
        sfx = pg.mixer.Sound(f"{self.SOUNDS_FOLDER}fx/{sfx_file}.mp3")
        self.channel1.set_volume(self.VOLUME)
        self.channel1.play(sfx)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame as pg

class SoundManager():
    """Gestionnaire des sons"""
    VOLUME = 0.2 #Volume général du son
    SOUNDS_FOLDER = "res/sounds/"

    def __init__(self, map, old_bgm):
        self.old_bgm = old_bgm
        self.map = map
        self.channel1 = pg.mixer.Channel(1)
        self.music_file = self.map.game.game_data_db.execute("select music from maps where id = ?;", (self.map.map_id,)).fetchall()[0][0]
        self.current_music = self.music_file

        self.play_music(self.music_file, self.old_bgm)

    def play_music(self, music_file, old_bgm):
        """Joue une nouvelle musique"""
        if music_file == -1:
            pg.mixer.music.load(f"{self.SOUNDS_FOLDER}music/{self.music_file}.mp3")
            pg.mixer.music.set_volume(self.VOLUME)
            pg.mixer.music.play(-1)
        elif old_bgm is None or old_bgm != self.music_file:     # Même bande sonore ou première map chargée pendant la session
            pg.mixer.music.load(f"{self.SOUNDS_FOLDER}music/{music_file}.mp3")
            pg.mixer.music.set_volume(self.VOLUME)
            pg.mixer.music.play(-1) # Boucle la musique
    
    def play_sfx(self, sfx_file, channel = 1):
        """Joue un effet sonore"""
        sfx = pg.mixer.Sound(f"{self.SOUNDS_FOLDER}fx/{sfx_file}.mp3")
        self.channel1.set_volume(self.VOLUME)
        self.channel1.play(sfx)

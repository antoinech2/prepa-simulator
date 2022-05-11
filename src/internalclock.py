"""Gère l'horloge interne"""

import pygame as pg
import locale
import save

class InternalClock:
    TICKS_PER_MIN = 100
    MINUTES_PER_TURN = 10             # Nombre de minutes qui passent à chaque tour, < 120

    def __init__(self, game):
        self.game = game
        self.pgclock = pg.time.Clock()

        # Compteurs de ticks
        self.ticks_since_epoch = save.load_config("player")['ticks']
        self.ticks_since_sessionstart = 0

        # Horloge du jeu
        # TODO Sauvegarder l'heure courante
        self.weekday = 0
        self.find_dayname()
        self.hour = 8
        self.minute = 0
    
    def find_dayname(self):
        """Récupère le nom du jour courant depuis le fichier locale"""
        self.dayname = [locale.getstring_system(day) for day in ["day_0", "day_1", "day_2", "day_3", "day_4", "day_5", "day_6"]][self.weekday]

    def update(self):
        self.ticks_since_epoch += 1
        self.ticks_since_sessionstart += 1
        
        # Actualisation de l'heure
        if self.ticks_since_epoch % self.TICKS_PER_MIN == 0:
            self.minute += self.MINUTES_PER_TURN
            if self.minute >= 60:
                self.hour += self.minute // 60
                self.minute = self.minute % 60
            if self.hour >= 24:
                self.weekday += 1
                self.hour = 0
                if self.weekday >= 7:
                    self.weekday = 0
                self.find_dayname()
    
    def save(self):
        """Sauvegarde des ticks et de la date courante"""
        # TODO Sauvegarder la date courante
        save.save_config("player", ticks = self.ticks_since_epoch)
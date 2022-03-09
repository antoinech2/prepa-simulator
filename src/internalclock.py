"""Gère l'horloge interne"""

import pygame as pg

class InternalClock:
    TICKS_PER_MIN = 60
    MINUTES_PER_TURN = 2             # Nombre de minutes qui passent à chaque tour, < 120

    def __init__(self, game):
        self.game = game
        self.pgclock = pg.time.Clock()

        # Compteurs de ticks
        self.ticks_since_epoch = 0      # TODO Trouver un moyen d'enregistrer le nb de ticks depuis le dernier reset
        self.ticks_since_sessionstart = 0

        # Horloge du jeu
        # TODO Sauvegarder l'heure courante
        self.weekday = 0
        self.hour = 8
        self.minute = 0
    
    def get_time(self):
        return([self.weekday, self.hour, self.minute])
    
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
            if self.weekday >= 6:
                self.weekday = 0

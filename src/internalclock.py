"""Gère l'horloge interne"""

import pygame as pg
import locale
import save

class InternalClock:
    GAME_TICK = 10                   # Nombre de ticks internes par tick de jeu (recalcul des scripts, etc.)
    TIME_TICK = 180                  # Nombre de ticks internes par incrémentation du temps.
    MINUTES_PER_TURN = 1             # Nombre de minutes qui passent à chaque tour, < 120. #! Réglage par défaut : 1

    def __init__(self, game):
        self.game = game
        self.pgclock = pg.time.Clock()

        # Compteurs de ticks
        self.ticks_since_epoch = save.load_config("internals")['ticks']
        self.ticks_since_sessionstart = 0
        self.ticks_since_timechange = 0
        self.ticks_since_last_gametick = 0

        # Horloge du jeu
        self.weekday = save.load_config("internals")["day"]
        self.find_dayname()
        self.hour = save.load_config("internals")["hour"]
        self.minute = save.load_config("internals")["minute"]
    
    def find_dayname(self):
        """Récupère le nom du jour courant depuis le fichier locale"""
        self.dayname = [locale.get_substring("system", day) for day in ["day_0", "day_1", "day_2", "day_3", "day_4", "day_5", "day_6"]][self.weekday]

    def update(self):
        if not self.game.menu_manager.sidemenu.onscreen:        # Pas d'update lorsque le menu latéral est ouvert
            self.ticks_since_epoch += 1
            self.ticks_since_sessionstart += 1
            if self.game.dialogue is None:
                self.ticks_since_timechange += 1
                self.ticks_since_last_gametick += 1
            
            # Actualisation de l'heure si le joueur ne parle pas

            if self.ticks_since_last_gametick >= self.GAME_TICK and not self.game.script_manager.perblock:
                self.ticks_since_last_gametick = 0
                if self.game.player.is_sprinting:
                    self.game.player.stamina -= 1
                for script in self.game.script_manager.permanent_scripts:
                    self.game.script_manager.execute_script(script, "back")
            
            if self.ticks_since_timechange >= self.TIME_TICK and not self.game.script_manager.perblock:
                self.ticks_since_timechange = 0
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
                self.game.player.stamina = self.game.player.stamina + 2 if self.game.player.stamina + 2 < self.game.player.MAX_ENERGY else self.game.player.MAX_ENERGY
    
    def save(self):
        """Sauvegarde des ticks et de la date courante"""
        # TODO Implémenter les saisons
        save.save_config("internals", ticks = self.ticks_since_epoch, day = self.weekday, hour = self.hour, minute = self.minute)
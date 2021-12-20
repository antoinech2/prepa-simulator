#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Programme principal pour exécuter le jeu"""

# Import externe
import pygame as pg
import os

# Import interne
import game as g

if __name__ == '__main__' :
    # Modification du répertoire de base pour tout le jeu hors des fichiers sources
    os.chdir("..")
    pg.init()
    # Démarrage du jeu
    game = g.Game()
    game.run()
    # Redémarrage du jeu en cas de redimension de la fenêtre
    while game.restart:
        pg.init()
        game = g.Game()
        game.run()

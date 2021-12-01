#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Programme principal pour exécuter le jeu"""

import pygame as pg
import os

import game

if __name__ == '__main__' :
    os.chdir("..")
    pg.init()
    game = game.Game()
    game.run()
    game.CloseGame()

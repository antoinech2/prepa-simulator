#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Programme principal pour exécuter le jeu"""

import pygame as pg
import os

from game import *

if __name__ == '__main__' :
    os.chdir("..")
    pg.init()
    game = Game()
    game.run()
    game.CloseGame()

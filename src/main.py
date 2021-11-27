import pygame as pg
import os

from game import *

if __name__ == '__main__' :
    os.chdir("..")
    pg.init()
    game = Game()
    game.run()
    while game.restart:
        game = Game()
        game.run()

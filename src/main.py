import pygame
import os

from game import *

if __name__ == '__main__' :
    os.chdir("..")
    pygame.init()
    game = Game()
    game.run()

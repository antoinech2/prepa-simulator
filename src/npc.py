import pygame as pg

class Npc(pg.sprite.Sprite):
    def __init__(self, num):
        self.sprite = pg.image.load(sprite)
        with open(f'../res/text/dialogues/pnj{num}.txt','r') as a:
            self.dial = a.readline().strip().split("__")
            print(self.dial)

a = Pnj('../res/textures/player.png', 1)

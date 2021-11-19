import pygame as p

class Pnj:
    def __init__(self,sprite,num):
        self.sprite = p.image.load(sprite)
        with open(f'../res/text/dialogues/pnj{num}.txt','r') as a:
            self.dial = a.readline().strip().split("__")
            print(self.dial)

a = Pnj('../res/textures/player.png',1)

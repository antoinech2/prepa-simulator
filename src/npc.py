import pygame as pg
import sqlite3 as sql

class Npc(pg.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.sprite_sheet = pg.image.load('res/textures/player.png')
        self.image = pg.Surface([32,32]) #creation d'une image
        self.image.set_colorkey([0,0,0]) #transparence
        self.rect = self.image.get_rect() #rectangle autour du joueur
        self.rect.topleft = [x,y] #placement du npc
        self.image.blit(self.sprite_sheet,(0,0),(0,0,32,32)) #affichage du npc
        self.feet = pg.Rect(0,0, self.rect.width * 0.5 , 12) # by djessy , c'est necessaire pour la commande update

        #sql : recuperation des dialogues
        self.connection = sql.connect("res/text/dialogues/dial_prepa_simulator.db")
        self.crs = self.connection.cursor()
        self.crs.execute("SELECT texte FROM npc_1 WHERE lieu = 'debut'")
        self.dial = []
        for d in self.crs:
            self.dial.append(d[0])

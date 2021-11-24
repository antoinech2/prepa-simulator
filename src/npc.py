import pygame as pg

class Npc(pg.sprite.Sprite):
    def __init__(self,x,y,game):
        super().__init__()
        self.sprite_sheet = pg.image.load('res/textures/player.png')
        self.game = game
        self.dialogue = game.dialogue
        self.image = pg.Surface([32,32]) #creation d'une image
        self.image.set_colorkey([0,0,0]) #transparence
        self.rect = self.image.get_rect() #rectangle autour du joueur
        self.rect.topleft = [x,y] #placement du npc
        self.image.blit(self.sprite_sheet,(0,0),(0,0,32,32)) #affichage du npc
        self.feet = pg.Rect(0,0, self.rect.width * 0.5 , 12) # by djessy , c'est necessaire pour la commande update
        self.dialogue.crs.execute("SELECT texte FROM npc_1 WHERE lieu = 'debut'")
        #sql : recuperation des dialogues
        self.dial = []
        for d in self.dialogue.crs:
            self.dial.append(d[0])

        

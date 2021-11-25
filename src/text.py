import pygame as pg
import sqlite3 as sql





class Dialogue():
    def __init__(self, game):
        talk_box_surf = pg.image.load("res/textures/talk_box_next.png").convert()
        talk_box_x = int(talk_box_surf.get_width()*1.5)  # FIXME C'est degueulasse d'utiliser int()
        talk_box_y = int(talk_box_surf.get_height()*1.5)
        self.talk_box_img = pg.transform.scale(talk_box_surf,(talk_box_x,talk_box_y))
        self.game = game
        self.connection = sql.connect("res/text/dialogues/dial_prepa_simulator.db")
        self.crs = self.connection.cursor()
        self.font = pg.font.SysFont("monospace",16)


    def show_talk_box(self, x, y):
        self.game.screen.blit(self.talk_box_img, (x, y))


    def ecrire(self,texte,color = (255,0,0)):
        text_affiche = self.font.render("text",True,color)
        self.talk_box_img.blit(text_affiche,(50,50))

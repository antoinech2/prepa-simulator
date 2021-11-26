import pygame as pg
import sqlite3 as sql





class Dialogue():
    def __init__(self, game):
        talk_box_surf = pg.image.load("res/textures/talk_box_next.png").convert()
        talk_box_x = int(talk_box_surf.get_width()*0.75) # FIXME C'est degueulasse d'utiliser int()
        talk_box_y = int(talk_box_surf.get_height()*0.75)
        self.current_text = ""
        self.current_text_id = 0
        self.current_npc = None
        self.talk_box_img = pg.transform.scale(talk_box_surf,(talk_box_x,talk_box_y))
        self.talk_box_img.set_colorkey([255,255,255])
        self.game = game
        self.connection = sql.connect("res/text/dialogues/dial_prepa_simulator.db")
        self.crs = self.connection.cursor()
        self.font = pg.font.SysFont("comic sans ms",16)

    def update_dialogue(self):
        if self.game.player.is_talking:
            self.show_talk_box()

    def show_talk_box(self):
        a = self.game.screen.get_size()[0]/2
        b = self.game.screen.get_size()[1]
        c = self.talk_box_img.get_width()/2
        d = self.talk_box_img.get_height()
        self.game.screen.blit(self.talk_box_img,(a-c,b-d))


    def dial_suiv(self):
        pg.draw.rect(self.talk_box_img,(195,195,195),(15,100,400,75))
        if self.current_text_id < len(self.current_npc.dial) - 1:
            self.current_text_id += 1
            self.current_text = self.current_npc.dial[self.current_text_id]
            self.ecrire(self.current_text)
        else:
            self.current_text_id = 0
            self.game.player.is_talking = False


    def init_dial(self,target_npc):
        self.current_npc = target_npc
        self.show_talk_box()
        self.ecrire(self.current_npc.dial[self.current_text_id])


    def ecrire(self,texte,color = (0,0,0)):
        text_affiche = self.font.render(texte,False,color)
        self.talk_box_img.blit(text_affiche,(30,100))

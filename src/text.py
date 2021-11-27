import pygame as pg
import sqlite3 as sql





class Dialogue():
    def __init__(self, game):
        talk_box_surf = pg.image.load("res/textures/talk_box_next.png").convert()
        talk_box_x = int(talk_box_surf.get_width()*0.75) # FIXME C'est degueulasse d'utiliser int()
        talk_box_y = int(talk_box_surf.get_height()*0.75)
        self.current_text = ""
        self.current_text_id = -1
        self.current_letter_id = -1
        self.current_letter = ""
        self.current_npc = None
        self.talk_box_img = pg.transform.scale(talk_box_surf,(talk_box_x,talk_box_y))
        self.talk_box_img.set_colorkey([255,255,255])
        self.game = game
        self.connection = sql.connect("res/text/dialogues/dial_prepa_simulator.db")
        self.crs = self.connection.cursor()
        self.font = pg.font.SysFont("comic sans ms",16)
        self.tw_sound = pg.mixer.Sound("res/sounds/sound_effect/typewriter.wav")
        self.internal_clock = 0
        self.is_writing = False
        self.frequence = 0

    def update_dialogue(self):
        if self.game.player.is_talking:
            self.show_talk_box()
            if self.is_writing:
                self.sequencer()
        self.internal_clock = (self.internal_clock + 1)%60


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
            self.type_writer()
        else:
            self.current_text_id = -1
            self.game.player.is_talking = False


    def init_dial(self,target_npc):
        self.current_npc = target_npc
        self.dial_suiv()


    def type_writer(self,f = 20):
        self.is_writing = True
        self.frequence = f

    def tp_writer(self):
        if self.current_letter_id < len(self.current_text) - 1:
            self.current_letter_id += 1
            self.ecrire(self.current_text[:self.current_letter_id+1],30,100)
            pg.mixer.Sound.play(self.tw_sound)
        else:
            self.current_letter_id = -1
            self.is_writing = False


    def sequencer(self):
        if self.internal_clock % int(60/self.frequence) == 0:
            self.tp_writer()


    def ecrire(self,texte,x,y,color = (0,0,0)):
        text_affiche = self.font.render(texte,False,color)
        self.talk_box_img.blit(text_affiche,(x,y))

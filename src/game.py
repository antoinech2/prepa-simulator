import pygame as pg
import pyscroll
import sqlite3 as sql

from player import *
from npc import *
from text import *
from maps import *


class Game:
    def __init__(self):
        # Gestion de l'écran
        self.screen = pg.display.set_mode((800,600)) # taille de la fenêtre
        pg.display.set_caption("Prepa Simulator") # le petit nom du jeu

        self.tick_count = 0
        self.dialogue = Dialogue(self)

        # génération d'un joueur
        # TODO: Calcul a faire en init joueur
        #player_position = self.map.tmx_data.get_object_by_name("spawn")

        self.player = Player(0, 0, self)
        self.map_manager = MapManager(self.screen, self.player)

        #generation du groupe qui contient les npc
        #self.group_npc = pg.sprite.Group()
        #generation  d'un npc
        # TODO: Npc chargé par la map
        #npc_1 = Npc(self, 300,100)
        #self.group.add(npc_1)
        #self.group_npc.add(npc_1)
        #pg.mixer.music.load('res/sounds/music/proto_musique.mp3')
        #pg.mixer.music.play(-1)

    def CloseGame(self):
        self.db_connexion.commit()
        self.db_cursor.close()
        self.db_connexion.close()

    # TODO: A terme : classe Inputs pour gérer les clic et clavier
    def handle_input(self): # les flèches du clavier
        pressed = pg.key.get_pressed()
        if not self.player.is_talking:
            if pressed[pg.K_UP]:
                self.player.move_up() # voir player
                self.player.change_animation('up') #voir player
            elif pressed[pg.K_DOWN]:
                self.player.move_down()
                self.player.change_animation('down')
            elif pressed[pg.K_LEFT]:
                self.player.move_left()
                self.player.change_animation('left')
            elif pressed[pg.K_RIGHT]:
                self.player.move_right()
                self.player.change_animation('right')
            else :
                self.player.is_animated = False

    def update(self):
        self.map_manager.update()

    def run(self):

        clock = pg.time.Clock()

        running = True

        while running:

            self.handle_input()
            self.update()
            self.map_manager.draw()
            self.player.update_player()
            pg.display.flip() #update l'ecran


            for event in pg.event.get():
                if event.type == pg.QUIT :
                    running = False
                elif event.type == pg.KEYDOWN:
                    ## TODO: Classe inputs
                    if event.key == pg.K_SPACE: #si Espace est pressée
                        self.player.space_pressed()
            clock.tick(60) #60 fps psk ça va trop vite
        pg.quit()

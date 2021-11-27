import pygame as pg
import pytmx
import pyscroll
import sqlite3 as sql
import yaml
import os

from player import *
from npc import *
from text import *


class Game:
    CONFIGURATION_FILE_LOCATION = "sav/window.yaml"
    DEFAULT_WINDOW_SIZE = (1000, 600) # FIXME: Passer en variable locale, trouver comment faire

    def __init__(self):

        self.restart = True
        self.resizable = False
        self.is_running = False

        # BDD
        self.db_connexion = sql.connect("res/text/dialogues/dial_prepa_simulator.db")
        self.db_cursor = self.db_connexion.cursor()

        #Taille de l'écran
        if not os.path.isdir("sav"):
            os.makedirs("sav")

        if os.path.isfile(self.CONFIGURATION_FILE_LOCATION):
            window_config = yaml.safe_load(open(self.CONFIGURATION_FILE_LOCATION, 'r'))
            self.window_size = (window_config.get("size").get("width"), window_config.get("size").get("height"))
        else:
            self.window_size = self.DEFAULT_WINDOW_SIZE
            open(self.CONFIGURATION_FILE_LOCATION, 'w').close()
            self.change_window_size(self.DEFAULT_WINDOW_SIZE[1], self.DEFAULT_WINDOW_SIZE[0])

        # Gestion de l'écran
        self.screen = pg.display.set_mode(self.window_size, pg.RESIZABLE) # taille de la fenêtre
        pg.display.set_caption("jeu") # le petit nom du jeu

        # charger la carte
        ## TODO: Passer avec une classe Map
        tmx_data = pytmx.util_pygame.load_pygame('res/maps/carte.tmx' )
        map_data = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data,self.screen.get_size())
        map_layer.zoom = 2

        self.dialogue = Dialogue(self)

        #génération d'un joueur
        # TODO: Calcul a faire en init joueur
        player_position = tmx_data.get_object_by_name("spawn")

        self.player = Player(player_position.x,player_position.y,self)

        #affectation des murs de collision
        # TODO: --> Classe Map
        self.walls = []
        for obj in tmx_data.objects :
            if obj.type == "mur" :
                self.walls.append(pg.Rect(obj.x , obj.y , obj.width , obj.height ))


        # dessiner le grp de calques
        self.group = pyscroll.PyscrollGroup(map_layer = map_layer , default_layer = 1)
        self.group.add(self.player) #player à la couche default_layer

        #generation du groupe qui contient les npc
        self.group_npc = pg.sprite.Group()
        #generation  d'un npc
        # TODO: Npc chargé par la map
        npc_1 = Npc(self, 300,100)
        self.group.add(npc_1)
        self.group_npc.add(npc_1)
        pg.mixer.music.load('res/sounds/music/proto_musique.mp3')
        #pg.mixer.music.play(-1)

    def quit_game(self):
        self.is_running = False

    def close_database(self):
        self.db_connexion.commit()
        self.db_cursor.close()
        self.db_connexion.close()

    def change_window_size(self, height, width):
        if self.resizable:
            new_window_config = {"size" : {"width" : width, "height" : height}}
            with open(self.CONFIGURATION_FILE_LOCATION, 'w') as file:
                yaml.dump(new_window_config, file)
            self.quit_game()
            self.restart = True
        else:
            self.resizable = True

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
        self.group.update()
        #vérif collision
        # TODO: --> Classe Player
        for sprite in self.group.sprites():
            if sprite.feet.collidelist(self.walls) > -1:
                sprite.move_back()


    def run(self):
        self.restart = False
        clock = pg.time.Clock()

        self.is_running = True

        while self.is_running:

            self.handle_input()
            self.update()
            self.group.center(self.player.rect)
            self.group.draw(self.screen)
            self.player.update_player()
            pg.display.flip() #update l'ecran


            for event in pg.event.get():
                if event.type == pg.QUIT :
                    self.is_running = False
                elif event.type == pg.KEYDOWN:
                    ## TODO: Classe inputs
                    if event.key == pg.K_SPACE: #si Espace est pressée
                        self.player.space_pressed()
                elif event.type == pg.VIDEORESIZE:
                    self.change_window_size(event.h, event.w)
            clock.tick(60) #60 fps psk ça va trop vite
        self.close_database()

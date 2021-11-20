import pygame as pg
import pytmx
import pyscroll
from player import Player
from npc import Npc

class Game :
    def __init__(self):
        self.screen = pg.display.set_mode((800,600)) # taille de la fenêtre
        pg.display.set_caption("jeu") # le petit nom du jeu

        # charger la carte
        tmx_data = pytmx.util_pygame.load_pygame('res/carte.tmx' )
        map_data = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data,self.screen.get_size())
        map_layer.zoom = 2

        #génération d'un joueur
        player_position = tmx_data.get_object_by_name("spawn")
        self.player = Player(player_position.x,player_position.y)


        # dessiner le grp de calques
        self.group = pyscroll.PyscrollGroup(map_layer = map_layer , default_layer = 1)
        self.group.add(self.player) #player à la couche default_layer

        #generation  d'un npc
        self.group.add(Npc(300,130))

        pg.mixer.music.load('res/sounds/music/proto_musique.mp3')
        #pg.mixer.music.play(-1)


    def handle_input(self): # les flèches du clavier
        pressed = pg.key.get_pressed()
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




    def run(self):

        clock = pg.time.Clock()

        running = True

        while running:

            self.handle_input()
            self.group.update()
            self.group.center(self.player.rect)
            self.group.draw(self.screen)
            pg.display.flip()

            for event in pg.event.get():
                if event.type == pg.QUIT :
                    running = False
            clock.tick(60) #60 fps psk ça va trop vite
        pg.quit()

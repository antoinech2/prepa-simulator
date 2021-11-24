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

        self.player = Player(player_position.x,player_position.y,self)

        #affectation des murs de collision
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
        npc_1 = Npc(300,100)
        self.group.add(npc_1)
        self.group_npc.add(npc_1)

        a = pg.image.load("res/textures/talk_box_next.png")
        self.talk_box_img = pg.transform.scale(a,(int(a.get_width()*1.5),int(a.get_height()*1.5)))

        pg.mixer.music.load('res/sounds/music/proto_musique.mp3')
        #pg.mixer.music.play(-1)


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
        for sprite in self.group.sprites():
            if sprite.feet.collidelist(self.walls) > -1:
                sprite.move_back()


    def run(self):

        clock = pg.time.Clock()

        running = True

        while running:

            self.handle_input()
            self.update()
            self.group.center(self.player.rect)
            self.group.draw(self.screen)
            self.player.update_player()
            pg.display.flip() #update l'ecran


            for event in pg.event.get():
                if event.type == pg.QUIT :
                    running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE: #si Espace est pressée
                        self.player.space_pressed()
            clock.tick(60) #60 fps psk ça va trop vite
        pg.quit()

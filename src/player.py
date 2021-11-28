import pygame as pg
from text import *

class Player(pg.sprite.Sprite):
    def __init__(self, x, y, game):
        super().__init__()
        self.game = game
        self.dialogue = game.dialogue
        self.is_animated = False
        self.is_talking = False
        self.sprite_sheet = pg.image.load('res/textures/player.png')
        self.image = self.get_image(0,0) # en bas par défaut
        self.image.set_colorkey([0,0,0]) # transparence
        self.rect = self.image.get_rect() # rectangle autour du joueur
        self.position = [x,y]
        self.feet = pg.Rect(0,0, self.rect.width * 0.5 , 12)
        self.old_position = self.position.copy()
        self.images = {
            'down' : [ self.get_image(0,0), self.get_image(32,0) , self.get_image(64,0)],
            'left' : [self.get_image(0,32),self.get_image(32,32),self.get_image(64,32)],
            'right' : [self.get_image(0,64),self.get_image(32,64),self.get_image(64,64)],
            'up' : [self.get_image(0,96),self.get_image(32,96),self.get_image(64,96)]
        }
        self.walk_speed = 1.5
        self.animation_speed = 0.2
        self.current_sprite = 0
    def change_animation(self,sens): #change l'image en fonction du sens 'sens'
            self.is_animated = True
            self.image = self.images[sens][ int(self.current_sprite)]
            self.image.set_colorkey([0,0,0]) #transparence

    def move_right(self):
        self.position[0] += self.walk_speed

    def move_left(self):
        self.position[0] -= self.walk_speed

    def move_down(self):
        self.position[1] += self.walk_speed

    def move_up(self):
        self.position[1] -= self.walk_speed

    def update(self) : #mettre à jour la position
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom
        if self.is_animated == True :
            self.current_sprite += self.animation_speed
            if self.current_sprite >= 3:
                self.current_sprite = 0

    def get_image(self,x,y): # retourne un 'bout' de l'image 'player.png' en fonction de ses coordonées x,y
        image = pg.Surface([32,32])
        image.blit(self.sprite_sheet,(0,0),(x,y,32,32))
        return image

    def save_location(self):
        self.old_position = self.position.copy()

    def update_player(self): # est appelée à chaque tick
        self.save_location()
        self.dialogue.update_dialogue()


    def move_back(self):
        self.position = self.old_position
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom

    def space_pressed(self):# quand espace est pressé
        if self.is_talking:
            self.dialogue.dial_suiv()
        else:
            self.can_talk()


    def can_talk(self):
        if pg.sprite.spritecollide(self,self.game.group_npc,False): # si il est en collision avec un mec du groupe "group_target"
            self.is_talking = True
            self.dialogue.init_dial(pg.sprite.Group.sprites(self.game.group_npc)[0])

    def talk_npc(self):
        if self.is_talking:
            self.dialogue.dial_suiv()

import pygame as pg

class Player(pg.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.is_animated = False
        self.is_talking = False
        self.sprite_sheet = pg.image.load('res/textures/player.png')
        self.image = self.get_image(0,0) # en bas par défaut
        self.image.set_colorkey([0,0,0]) # transparence
        self.rect = self.image.get_rect() # rectangle autour du joueur
        self.position = [x,y]
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
        if self.is_animated == True :
            self.current_sprite += self.animation_speed
            if self.current_sprite >= 3:
                self.current_sprite = 0

    def get_image(self,x,y): # retourne un 'bout' de l'image 'player.png' en fonction de ses coordonées x,y
        image = pg.Surface([32,32])
        image.blit(self.sprite_sheet,(0,0),(x,y,32,32))
        return image

    def can_talk(self,group_target):
        if pg.sprite.spritecollide(self,group_target,False): # si il est en collision avec un mec du groupe "group_target"
            #lancer script dialogue
            pass

import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.sprite_sheet = pygame.image.load('jeu video\player.png') 
        self.image = self.get_image(0,0) # en bas par défaut 
        self.image.set_colorkey([0,0,0]) # transparence
        self.rect = self.image.get_rect() # rectangle autour du joueur 
        self.position = [x,y]
        self.images = {  
            'down' : self.get_image(0,0),
            'left' : self.get_image(0,32),
            'right' : self.get_image(0,64),
            'up' : self.get_image(0,96)
        }
        self.speed = 1.5

    def change_animation(self,sens): #change l'image en fonction du sens 'sens'
        self.image = self.images[sens]
        self.image.set_colorkey([0,0,0]) #transparence

    def move_right(self): 
        self.position[0] += self.speed

    def move_left(self): 
        self.position[0] -= self.speed

    def move_down(self): 
        self.position[1] += self.speed

    def move_up(self): 
        self.position[1] -= self.speed

    def update(self) : #mettre à jour la position 
        self.rect.topleft = self.position

    def get_image(self,x,y): # retourne un 'bout' de l'image 'player.png' en fonction de ses coordonées x,y 
        image = pygame.Surface([32,32])
        image.blit(self.sprite_sheet,(0,0),(x,y,32,32))
        return image

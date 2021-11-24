import pygame as pg


class Dialogue():
    def __init__(self, game):
        talk_box_surf = pg.image.load("res/textures/talk_box_next.png")
        talk_box_x = int(talk_box_surf.get_width()*1.5)  # FIXME C'est degueulasse d'utiliser int()
        talk_box_y = int(talk_box_surf.get_height()*1.5)
        self.talk_box_img = pg.transform.scale(talk_box_surf,(talk_box_x,talk_box_y))
        self.game = game

    def show_talk_box(self, x, y):
        self.game.screen.blit(self.talk_box_img, (x, y))

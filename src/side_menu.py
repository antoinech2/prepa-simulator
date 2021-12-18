#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame as pg

class SideMenu():
    SIDEMENU_POSITION = [500,50]
    TEXTURE_LOCATION = "res/textures/menu/sidemenu.png"

    def __init__(self, game, submenus):
        self.submenus = submenus    # Liste des menus secondaires
        self.submenu_no = 0     # Submenu en cours de sélection
        self.game = game

        # Texture du menu latéral
        self.texture_surf = pg.image.load(self.TEXTURE_LOCATION).convert()
        self.tex_x = int(self.texture_surf.get_width()*0.75)
        self.tex_y = int(self.texture_surf.get_height()*0.75)
        self.texture = pg.transform.scale(self.texture_surf, (self.tex_x, self.tex_y))
        self.texture.set_colorkey([255, 255, 255])

    def show_sidemenu(self):
        """Affichage du menu latéral"""
        rect = self.texture.get_rect(center=(self.game.screen.get_size()[0]/2, self.game.screen.get_size()[1]-self.talk_box_img.get_height()/2))
        self.game.screen.blit(self.texture, rect)
        
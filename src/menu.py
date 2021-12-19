#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame as pg
import pyscroll

class SideMenu():
    SIDEMENU_POSITION = (30, 100)
    TEXTURE_LOCATION = "res/textures/menu/sidemenu.png"
    SIDEMENU_OFFSET = (20, 20) # Temporaire, à passer en relatif

    def __init__(self, game):
        self.submenu_no = 0     # Submenu en cours de sélection
        self.game = game
        self.onscreen = False

        # Texture du menu latéral
        self.texture_surf = pg.image.load(self.TEXTURE_LOCATION).convert()
        self.tex_x = int(self.texture_surf.get_width()*0.75)
        self.tex_y = int(self.texture_surf.get_height()*0.75)
        self.texture = pg.transform.scale(self.texture_surf, (self.tex_x, self.tex_y))
        self.texture.set_colorkey([255, 255, 255])


    def show_sidemenu(self):
        """Affichage du menu latéral"""
        rect = self.texture.get_rect(topright=(self.game.screen.get_size()[0] - self.SIDEMENU_OFFSET[0], self.SIDEMENU_OFFSET[1]))
        self.game.screen.blit(self.texture, rect)


class MenuManager():
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        
        # Menu latéral
        self.sidemenu = SideMenu(self.game)
        
        # Menus secondaires
        pass

    def toggle_sidemenu(self):
        """Commute l'affichage du menu latéral"""
        if not self.game.player.is_talking:
            self.sidemenu.onscreen = not self.sidemenu.onscreen
            self.game.player.can_move = not self.game.player.can_move

    def draw(self):
        """Affiche le menu latéral s'il est ouvert"""
        if self.sidemenu.onscreen:
            self.sidemenu.show_sidemenu()
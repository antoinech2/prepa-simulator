#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame as pg
import pyscroll


# TODO Uniformisation des dialogues sous le module menu
class Font():
    pg.font.init()
    """Classe de la police d'écriture"""
    def __init__(self, font_name):
        self.font_name = font_name
        self.font_size = 16
        self.font = pg.font.SysFont(self.font_name, self.font_size)
        self.font_width = max([metric[1] for metric in self.font.metrics("azertyuiopqsdfghjklmwxcvbnAZERTYUIOPQSDFGHJKLMWXCVBN")]) # Chasse maximale pour la police choisie


class SideMenu():
    """Classe du menu latéral"""
    SIDEMENU_POSITION = (30, 100)
    TEXTURE_LOCATION = "res/textures/menu/sidemenu.png"
    SIDEMENU_OFFSET = (20, 20) # Temporaire, à passer en relatif
    ARROW_TEX = "res/textures/menu/arrow.png"

    def __init__(self, game):
        self.submenu_list = []
        self.game = game
        self.onscreen = False

        # Texture du menu latéral
        self.texture_surf = pg.image.load(self.TEXTURE_LOCATION).convert()
        self.tex_x = int(self.texture_surf.get_width()*0.75)
        self.tex_y = int(self.texture_surf.get_height()*0.75)
        self.texture = pg.transform.scale(self.texture_surf, (self.tex_x, self.tex_y))
        self.texture.set_colorkey([255, 255, 255])

        # Flèche
        self.arrow_pos = 0 # Submenu en cours de sélection
        # Texture de la flèche
        self.arrow_tex_surf = pg.image.load(self.ARROW_TEX).convert()
        self.arrow_tex_x = int(self.arrow_tex_surf.get_width()*0.75)
        self.arrow_tex_y = int(self.arrow_tex_surf.get_height()*0.75)
        self.arrow_tex = pg.transform.scale(self.arrow_tex_surf, (self.arrow_tex_x, self.arrow_tex_y))
        self.arrow_tex.set_colorkey([255, 255, 255])


    def show_sidemenu(self):
        """Affichage du menu latéral"""
        rect = self.texture.get_rect(topright=(self.game.screen.get_size()[0] - self.SIDEMENU_OFFSET[0], self.SIDEMENU_OFFSET[1]))
        self.game.screen.blit(self.texture, rect)

    def show_arrow(self):
        """Affichage de la flèche"""
        rect = self.arrow_tex.get_rect(topright = self.submenu_list[self.arrow_pos].icon_position)
        self.texture.blit(self.arrow_tex, rect)
    
    def menu_move_down(self):
        """Utilisation de la touche ↓"""
        # TODO Changements lorsqu'une fenêtre est ouverte
        if self.arrow_pos < len(self.submenu_list) - 1:
            self.arrow_pos += 1
    
    def menu_move_up(self):
        """Utilisation de la touche ↑"""
        if self.arrow_pos >= 1:
            self.arrow_pos -= 1
    
    def clear(self):
        """Suppression du contenu du menu latéral"""
        self.texture = pg.transform.scale(self.texture_surf, (self.tex_x, self.tex_y))
        self.texture.set_colorkey([255, 255, 255])


class SubMenu():
    """Classe des menus secondaires"""
    SUBMENU_ICON_PATH = "res/textures/menu/submenu/"
    ICON_TEXT_SPACING = (30, 6) # Temporaire
    def __init__(self, name, ingame_name, sidemenu, iconpos):
        self.name = name
        self.ingame_name = ingame_name
        self.sidemenu = sidemenu
        self.sidemenu.submenu_list.append(self)
        self.icon_path = f"{self.SUBMENU_ICON_PATH}{self.name}.png"
        self.icon_position = iconpos
        self.is_open = False

        # Graphiques
        self.icon_surf = pg.image.load(self.icon_path).convert()
        self.tex_x = int(self.icon_surf.get_width()*0.75)
        self.tex_y = int(self.icon_surf.get_height()*0.75)
        self.icon = pg.transform.scale(self.icon_surf, (self.tex_x, self.tex_y))
        self.icon.set_colorkey([255, 255, 255])

    def show_on_sidebar(self):
        text_affiche = self.sidemenu.game.DEFAULT_FONT.font.render(self.ingame_name, True, (0, 0, 0)) # à changer en variable globale
        self.sidemenu.texture.blit(self.icon, self.icon_position) # Affichage de l'icône
        self.sidemenu.texture.blit(text_affiche, (self.icon_position[0] + self.ICON_TEXT_SPACING[0], self.icon_position[1] + self.ICON_TEXT_SPACING[1]))


class BagSubMenu(SubMenu):
    """Classe du sous-menu du Sac"""
    BAGICON_POSITION = (30, 100) # Temporaire
    
    def __init__(self, sidemenu):
        super().__init__("bag", "SAC", sidemenu, self.BAGICON_POSITION)



class SaveSubMenu(SubMenu):
    """Classe du sous-menu de sauvegarde"""
    SAVEICON_POSITION = (30, 200) # Temporaire
    def __init__(self, sidemenu):
        super().__init__("save", "SAUVER", sidemenu, self.SAVEICON_POSITION)
    # TODO Implémenter une fonction de sauvegarde des données
    # TODO Boîte de choix (Oui Non, MP MP*, SII Info (mais le choix est évident), etc.)


class MenuManager():
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        
        # Menu latéral
        self.sidemenu = SideMenu(self.game)
        self.sidemenu.bagmenu = BagSubMenu(self.sidemenu)
        self.sidemenu.savemenu = SaveSubMenu(self.sidemenu)
        
        # Menus secondaires
        pass

    def toggle_sidemenu(self):
        """Commute l'affichage du menu latéral"""
        if not self.game.player.is_talking:
            self.sidemenu.onscreen = not self.sidemenu.onscreen
            self.game.player.can_move = not self.game.player.can_move
            self.game.player.menu_is_open = not self.game.player.menu_is_open

    def draw(self):
        """Affiche le menu latéral s'il est ouvert"""
        if self.sidemenu.onscreen:
            self.sidemenu.show_sidemenu()
            for submenu in self.sidemenu.submenu_list:
                submenu.show_on_sidebar()
            self.sidemenu.show_arrow()
    
    def menu_move(self, direction):
        """Déplacement dans un menu"""
        # TODO Cas d'un submenu ouvert
        self.sidemenu.clear() # Effacement de l'ancienne position de la flèche
        if direction == "up":
            self.sidemenu.menu_move_up()
        elif direction == "down":
            self.sidemenu.menu_move_down()
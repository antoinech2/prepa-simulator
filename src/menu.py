#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame as pg
import pyscroll
import numpy as np


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
    # Constantes sonores
    OPEN_MENU_SFX_PATH = "res/sounds/sound_effect/open_menu.mp3"
    CLOSE_MENU_SFX_PATH = "res/sounds/sound_effect/close_menu.mp3"
    MOVE_ARROW_SFX_PATH = "res/sounds/sound_effect/typewriter.wav"

    # Constantes graphiques
    SIDEMENU_POSITION = (30, 100)
    TEXTURE_LOCATION = "res/textures/menu/sidemenu.png"
    SIDEMENU_OFFSET = (20, 20) # Temporaire, à passer en relatif
    ARROW_TEX = "res/textures/menu/arrow.png"

    def __init__(self, game):
        self.submenu_list = []
        self.game = game
        self.onscreen = False

        # Effets sonores
        self.open_sfx = pg.mixer.Sound(self.OPEN_MENU_SFX_PATH)
        self.close_sfx = pg.mixer.Sound(self.CLOSE_MENU_SFX_PATH)
        self.move_sfx = pg.mixer.Sound(self.MOVE_ARROW_SFX_PATH)

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
        if self.arrow_pos == len(self.submenu_list) - 1:
            self.arrow_pos = 0
        elif self.arrow_pos < len(self.submenu_list) - 1:
            self.arrow_pos += 1
        
    
    def menu_move_up(self):
        """Utilisation de la touche ↑"""
        if self.arrow_pos == 0:
            self.arrow_pos = len(self.submenu_list) - 1
        elif self.arrow_pos >= 1:
            self.arrow_pos -= 1
        
    
    def clear(self):
        """Suppression du contenu du menu latéral"""
        self.texture = pg.transform.scale(self.texture_surf, (self.tex_x, self.tex_y))
        self.texture.set_colorkey([255, 255, 255])
    
    def currently_opened_submenu(self):
        """Identifiant du sous-menu actuellement ouvert, None si aucun menu n'est ouvert"""
        for submenu_id in range(len(self.submenu_list)):
            if self.submenu_list[submenu_id].is_open:
                return(submenu_id) # Il n'y a qu'un seul submenu d'ouvert


class SubMenu():
    """Classe des menus secondaires"""
    SUBMENU_ICON_PATH = "res/textures/menu/submenu/"
    SUBMENU_BOX_PATH = "res/textures/menu/boxes/"
    ICON_TEXT_SPACING = (30, 6) # Temporaire
    DEFAULT_BOX_PATH = "res/textures/menu/boxes/default.png" # à enlever une fois que tous les menus seront implémentés
    def __init__(self, name, ingame_name, sidemenu, iconpos):
        self.name = name
        self.ingame_name = ingame_name
        self.sidemenu = sidemenu
        self.sidemenu.submenu_list.append(self)
        self.icon_path = f"{self.SUBMENU_ICON_PATH}{self.name}.png"
        self.box_path = f"{self.SUBMENU_BOX_PATH}{self.name}.png"
        self.icon_position = iconpos
        self.is_open = False

        # Graphiques sur le menu latéral
        self.icon_surf = pg.image.load(self.icon_path).convert()
        self.tex_x = int(self.icon_surf.get_width()*0.75)
        self.tex_y = int(self.icon_surf.get_height()*0.75)
        self.icon = pg.transform.scale(self.icon_surf, (self.tex_x, self.tex_y))
        self.icon.set_colorkey([255, 255, 255])

        # Graphiques de la boîte du sous-menu
        try:
            self.box_surf = pg.image.load(self.box_path).convert()
        except FileNotFoundError: # temporaire, à enlever une fois les autres menus implementés
            self.box_surf = pg.image.load(self.DEFAULT_BOX_PATH).convert()
        self.box_x = int(self.box_surf.get_width()*0.75)
        self.box_y = int(self.box_surf.get_height()*0.75)
        self.box = pg.transform.scale(self.box_surf, (self.box_x, self.box_y))
        self.box.set_colorkey([255, 255, 255])
    
    def clear(self):
        """Suppression du contenu du sous_menu"""
        self.box = pg.transform.scale(self.box_surf, (self.box_x, self.box_y))
        self.box.set_colorkey([255, 255, 255])

    def show_on_sidebar(self):
        """Affichage de l'icône et du nom du sous-menu dans le menu latéral"""
        text_affiche = self.sidemenu.game.DEFAULT_FONT.font.render(self.ingame_name, True, (0, 0, 0)) # à changer en variable globale
        self.sidemenu.texture.blit(self.icon, self.icon_position) # Affichage de l'icône
        self.sidemenu.texture.blit(text_affiche, (self.icon_position[0] + self.ICON_TEXT_SPACING[0], self.icon_position[1] + self.ICON_TEXT_SPACING[1])) # Affichage du nom du sous-menu avec un offset

    def open(self):
        """Ouverture du sous-menu"""
        rect = self.box.get_rect(center = (self.sidemenu.game.screen.get_size()[0] / 2, self.sidemenu.game.screen.get_size()[1] / 2))
        self.sidemenu.game.screen.blit(self.box, rect)

class MissionsSubMenu(SubMenu):
    """Classe du sous-menu des missions"""
    MISSICON_POSITION = (30, 50) # Temporaire
    def __init__(self, sidemenu):
        super().__init__("missions", "MISSIONS", sidemenu, self.MISSICON_POSITION)

class BagSubMenu(SubMenu):
    """Classe du sous-menu du Sac"""
    BAGICON_POSITION = (30, 100)        # Temporaire
    BAG_UPPERLEFT_CORNER = (60, 20)     # Coin haut gauche du Sac pour placer la première icône. Temporaire
    ONSCREEN_OBJECTS = 8                # Nombre d'objets affichés à l'écran
    LINE_HEIGHT = 40                    # Hauteur d'une ligne de texte
    NAME_ICON_OFFSET = (40, 0)          # Espace entre l'icône d'un objet et son nom. Temporaire
    AMOUNT_ICON_OFFSET = (40, 12)       # Espace entre l'icône d'un objet et sa quantité. Temporaire

    def __init__(self, sidemenu):
        super().__init__("bag", "SAC", sidemenu, self.BAGICON_POSITION)
        self.groups = self.sidemenu.game.player.bag.separate(self.ONSCREEN_OBJECTS) # Groupes ("pages") d'objets de taille ONSCREEN_OBJECTS
        print(self.groups)
        self.onscreen_group = 0 # ID du groupe à l'écran

    def show_object_row(self, object_couple, row):
        """Affiche un objet à la rangée choisie avec sa quantité"""
        # Affichage de l'icône
        icon_coords = (self.BAG_UPPERLEFT_CORNER[0], self.BAG_UPPERLEFT_CORNER[1] + row*self.LINE_HEIGHT)
        icon = self.sidemenu.game.map_manager.object_manager.list_of_objects[object_couple[0]].bag_sprite
        rect = icon.get_rect(topleft = icon_coords)
        self.box.blit(icon, rect)
        
        # Affichage du nom
        obj_nametag = self.sidemenu.game.DEFAULT_FONT.font.render(self.sidemenu.game.map_manager.object_manager.list_of_objects[object_couple[0]].name, True, (0, 0, 0))
        nametag_rect = obj_nametag.get_rect(topleft = np.array(icon_coords) + np.array(self.NAME_ICON_OFFSET))
        self.box.blit(obj_nametag, nametag_rect)

        # Affichage de la quantité
        qty_tag = self.sidemenu.game.DEFAULT_FONT.font.render(f"x{object_couple[1]}", True, (0, 0, 0))
        qty_rect = qty_tag.get_rect(topleft = np.array(icon_coords) + np.array(self.AMOUNT_ICON_OFFSET))
        self.box.blit(qty_tag, qty_rect)

    def print_menu_contents(self):
        """Affichage du contenu du Sac"""
        # TODO Faire des onglets (ie classificat° des objets), cette fonction est encore rudimentaire
        for row in range(len(self.groups[self.onscreen_group])):
            self.show_object_row(self.groups[self.onscreen_group][row], row)

    def refresh_groups(self):
        """Rafraîchissement des objets à afficher à l'écran"""
        self.groups = self.sidemenu.game.player.bag.separate(self.ONSCREEN_OBJECTS)
        print(self.groups)

class SaveSubMenu(SubMenu):
    """Classe du sous-menu de sauvegarde"""
    SAVEICON_POSITION = (30, 150) # Temporaire
    def __init__(self, sidemenu):
        super().__init__("save", "SAUVER", sidemenu, self.SAVEICON_POSITION)
    # TODO Implémenter une fonction de sauvegarde des données
    # TODO Boîte de choix (Oui Non, MP MP*, SII Info (mais le choix est évident), etc.)


class OptionsSubMenu(SubMenu):
    """Classe du sous-menu des options"""
    OPTIONSICON_POSITION = (30, 200) # Temporaire
    def __init__(self, sidemenu):
        super().__init__("options", "OPTIONS", sidemenu, self.OPTIONSICON_POSITION)

class MenuManager():
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        
        # Menu latéral
        self.sidemenu = SideMenu(self.game)
        self.sidemenu.missionsmenu = MissionsSubMenu(self.sidemenu)
        self.sidemenu.bagmenu = BagSubMenu(self.sidemenu)
        self.sidemenu.savemenu = SaveSubMenu(self.sidemenu)
        self.sidemenu.optionsmenu = OptionsSubMenu(self.sidemenu)
        
        # Menus secondaires
        pass

    def toggle_sidemenu(self):
        """Commute l'affichage du menu latéral"""
        if not self.game.player.is_talking and self.sidemenu.currently_opened_submenu() is None:
            self.sidemenu.onscreen = not self.sidemenu.onscreen
            self.game.player.can_move = not self.game.player.can_move
            self.game.player.menu_is_open = not self.game.player.menu_is_open
            if self.game.player.menu_is_open:
                pg.mixer.Sound.play(self.sidemenu.open_sfx) # Joue un son lorsqu'on ouvre le menu
            else:
                pg.mixer.Sound.play(self.sidemenu.close_sfx) # lorsqu'on ferme le menu

    def draw(self):
        """Affiche le menu latéral s'il est ouvert"""
        if self.sidemenu.onscreen:
            self.sidemenu.show_sidemenu()
            for submenu in self.sidemenu.submenu_list:
                submenu.show_on_sidebar()
            self.sidemenu.show_arrow()
            if self.sidemenu.currently_opened_submenu() is not None:
                self.sidemenu.submenu_list[self.sidemenu.currently_opened_submenu()].open()
                if self.sidemenu.currently_opened_submenu() == self.sidemenu.submenu_list.index(self.sidemenu.bagmenu):
                    self.sidemenu.bagmenu.print_menu_contents()
    
    def menu_move(self, direction):
        """Déplacement dans un menu"""
        # TODO Cas d'un submenu ouvert
        if self.sidemenu.onscreen:
            if self.sidemenu.currently_opened_submenu() is None: # si aucun menu n'est ouvert : déplacement dans le menu latéral
                self.sidemenu.clear() # Effacement de l'ancienne position de la flèche
                if direction == "up":
                    self.sidemenu.menu_move_up()
                elif direction == "down":
                    self.sidemenu.menu_move_down()
                pg.mixer.Sound.play(self.sidemenu.move_sfx)
    
    def open_menu(self):
        """Ouverture d'un sous-menu"""
        if self.sidemenu.currently_opened_submenu() is None:
            self.sidemenu.submenu_list[self.sidemenu.arrow_pos].is_open = True
            pg.mixer.Sound.play(self.sidemenu.open_sfx)
    
    def close_menu(self):
        """Fermeture d'un sous-menu"""
        # La fonction ne ferme pas le menu latéral, seulement le sous-menu
        if self.sidemenu.currently_opened_submenu() is not None:
            self.sidemenu.submenu_list[self.sidemenu.currently_opened_submenu()].is_open = False
            pg.mixer.Sound.play(self.sidemenu.close_sfx)
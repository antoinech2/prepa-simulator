#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame as pg
from pygame.image import load
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

    def __init__(self, name, ingame_name, sidemenu, iconpos, boundary, can_loop, line_height, initial_coords):
        self.name = name
        self.ingame_name = ingame_name
        self.sidemenu = sidemenu
        self.sidemenu.submenu_list.append(self)
        self.icon_path = f"{self.SUBMENU_ICON_PATH}{self.name}.png"
        self.box_path = f"{self.SUBMENU_BOX_PATH}{self.name}.png"
        self.icon_position = iconpos
        self.is_open = False

        # Paramètres relatifs à la flèche
        self.arrow = Arrow1D(self, boundary, can_loop, line_height, initial_coords)

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

    def draw(self):
        """Rafraîchissement de l'affichage"""
        self.show_on_sidebar()
        if self.is_open:
            self.open()
            self.arrow.draw()
            if type(self) == BagSubMenu:
                self.sidemenu.bagmenu.print_menu_contents()


class Arrow1D():
    """Classe des flèches à un degré de liberté"""
    # Utilisée dans les menus linéaires comme les boîtes Oui/Non, le Sac...
    # TODO ...et le menu latéral
    ARROW_TEX = "res/textures/menu/arrow.png"

    def __init__(self, parent, upper_limit, can_loop, line_height, origin_coords):
        self.parent = parent
        self.arrow_pos = 0 # Option courante
        self.upper_limit = upper_limit - 1 # Les positions commencent à 0
        self.can_loop = can_loop
        self.line_height = line_height
        self.origin_coords = origin_coords

        # Texture de la flèche
        self.arrow_tex_surf = pg.image.load(self.ARROW_TEX).convert()
        self.arrow_tex_x = int(self.arrow_tex_surf.get_width()*0.75)
        self.arrow_tex_y = int(self.arrow_tex_surf.get_height()*0.75)
        self.arrow_tex = pg.transform.scale(self.arrow_tex_surf, (self.arrow_tex_x, self.arrow_tex_y))
        self.arrow_tex.set_colorkey([255, 255, 255])

    def move_down(self):
        """Déplacement de la flèche vers le bas"""
        if self.arrow_pos < self.upper_limit:
            self.arrow_pos += 1
        elif self.arrow_pos >= self.upper_limit and self.can_loop:
            self.arrow_pos = 0

    def move_up(self):
        """Déplacement de la flèche vers le haut"""
        if self.arrow_pos > 0:
            self.arrow_pos -= 1
        elif self.arrow_pos <= 0 and self.can_loop:
            self.arrow_pos = self.upper_limit

    def draw(self):
        """Affichage à l'écran de la flèche"""
        rect = self.arrow_tex.get_rect(topleft = (self.origin_coords[0], self.origin_coords[1] + self.arrow_pos*self.line_height))
        self.parent.box.blit(self.arrow_tex, rect)

# TODO Classe Arrow2D

class MissionsSubMenu(SubMenu):
    """Classe du sous-menu des missions"""
    # WIP
    MISSICON_POSITION = (30, 50) # Temporaire
    def __init__(self, sidemenu, boundary, can_loop, line_height, initial_coords):
        super().__init__("missions", "MISSIONS", sidemenu, self.MISSICON_POSITION, boundary, can_loop, line_height, initial_coords)

class BagSubMenu(SubMenu):
    """Classe du sous-menu du Sac"""
    BAGICON_POSITION = (30, 100)        # Temporaire
    BAG_UPPERLEFT_CORNER = (80, 20)     # Coin haut gauche du Sac pour placer la première icône. Temporaire
    ONSCREEN_OBJECTS = 5                # Nombre d'objets affichés à l'écran
    NAME_ICON_OFFSET = (40, -4)         # Espace entre l'icône d'un objet et son nom. Temporaire
    AMOUNT_ICON_OFFSET = (40, 8)        # Espace entre l'icône d'un objet et sa quantité. Temporaire
    KEYITEM_OFFSET = (40, 2)            # Espace entre l'icône d'un objet clé et son nom. temporaire

    def __init__(self, sidemenu, boundary, can_loop, line_height, initial_coords):
        super().__init__("bag", "SAC", sidemenu, self.BAGICON_POSITION, boundary, can_loop, line_height, initial_coords)
        self.groups = self.sidemenu.game.player.bag.separate(self.ONSCREEN_OBJECTS) # Groupes ("pages") d'objets de taille ONSCREEN_OBJECTS
        print(self.groups)
        self.onscreen_group = 0 # ID du groupe à l'écran

    def show_object_row(self, object_couple, row):
        """Affiche un objet à la rangée choisie avec sa quantité"""
        # Affichage de l'icône
        parentobj = self.sidemenu.game.map_manager.object_manager.list_of_objects[object_couple[0]]
        icon_coords = (self.BAG_UPPERLEFT_CORNER[0], self.BAG_UPPERLEFT_CORNER[1] + row*self.arrow.line_height)
        icon = parentobj.bag_sprite
        rect = icon.get_rect(topleft = icon_coords)
        self.box.blit(icon, rect)

        # Affichage du nom
        obj_nametag = self.sidemenu.game.DEFAULT_FONT.font.render(self.sidemenu.game.map_manager.object_manager.list_of_objects[object_couple[0]].name, True, (0, 0, 0))
        if parentobj.category == "key_item":
            nametag_rect = obj_nametag.get_rect(topleft = np.array(icon_coords) + np.array(self.KEYITEM_OFFSET))
        else:
            nametag_rect = obj_nametag.get_rect(topleft = np.array(icon_coords) + np.array(self.NAME_ICON_OFFSET))
        self.box.blit(obj_nametag, nametag_rect)

        # Affichage de la quantité
        if parentobj.category != "key_item":
            qty_tag = self.sidemenu.game.DEFAULT_FONT.font.render(f"x{object_couple[1]}", True, (0, 0, 0))
            qty_rect = qty_tag.get_rect(topleft = np.array(icon_coords) + np.array(self.AMOUNT_ICON_OFFSET))
            self.box.blit(qty_tag, qty_rect)

    def print_menu_contents(self):
        """Affichage du contenu du Sac"""
        # TODO Faire des onglets (ie classificat° des objets), cette fonction est encore rudimentaire
        for row in range(len(self.groups[self.onscreen_group])):
            self.show_object_row(self.groups[self.onscreen_group][row], row)

    def previous_group(self):
        if self.onscreen_group > 0:
            self.onscreen_group -= 1
            self.arrow.arrow_pos = 0

    def next_group(self):
        if self.onscreen_group < len(self.groups) - 1:
            self.onscreen_group += 1
            self.arrow.arrow_pos = 0

    def refresh_groups(self):
        """Rafraîchissement des objets à afficher à l'écran"""
        self.groups = self.sidemenu.game.player.bag.separate(self.ONSCREEN_OBJECTS)
        self.arrow.upper_limit = len(self.groups[self.onscreen_group]) - 1

class SaveSubMenu(SubMenu):
    """Classe du sous-menu de sauvegarde"""
    SAVEICON_POSITION = (30, 150) # Temporaire
    def __init__(self, sidemenu, boundary, can_loop, line_height, initial_coords):
        super().__init__("save", "SAUVER", sidemenu, self.SAVEICON_POSITION, boundary, can_loop, line_height, initial_coords)
    # TODO Implémenter une fonction de sauvegarde des données
    # TODO Boîte de choix (Oui Non, MP MP*, SII Info (mais le choix est évident), etc.)


class OptionsSubMenu(SubMenu):
    """Classe du sous-menu des options"""
    OPTIONSICON_POSITION = (30, 200) # Temporaire
    def __init__(self, sidemenu, boundary, can_loop, line_height, initial_coords):
        super().__init__("options", "OPTIONS", sidemenu, self.OPTIONSICON_POSITION, boundary, can_loop, line_height, initial_coords)

class MenuManager():
    MISSIONS_ORIGIN_COORDS = (-1, -1)       # WIP
    BAG_SUBMENU_HEIGHT = 5
    BAG_LINE_HEIGHT = 40                    # Hauteur d'une ligne de texte
    BAG_ORIGIN_COORDS = (60, 20)            # Coordonnées initiales de la flèche (Sac)
    SAVE_ORIGIN_COORDS = (-1, -1)           # WIP
    OPTIONS_ORIGIN_COORDS = (-1, -1)        # WIP



    def __init__(self, screen, game):
        self.screen = screen
        self.game = game

        # Menu latéral
        self.sidemenu = SideMenu(self.game)
        self.sidemenu.missionsmenu = MissionsSubMenu(self.sidemenu, -1, True, -1, self.MISSIONS_ORIGIN_COORDS)   # valeur numérique arbitraire, sera implémentée correctement une fois ce menu implémenté
        self.sidemenu.bagmenu = BagSubMenu(self.sidemenu, self.BAG_SUBMENU_HEIGHT, True, self.BAG_LINE_HEIGHT, self.BAG_ORIGIN_COORDS)
        self.sidemenu.savemenu = SaveSubMenu(self.sidemenu, -1, True, -1, self.SAVE_ORIGIN_COORDS)           # même remarque
        self.sidemenu.optionsmenu = OptionsSubMenu(self.sidemenu, -1, True, -1, self.OPTIONS_ORIGIN_COORDS)     # même remarque

        # Menus secondaires
        pass

    def toggle_sidemenu(self):
        """Commute l'affichage du menu latéral"""
        if self.sidemenu.currently_opened_submenu() is None:
            self.sidemenu.onscreen = not self.sidemenu.onscreen
            self.game.player.can_move = not self.game.player.can_move
            self.game.menu_is_open = not self.game.menu_is_open
            if self.game.menu_is_open:
                pg.mixer.Sound.play(self.sidemenu.open_sfx) # Joue un son lorsqu'on ouvre le menu
            else:
                pg.mixer.Sound.play(self.sidemenu.close_sfx) # lorsqu'on ferme le menu

    def draw(self):
        """Affiche le menu latéral s'il est ouvert"""
        if self.sidemenu.onscreen:
            self.sidemenu.show_sidemenu()
            self.sidemenu.show_arrow()
            for submenu in self.sidemenu.submenu_list:
                submenu.draw()

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
            elif self.sidemenu.currently_opened_submenu() == self.sidemenu.submenu_list.index(self.sidemenu.bagmenu): # sinon forcément un submenu est ouvert
                # Actions spécifiques au Sac
                bagmenu = self.sidemenu.submenu_list[self.sidemenu.currently_opened_submenu()]
                bagmenu.clear()
                if direction == "up":
                    bagmenu.arrow.move_up()
                elif direction == "down":
                    bagmenu.arrow.move_down()
                elif direction == "left":
                    bagmenu.previous_group()
                elif direction == "right":
                    bagmenu.next_group()
                bagmenu.refresh_groups() # Rafraîchissement pour prendre en compte les nouveaux objets affichés à l'écran

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

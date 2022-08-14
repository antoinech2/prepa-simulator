#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame as pg
import numpy as np


# TODO Uniformisation des dialogues sous le module menu
class Font():
    """Classe de la police d'écriture"""
    def __init__(self, font_name):
        self.font_name = font_name
        self.font_size = 16
        self.font = pg.font.SysFont(self.font_name, self.font_size)
        self.font_width = max([metric[1] for metric in self.font.metrics("azertyuiopqsdfghjklmwxcvbnAZERTYUIOPQSDFGHJKLMWXCVBN")]) # Chasse maximale pour la police choisie


class SideMenu():
    """Classe du menu latéral"""
    # Constantes sonores
    OPEN_MENU_SFX_PATH = "res/sounds/fx/open_menu.mp3"
    CLOSE_MENU_SFX_PATH = "res/sounds/fx/close_menu.mp3"
    MOVE_ARROW_SFX_PATH = "res/sounds/fx/typewriter.wav"

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
        # TODO : Passage à un objet Arrow1D
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
        text_affiche = self.sidemenu.game.default_font.font.render(self.ingame_name, True, (0, 0, 0)) # à changer en variable globale
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
            if type(self) == MissionsSubMenu:
                self.sidemenu.missionsmenu.print_menu_contents()


class ChoiceBox():
    """Classe des boîtes à choix multiple"""
    UPPERLEFT_CORNER = [20, 20]     # Position de la flèche dans sa position initiale
    ARROW_MARGIN = 25               # Espace entre la flèche et le texte
    LINE_HEIGHT = 40                # TODO Unifier les hauteurs de ligne dans Game
    CB_TEXTURE = "res/textures/choicebox.png"       # à changer pour des choicebox avec plus de 2 options

    def __init__(self, game, choices):
        self.game = game
        self.choices = choices
        self.arrow = Arrow1D(self, len(choices), False, self.game.menu_manager.BAG_LINE_HEIGHT, self.UPPERLEFT_CORNER)

        # Texture de la boîte
        self.box_surf = pg.image.load(self.CB_TEXTURE).convert()
        self.box_x = int(self.box_surf.get_width()*0.75)
        self.box_y = int(self.box_surf.get_height()*0.75)
        self.box = pg.transform.scale(self.box_surf, (self.box_x, self.box_y))
        self.box.set_colorkey([255, 255, 255])

    def print_choice(self, choice_id):
        """Affichage d'un choix dans le menu"""
        ch_nametag = self.game.default_font.font.render(self.choices[choice_id], True, (0, 0, 0))
        nametag_rect = ch_nametag.get_rect(topleft = np.array(self.UPPERLEFT_CORNER) + np.array([self.ARROW_MARGIN, choice_id * self.LINE_HEIGHT]))
        self.box.blit(ch_nametag, nametag_rect)
    
    def choice_taken(self):
        """Mise à jour dans le Menu Manager de l'option choisie"""
        # TODO à voir si le deuxième élément du tuple est utile ou non...
        self.game.menu_manager.choicebox_result = (self.arrow.arrow_pos, self.choices[self.arrow.arrow_pos])
        self.game.menu_manager.close_choicebox()
    
    def clear(self):
        """Suppression du contenu de la boîte"""
        self.box = pg.transform.scale(self.box_surf, (self.box_x, self.box_y))
        self.box.set_colorkey([255, 255, 255])

    def open(self):
        """Ouverture de la boîte de choix"""
        rect = self.box.get_rect(center = (self.game.screen.get_size()[0] / 2, self.game.screen.get_size()[1] / 2))
        self.game.screen.blit(self.box, rect)

    def draw(self):
        """Rafraîchissement de l'affichage"""
        self.open()
        self.arrow.draw()
        for choice in range(len(self.choices)):
            self.print_choice(choice)

class MiniBox():
    """Classe des émoticônes"""
    VERTICAL_OFFSET = -50       # Temporaire
    def __init__(self, game, img, target):
        self.game = game
        self.tex = pg.image.load(f"res/textures/minibox/{img}.png").convert()
        self.tex.set_colorkey([255, 255, 255])
        if target == "player":
            self.rect = self.tex.get_rect(center = (self.game.screen.get_size()[0]/2, self.game.screen.get_size()[1]/2 + self.VERTICAL_OFFSET))
    
    def draw(self):
        """Rafraîchissement de l'affichage"""
        self.game.screen.blit(self.tex, self.rect)


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
    
    def action(self):
        """Appui de la touche d'action"""
        pass

    def draw(self):
        """Affichage à l'écran de la flèche"""
        rect = self.arrow_tex.get_rect(topleft = (self.origin_coords[0], self.origin_coords[1] + self.arrow_pos*self.line_height))
        self.parent.box.blit(self.arrow_tex, rect)

# TODO Classe Arrow2D

class MissionsSubMenu(SubMenu):
    """Classe du sous-menu des missions"""
    # WIP
    MISSICON_POSITION = (30, 30) # Temporaire
    MISSIONS_UPPERLEFT_CORNER = (40, 15)
    LINE_HEIGHT = 30
    ONSCREEN_MISSIONS = 11
    NAME_ICON_OFFSET = (40, 1)
    PROGRESS_SPRITE_PATH = "res/textures/mission_status"

    def __init__(self, sidemenu, boundary, can_loop, line_height, initial_coords):
        super().__init__("missions", "MISSIONS", sidemenu, self.MISSICON_POSITION, boundary, can_loop, line_height, initial_coords)
        all_missions = list(self.sidemenu.game.mission_manager.dict_of_missions.keys())
        self.groups = []
        #self.arrow = Arrow1D(self, self.ONSCREEN_MISSIONS, False, self.LINE_HEIGHT, self.MISSIONS_UPPERLEFT_CORNER)

        # Composition des groupes
        while all_missions != []:
            group = []
            try:
                while len(group) < self.ONSCREEN_MISSIONS:
                    group.append(all_missions.pop(0))
            except IndexError:
                pass
            self.groups.append(group)

        self.onscreen_group = 0
    
    def show_mission_row(self, id, row):
        """Affiche une mission à la rangée choisie"""
        # Affichage du statut
        status = self.sidemenu.game.mission_manager.dict_of_missions[id].current_status
        icon_coords = (self.MISSIONS_UPPERLEFT_CORNER[0], self.MISSIONS_UPPERLEFT_CORNER[1] + row*self.arrow.line_height + 4)       #! Cf BagSubMenu
        icon = pg.image.load(f"{self.PROGRESS_SPRITE_PATH}/{status}.jpg").convert()
        rect = icon.get_rect(topleft = icon_coords)
        self.box.blit(icon, rect)
        # Affichage du nom
        if self.sidemenu.game.mission_manager.dict_of_missions[id].current_status != "blank":
            nametag = self.sidemenu.game.default_font.font.render(f"N°{str(id).zfill(3)} {self.sidemenu.game.mission_manager.dict_of_missions[id].name}", True, (0, 0, 0))
            nametag_rect = nametag.get_rect(topleft = np.array(icon_coords) + np.array(self.NAME_ICON_OFFSET))
            self.box.blit(nametag, nametag_rect)
        else:     # Affichage d'une suite de points d'interrogation
            nametag = self.sidemenu.game.default_font.font.render(f"N°{str(id).zfill(3)} ????????????????????????????????", True, (0, 0, 0))
            nametag_rect = nametag.get_rect(topleft = np.array(icon_coords) + np.array(self.NAME_ICON_OFFSET))
            self.box.blit(nametag, nametag_rect)

    def print_menu_contents(self):
        """Affichage du contenu du menu des missions"""
        # TODO Faire des onglets pour séparer les missions par type
        for row in range(len(self.groups[self.onscreen_group])):
            self.show_mission_row(self.groups[self.onscreen_group][row], row)


class BagSubMenu(SubMenu):
    """Classe du sous-menu du Sac"""
    LATERAL_WINDOW_UPPERLEFT = (521, 0) # Coin haut gauche de la fenêtre latérale après redimensionnement
    LATERAL_WINDOW_SIZE = (300, 375)    # Taille de la fenêtre latérale
    LATICON_VOFFSET = 70                # Décalage vertical pour le placement du centre de l'icône dans la barre latérale
    CLASS_VOFFSET = 50                  # Espace entre l'icône et la catégorie de l'objet
    DESC_VOFFSET = 35                   # Espace entre la catégorie et la description
    DESC_MAXLENGTH = 26                 # Longueur maximale d'une ligne de description (le maximum possible est 30)
    DESC_LINEHEIGHT = 22                # Hauteur d'une ligne de texte
    BAGICON_POSITION = (30, 80)         # Temporaire
    BAG_UPPERLEFT_CORNER = (80, 20)     # Coin haut gauche du Sac pour placer la première icône. Temporaire
    ONSCREEN_OBJECTS = 5                # Nombre d'objets affichés à l'écran
    NAME_ICON_OFFSET = (40, -4)         # Espace entre l'icône d'un objet et son nom. Temporaire
    AMOUNT_ICON_OFFSET = (40, 8)        # Espace entre l'icône d'un objet et sa quantité. Temporaire
    KEYITEM_OFFSET = (40, 2)            # Espace entre l'icône d'un objet clé et son nom. temporaire

    def __init__(self, sidemenu, boundary, can_loop, line_height, initial_coords):
        super().__init__("bag", "SAC", sidemenu, self.BAGICON_POSITION, boundary, can_loop, line_height, initial_coords)
        self.groups = self.sidemenu.game.bag.separate(self.ONSCREEN_OBJECTS) # Groupes ("pages") d'objets de taille ONSCREEN_OBJECTS
        self.onscreen_group = 0 # ID du groupe à l'écran
        print(self.groups)

    def show_object_row(self, object_couple, row):
        """Affiche un objet à la rangée choisie avec sa quantité"""
        # Affichage de l'icône
        parentobj = self.sidemenu.game.map_manager.object_manager.list_of_objects[object_couple[0]]
        icon_coords = (self.BAG_UPPERLEFT_CORNER[0], self.BAG_UPPERLEFT_CORNER[1] + row*self.arrow.line_height + 4)      #! Le 4 est temporaire, il sert à aligner l'icône et la flèche
        icon = parentobj.bag_sprite
        rect = icon.get_rect(topleft = icon_coords)
        self.box.blit(icon, rect)

        # Affichage du nom
        obj_nametag = self.sidemenu.game.default_font.font.render(self.sidemenu.game.map_manager.object_manager.list_of_objects[object_couple[0]].name, True, (0, 0, 0))
        if parentobj.category == "key_item":
            nametag_rect = obj_nametag.get_rect(topleft = np.array(icon_coords) + np.array(self.KEYITEM_OFFSET))
        else:
            nametag_rect = obj_nametag.get_rect(topleft = np.array(icon_coords) + np.array(self.NAME_ICON_OFFSET))
        self.box.blit(obj_nametag, nametag_rect)

        # Affichage de la quantité si l'objet n'est pas un objet-clé (ie. disponible en un seul exemplaire)
        if parentobj.category != "key_item":
            qty_tag = self.sidemenu.game.default_font.font.render(f"x{object_couple[1]}", True, (0, 0, 0))
            qty_rect = qty_tag.get_rect(topleft = np.array(icon_coords) + np.array(self.AMOUNT_ICON_OFFSET))
            self.box.blit(qty_tag, qty_rect)
        
    
    def lateral(self):
        """Affichage dans la fenêtre latérale des données relatives à l'objet sélectionné"""
        # Obtention de l'icône
        id = self.groups[self.onscreen_group][self.arrow.arrow_pos][0]          # Identifiant de l'objet sélectionné
        parentobj = self.sidemenu.game.map_manager.object_manager.list_of_objects[id]
        icon = parentobj.bag_sprite
        enlarged_icon = pg.transform.scale(icon, 3 * np.array(icon.get_size()))

        # Affichage de l'icône de l'objet
        lat_icon_coords = (int(self.LATERAL_WINDOW_UPPERLEFT[0] + self.LATERAL_WINDOW_SIZE[0] / 2),
                           int(self.LATERAL_WINDOW_UPPERLEFT[1] + self.LATICON_VOFFSET))
        rect2 = enlarged_icon.get_rect(center = lat_icon_coords)
        self.box.blit(enlarged_icon, rect2)

        # Affichage de la classe
        cat_raw = self.sidemenu.game.map_manager.object_manager.list_of_objects[id].category
        if cat_raw == "item":
            cat = "Objet"
        if cat_raw == "consumable":
            cat = "Objet consommable"
        if cat_raw == "key_item":
            cat = "Objet important"
        cat_tag = self.sidemenu.game.default_font.font.render(cat, True, (0, 0, 0))
        cat_rect = cat_tag.get_rect(center = np.array(lat_icon_coords) + np.array([1, self.CLASS_VOFFSET]))        #! Le 1 correspond à une correction graphique
        self.box.blit(cat_tag, cat_rect)

        # Construction et affichage de la description
        desc = self.sidemenu.game.map_manager.object_manager.list_of_objects[id].desc
        def format(text):
            """Découpage d'un texte en plusieurs lignes de taille adéquate"""
            formatted_text = []
            splitted_text = text.split()
            text_line = ""
            line_length = 0
            while splitted_text != []:
                word_length = len(splitted_text[0])
                if line_length + word_length > self.DESC_MAXLENGTH:
                    formatted_text.append(text_line)
                    text_line = ""
                    line_length = 0
                text_line += splitted_text[0] + " "
                line_length += word_length + 1
                del(splitted_text[0])
            formatted_text.append(text_line)
            return(formatted_text)
        splitted_desc = format(desc)
        for line in range(len(splitted_desc)):
            splitted_desc[line] = splitted_desc[line].rstrip()
            pgdesc = self.sidemenu.game.default_font.font.render(splitted_desc[line], True, (0, 0, 0))
            desc_rect = pgdesc.get_rect(center = np.array(lat_icon_coords) + np.array([1, self.CLASS_VOFFSET]) + np.array([1, self.DESC_VOFFSET]) + np.array([0, line * self.DESC_LINEHEIGHT]))        #! Le 1 correspond à une correction graphique
            self.box.blit(pgdesc, desc_rect)
        
        # Affichage du menu contextuel

    def print_menu_contents(self):
        """Affichage du contenu du Sac"""
        # TODO Faire des onglets pour séparer les objets par catégorie
        for row in range(len(self.groups[self.onscreen_group])):
            self.show_object_row(self.groups[self.onscreen_group][row], row)
        self.lateral()

    def previous_group(self):
        """Décrémente le groupe actuellement affiché à l'écran"""
        if self.onscreen_group > 0:
            self.onscreen_group -= 1
            self.arrow.arrow_pos = 0

    def next_group(self):
        """Incrémente le groupe actuellement affiché à l'écran"""
        if self.onscreen_group < len(self.groups) - 1:
            self.onscreen_group += 1
            self.arrow.arrow_pos = 0

    def refresh_groups(self):
        """Rafraîchissement des objets à afficher à l'écran"""
        self.groups = self.sidemenu.game.bag.separate(self.ONSCREEN_OBJECTS)
        self.arrow.upper_limit = len(self.groups[self.onscreen_group]) - 1

class SaveSubMenu(SubMenu):
    """Classe du sous-menu de sauvegarde"""
    SAVEICON_POSITION = (30, 130) # Temporaire
    def __init__(self, sidemenu, boundary, can_loop, line_height, initial_coords):
        super().__init__("save", "SAUVER", sidemenu, self.SAVEICON_POSITION, boundary, can_loop, line_height, initial_coords)
    
    def toggled(self):
        """Exécution de l'action de sauvegarde et fermeture du menu latéral"""
        self.sidemenu.game.menu_manager.close_menu()        # Fermeture du sous-menu de sauvegarde
        self.sidemenu.game.menu_manager.toggle_sidemenu()   # Fermeture du menu latéral
        sm = self.sidemenu.game.script_manager
        sm.execute_script(sm.find_script_from_name("save"), "back")


class OptionsSubMenu(SubMenu):
    """Classe du sous-menu des options"""
    OPTIONSICON_POSITION = (30, 180) # Temporaire
    def __init__(self, sidemenu, boundary, can_loop, line_height, initial_coords):
        super().__init__("options", "OPTIONS", sidemenu, self.OPTIONSICON_POSITION, boundary, can_loop, line_height, initial_coords)

class MenuManager():
    MISSIONS_SUBMENU_HEIGHT = 11             # Nombre de missions par menu
    MISSIONS_LINE_HEIGHT = 30
    MISSIONS_ORIGIN_COORDS = (20, 15)       # Coordonnées initiales de la flèche (missions)
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
        self.sidemenu.missionsmenu = MissionsSubMenu(self.sidemenu, self.MISSIONS_SUBMENU_HEIGHT, True, self.MISSIONS_LINE_HEIGHT, self.MISSIONS_ORIGIN_COORDS)   # valeur numérique arbitraire, sera implémentée correctement une fois ce menu implémenté
        self.sidemenu.bagmenu = BagSubMenu(self.sidemenu, self.BAG_SUBMENU_HEIGHT, True, self.BAG_LINE_HEIGHT, self.BAG_ORIGIN_COORDS)
        self.sidemenu.savemenu = SaveSubMenu(self.sidemenu, -1, True, -1, self.SAVE_ORIGIN_COORDS)           # même remarque
        self.sidemenu.optionsmenu = OptionsSubMenu(self.sidemenu, -1, True, -1, self.OPTIONS_ORIGIN_COORDS)     # même remarque
        # Menus secondaires
        self.choicebox = None           # Boîte à choix multiples
        self.choicebox_result = None    # Place et nom de l'option choisie dans la choicebox
        # Boîtes de décoration
        self.minibox = None

    def toggle_sidemenu(self):
        """Commute l'affichage du menu latéral"""
        if self.game.dialogue is None and self.sidemenu.currently_opened_submenu() is None:
            # Réinitialisation des positions des flèches
            self.sidemenu.bagmenu.onscreen_group = 0
            self.sidemenu.bagmenu.arrow.arrow_pos = 0

            # Rafraîchissement de l'affichage de tous les sous-menus
            self.sidemenu.bagmenu.clear()

            # Ouverture ou fermeture du sous-menu
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
        if self.choicebox is not None:
            self.choicebox.draw()
        if self.minibox is not None:
            self.minibox.draw()

    def menu_move(self, direction):
        """Déplacement dans un menu"""
        if self.choicebox is not None:
            self.choicebox.clear()
            if direction == "up":
                self.choicebox.arrow.move_up()
            elif direction == "down":
                self.choicebox.arrow.move_down()
        elif self.sidemenu.onscreen:
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
                    if bagmenu.arrow.arrow_pos > len(bagmenu.groups[bagmenu.onscreen_group]):        # Dépassement lié à un groupe d'objets incomplet
                        bagmenu.arrow.arrow_pos = len(bagmenu.groups[bagmenu.onscreen_group]) - 1
                elif direction == "down":
                    bagmenu.arrow.move_down()
                elif direction == "left":
                    bagmenu.previous_group()
                elif direction == "right":
                    bagmenu.next_group()
                bagmenu.refresh_groups() # Rafraîchissement pour prendre en compte les nouveaux objets affichés à l'écran
            elif self.sidemenu.currently_opened_submenu() == self.sidemenu.submenu_list.index(self.sidemenu.missionsmenu):
                # Actions spécifiques aux missions
                mismenu = self.sidemenu.submenu_list[self.sidemenu.currently_opened_submenu()]
                mismenu.clear()
                if direction == "up":
                    mismenu.arrow.move_up()
                elif direction == "down":
                    mismenu.arrow.move_down()

    def open_menu(self):
        """Ouverture d'un sous-menu"""
        if self.sidemenu.currently_opened_submenu() is None:
            self.sidemenu.submenu_list[self.sidemenu.arrow_pos].is_open = True
            pg.mixer.Sound.play(self.sidemenu.open_sfx)
            if self.sidemenu.currently_opened_submenu() == self.sidemenu.submenu_list.index(self.sidemenu.savemenu):
                self.sidemenu.savemenu.toggled()

    def close_menu(self):
        """Fermeture d'un sous-menu"""
        # La fonction ne ferme pas le menu latéral, seulement le sous-menu
        if self.sidemenu.currently_opened_submenu() is not None:
            self.sidemenu.submenu_list[self.sidemenu.currently_opened_submenu()].is_open = False
            pg.mixer.Sound.play(self.sidemenu.close_sfx)
    
    def open_choicebox(self, choices):
        """Ouverture d'une boîte à choix multiples"""
        if self.choicebox is None:
            self.game.player.can_move = False
            self.choicebox = ChoiceBox(self.game, choices)
    
    def close_choicebox(self):
        """Fermeture d'une boîte à choix multiples"""
        if self.choicebox is not None:
            if not self.sidemenu.onscreen:
                self.game.player.can_move = True       # On peut bouger à la fermeture de la boîte uniquement si le menu latéral n'est pas ouvert
            self.choicebox = None

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Gestion des objets"""

import pygame as pg
import dialogue

class ObjectManager():
    """Classe de gestion des différents objets du jeu"""
    def __init__(self, map):
        self.obj_group = pg.sprite.Group()
        self.map = map
        self.total_object_count = self.map.game.game_data_db.execute("select count(*) from objects;")
        self.list_of_objects = []

        # Chargement des propriétés des objets
        self.initialize_object_properties()

        # Chargement de la liste des objets
        obj_list = self.map.game.game_data_db.execute("select objects.id, x_coord, y_coord, object_id, hidden from objects join maps on objects.map_id = maps.id where maps.id = ?", (map.map_id,)).fetchall()
        for obj in obj_list:
            new_object = MapObject(map, obj[0], (obj[1], obj[2]), self.list_of_objects[obj[3]], (True if obj[4] == 1 else False))
            if new_object.exists:
                self.obj_group.add(new_object)
                self.map.object_group.add(new_object)

    def pickup_check(self):
        """Vérification de l'existence d'un objet avant ramassage"""
        obj_collide_list = pg.sprite.spritecollide(self.map.game.player, self.obj_group, False)
        for obj in obj_collide_list:            # Liste de tous les objets autour du joueur, inclut les objets déjà ramassés
            if not obj.exists:
                obj_collide_list.remove(obj)    # Seuls les objets non ramassés sont pris en compte
        if len(obj_collide_list) != 0:
            self.map.game.bag.pickup_object(obj_collide_list[0])
            obj_collide_list[0].save()
            self.map.game.map_manager.sound_manager.play_sfx("jingleV2")        # Musique d'obtention d'un objet
            self.map.game.dialogue = dialogue.Dialogue(self.map.game, None, True, None, [f"Obtenu : {obj_collide_list[0].parent.name} !"])      # Boîte de dialogue informant le joueur
        self.refresh_objects()
        self.map.game.menu_manager.sidemenu.bagmenu.refresh_groups()     # Mise à jour de l'affichage des objets dans le sac
        
        print(self.map.game.menu_manager.sidemenu.bagmenu.groups)

    def refresh_objects(self):
        """Suppression du sprite des objets ramassés"""
        for obj in self.obj_group:
            if not obj.exists:
                self.map.object_group.remove(obj)                     # Affichage du sprite de l'objet sur la carte
    
    def initialize_object_properties(self):
        """Initialisation des propriétés des objets du jeu"""
        object_ids = self.map.game.game_data_db.execute("select id from object_list;").fetchall()
        object_names = self.map.game.game_data_db.execute("select object_name from object_list;").fetchall()
        object_categories = self.map.game.game_data_db.execute("select object_category from object_list;").fetchall()
        object_descs = self.map.game.game_data_db.execute("select object_desc from object_list;").fetchall()
        for id in range(len(object_ids)):
            self.list_of_objects.append(Object(object_ids[id][0], object_names[id][0], object_categories[id][0], object_descs[id][0])) # La liste est considérée dans l'ordre


class MapObject(pg.sprite.Sprite):
    """Classe des objets sur la carte"""
    # TODO Nettoyer cette classe, elle est réservée à l'affichage sur la carte d'un élément de objects
    OBJ_TEX_FOLDER = "res/textures/objects/"
    OVERWORLD_TEX = "res/textures/objects/overworld.png"

    def __init__(self, map, id, coords, parent, hidden):
        super().__init__()
        self.map = map
        self.id = id
        self.parent = parent         # Entité Object dont est issu l'objet de la carte
        self.path = f"{self.OBJ_TEX_FOLDER}placeholder.png"         # Chemin de l'icône dans le Sac de l'objet TODO à remplacer par {self.name}.png lorsque le Sac sera implémenté
        self.is_hidden = hidden
        self.exists = False if self.map.game.save.execute('select obtained from mapobjects where mapobj_id = ?;', (self.id,)).fetchall()[0][0] == 1 else True

        # Affichage du sprite, les variables sont similaires à celles de la classe Npc
        self.bag_sprite = pg.image.load(self.path)                  # Le sprite dans le sac
        self.overworld_sprite = pg.image.load(self.OVERWORLD_TEX)   # Le sprite sur la carte du monde
        self.image = pg.Surface([16, 16])
        if self.is_hidden:
            self.image.set_alpha(0)     # Le sprite est totalement transparent
        else:
            self.image.set_colorkey([0, 0, 0])      # Sinon, le sprite est opaque
        self.rect = self.image.get_rect()
        self.rect.topleft = coords
        if self.exists:     # Affichage de l'objet s'il n'a pas encore été ramassé
            self.image.blit(self.overworld_sprite, (0, 0),
                            (0, 0, 16, 16))
    
    def save(self):
        """Sauvegarde de l'état de l'objet sur la carte pour empêcher sa réapparition"""
        self.map.game.save.execute('replace into mapobjects values (?, 1)', (self.id,))


class Object():
    """Classe générale des objets"""
    OBJ_TEX_FOLDER = "res/textures/objects/"
    OVERWORLD_TEX = "res/textures/objects/overworld.png"
    PLACEHOLDER_TEX_PATH = "res/textures/objects/placeholder.png"
    
    def __init__(self, id, name, category, desc):
        self.id = id
        self.name = name
        self.category = category
        self.desc = desc
        self.path = f"{self.OBJ_TEX_FOLDER}object{self.id}.png"         # Chemin de l'icône dans le Sac de l'objet

        # Graphismes
        try:
            self.bag_sprite = pg.image.load(self.path)
        except FileNotFoundError: # TODO à remplacer lorsque tous les objets auront des icônes
            self.bag_sprite = pg.image.load(self.PLACEHOLDER_TEX_PATH)
        self.overworld_sprite = pg.image.load(self.OVERWORLD_TEX)
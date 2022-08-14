#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import externe
import pygame as pg

import entities

"""Gère les NPC du jeu"""


class NpcManager():
    """Gère le chargement des NPC et le déclenchement des dialogues"""
    def __init__(self, map):
        # Objet associé
        self.map = map

        # Liste les NPC chargés
        self.npc_group = pg.sprite.Group()

        # Liste des PNJ en train de parler
        self.talking_npcs = []

        # Chargement de tous les NPC de la carte
        npcs = self.map.game.game_data_db.execute("SELECT npc.id, npc.nom, x_coord, y_coord, direction, script_id, sprite FROM npc JOIN maps ON npc.map_id = maps.id WHERE maps.id = ?", (map.map_id,)).fetchall()
        for npc in npcs:
            new_npc = entities.Npc(map, npc[0], npc[1], (npc[2], npc[3]), npc[4], npc[5], npc[6])
            self.npc_group.add(new_npc)
            self.map.object_group.add(new_npc)
    
    def flip(self):
        """Réinitialise l'orientation de tous les PNJs"""
        for npc in self.npc_group:
            if npc.direction == 0:
                disp = "up"
            if npc.direction == 90:
                disp = "right"
            if npc.direction == 180:
                disp = "down"
            if npc.direction == 270:
                disp = "left"
            self.map.game.script_manager.setdirection(npc.id, disp)
    
    def force_flip(self, id, direction):
        """Force un PNJ à s'orienter selon une direction donnée"""
        if direction == 0:
            disp = "up"
        if direction == 90:
            disp = "right"
        if direction == 180:
            disp = "down"
        if direction == 270:
            disp = "left"
        self.map.game.script_manager.setdirection(self.find_npc(id), disp)
    
    def find_npc(self, id):
        """Cherche un PNJ par son identifiant"""
        for npc in self.npc_group:
            if npc.id == id:
                return(npc)
        return(None)

    def check_talk(self):
        """Démarre le dialogue avec un NPC proche"""
        npc_collide_list = pg.sprite.spritecollide(self.map.game.player, self.npc_group, False)
        if len(npc_collide_list) > 0:
            first_npc = npc_collide_list[0]
            if first_npc not in self.talking_npcs:
                self.talking_npcs.append(first_npc)
                self.map.game.script_manager.execute_script(first_npc.script, "back", first_npc)


class OldNpc(pg.sprite.Sprite):
    """Représente un NPC (ancienne version)"""

    DEFAULT_SPRITESHEET_LOC = 'res/textures/m2.png'

    def __init__(self, map, id, name, coords, direction, script_id, sprite = None):
        super().__init__()

        # Objet associé
        self.map = map

        # Variables d'état
        self.id = id
        self.name = name
        self.direction = direction
        if script_id is not None:
            self.script = self.map.game.script_manager.get_script_from_id(script_id)
        else:
            self.script = self.map.game.script_manager.find_script_from_name("ordinaryNpc") # Temporaire, tous les NPC disposent du script dummyScript

        # Graphique
        if sprite is None:
            self.sprite_sheet = pg.image.load(self.DEFAULT_SPRITESHEET_LOC)
        else:
            self.sprite_sheet = pg.image.load(f"res/textures/{sprite}.png")
        self.image = pg.Surface([32, 32])  # creation d'une image
        if sprite == "void":    # Cas du NPC invisible
            self.image.set_alpha(0)
        else:
            self.image.set_colorkey([0, 0, 0])  # transparence
        self.rect = self.image.get_rect()  # rectangle autour du joueur
        self.rect.topleft = coords  # placement du npc
        self.image.blit(self.sprite_sheet, (0, 0),
                        (0, 0, 32, 32))  # affichage du npc
        self.feet = pg.Rect(0, 0, self.rect.width * 0.5, 12)

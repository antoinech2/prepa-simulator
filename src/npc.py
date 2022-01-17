#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import externe
import pygame as pg

"""Gère les NPC du jeu"""


class NpcManager():
    """Gère le chargement des NPC et le déclenchement des dialogues"""
    def __init__(self, map):
        # Objet associé
        self.map = map

        # Liste les NPC chargés
        self.npc_group = pg.sprite.Group()

        # Chargement de tous les NPC de la carte
        npcs = self.map.game.game_data_db.execute("SELECT npc.id, npc.nom, x_coord, y_coord, default_dia, script_id, sprite FROM npc JOIN maps ON npc.map_id = maps.id WHERE maps.id = ?", (map.map_id,)).fetchall()
        for npc in npcs:
            new_npc = Npc(map, npc[0], npc[1], (npc[2], npc[3]), npc[4], npc[5], npc[6])
            self.npc_group.add(new_npc)
            self.map.object_group.add(new_npc)

    def check_talk(self):
        """Démarre le dialogue avec un NPC proche"""
        npc_collide_list = pg.sprite.spritecollide(self.map.game.player, self.npc_group, False)
        if len(npc_collide_list) > 0:
            first_npc = npc_collide_list[0]
            if self.map.game.running_script is None: # Empêche le joueur d'exécuter deux fois le même script
                self.map.game.script_manager.execute_script(first_npc.script, first_npc)


class Npc(pg.sprite.Sprite):
    """Représente un NPC"""

    DEFAULT_SPRITESHEET_LOC = 'res/textures/player.png'

    def __init__(self, map, id, name, coords, default_dia, script_id, sprite = None):
        super().__init__()

        # Objet associé
        self.map = map

        # Variables d'état
        self.id = id
        self.name = name
        self.default_dia = default_dia
        if script_id is not None:
            self.script = self.map.game.script_manager.get_script_from_id(script_id)
        else:
            self.script = self.map.game.script_manager.find_script_from_name("ordinaryNpc") # Temporaire, tous les NPC disposent du script dummyScript
        print(self.script.name)
        self.flags = [False, False] # TEMPORAIRE Jeu de deux drapeaux pour chaque NPC, à élargir si besoin
                                    # TODO Sauvegarder l'état des flags à chaque interaction et lorsqu'on quitte le jeu

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

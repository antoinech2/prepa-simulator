#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Gère le joueur"""

import pygame as pg

import debug
import save

class Player(pg.sprite.Sprite):
    """Représente le joueur"""

    TEXTURE_FILE_LOCATION = 'res/textures/m2.png'

    SPEED_NORMALISATION = 1/(2**0.5)
    SPRINT_WALK_SPEED_MULTIPLIER = 8 # Multiplicateur de vitesse en cas de sprint
    WALK_ANIMATION_COOLDOWN = 8 # Cooldown entre deux changements d'animations (en frames)
    SPRINT_ANIMATION_COOLDOWN = 3 # Cooldown entre deux changements d'animations (en frames)

    FEET_SIZE = 12 # Hauteur de la zone de collision (en pixels)

    ANIMATION_DICT = {
    "1,1" : "down-right",
    "1,0" : "right",
    "0,1" : "down",
    "1,-1" : "up-right",
    "0,-1" : "up",
    "-1,1" : "down-left",
    "-1,0" : "left",
    "-1,-1" : "up-left"}

    def __init__(self, game):
        super().__init__()
        self.game = game

        # Variables d'état
        self.is_animated = False        # Le sprite du joueur défile
        self.is_sprinting = False       # Le joueur sprinte
        self.is_warping = False         # Le joueur se téléporte
        self.can_move = True            # Le joueur est capable de bouger
        self.boop = False               # Le joueur est en collision

        # Chargement de la position dans la sauvegarde
        config = save.load_config("entities")["player"]
        self.position = config["position"]
        self.base_walk_speed = config["speed"] # Vitesse du joueur sans multiplicateur (en pixel/frame)

        # Graphique
        self.drawing_layer = 1
        self.sprite_sheet = pg.image.load(self.TEXTURE_FILE_LOCATION)
        self.image = self.get_image(0, 0)  # en bas par défaut
        self.image.set_colorkey([0, 0, 0])  # transparence
        self.rect = self.image.get_rect()  # rectangle autour du joueur
        self.feet = pg.Rect(0, 0, self.rect.width * 0.5, self.FEET_SIZE)
        self.current_sprite = 0

        self.IMAGES = {
        'down': [self.get_image(0, 0), self.get_image(32, 0), self.get_image(64, 0)],
        'down-left': [self.get_image(0, 0), self.get_image(32, 0), self.get_image(64, 0)],
        'down-right': [self.get_image(0, 0), self.get_image(32, 0), self.get_image(64, 0)],
        'left': [self.get_image(0, 32), self.get_image(32, 32), self.get_image(64, 32)],
        'right': [self.get_image(0, 64), self.get_image(32, 64), self.get_image(64, 64)],
        'up': [self.get_image(0, 96), self.get_image(32, 96), self.get_image(64, 96)],
        'up-left': [self.get_image(0, 96), self.get_image(32, 96), self.get_image(64, 96)],
        'up-right': [self.get_image(0, 96), self.get_image(32, 96), self.get_image(64, 96)]
        }

    def save(self):
        """Sauvegarde lors de la fermeture du jeu"""
        save.save_config("entities", player = dict(map_id = self.game.map_manager.map_id, position = self.position, speed = self.base_walk_speed))

    def change_animation(self, direction):  # change l'image en fonction du sens 'sens'
        """Change l'image de l'animation du joueur"""
        animation = self.ANIMATION_DICT[str(direction[0])+","+str(direction[1])]
        self.image = self.IMAGES[animation][int(self.current_sprite)]
        self.image.set_colorkey([0, 0, 0])  # transparence

    def is_colliding(self):
        """Vérifie la collision avec un mur ou un portail"""
        # Collision avec un portail
        index = self.feet.collidelist(self.game.map_manager.portals)
        if index >= 0:   # Le joueur est dans un portail
            # On récupère l'endroit où téléporter le joueur
            [to_world, to_point] = self.game.game_data_db.execute("SELECT to_world, to_point FROM portals WHERE id = ?", (self.game.map_manager.portals_id[index],)).fetchall()[0]
            old_bgm = self.game.map_manager.sound_manager.music_file
            self.warp(to_world, to_point, old_bgm)
            self.is_warping = True
            return True
        else:
            # Collision avec les murs
            return True if self.feet.collidelist(self.game.map_manager.walls) > -1 else False
    
    def warp(self, map, coords, old_bgm):
        """Téléportation du joueur vers une nouvelle map"""
        transition_step = 5
        # On empêche le joueur de bouger pendant le warp
        self.can_move = False
        # Transition vers un écran noir
        fader = pg.Surface(self.game.window_size).convert()       # Fond noir initialement transparent
        fader.set_alpha(0)
        while fader.get_alpha() < 255:
            self.game.screen.blit(fader, (0, 0))
            fader.set_alpha(fader.get_alpha() + 2.2)              # L'opacité du fond noir est augmentée
            if self.game.debug:
                debug.show_debug_menu(self.game)                  # Conservation du menu de debug à l'écran
            pg.display.flip()
            pg.time.delay(transition_step)
        # Téléportation
        self.game.map_manager.load_map(map, old_bgm) # On charge la nouvelle carte
        self.game.map_manager.teleport_player(coords)  # on téléporte le joueur à la destination
        self.update()
        self.game.map_manager.draw()
        pg.display.flip()
    
    def end_warp(self):
        """Fin de la transition de warp"""
        transition_step = 1
        void = pg.Surface(self.game.window_size).convert()          # Fond noir initialement opaque
        void.set_alpha(255)
        bg = self.game.screen.convert()                             # Arrière-plan final
        bg.set_alpha(255)
        while void.get_alpha() > 0:
            self.game.map_manager.draw()
            self.game.screen.blit(bg, (0, 0))
            self.game.screen.blit(void, (0, 0))
            void.set_alpha(void.get_alpha() - 17)
            pg.display.flip()
            pg.time.delay(transition_step)
        

    def move(self, list_directions, sprinting):
        """Méthode de déplacement du joueur"""
        if list_directions.count(True) > 0: # Si au moins une touche de déplacement est préssée
            if self.can_move: # Le joueur n'est pas en dialogue
                self.boop = False # Le joueur a de nouveau bougé depuis la dernière collision
                speed_multiplier = self.SPRINT_WALK_SPEED_MULTIPLIER if sprinting else 1
                self.is_sprinting = True if sprinting else False

                # On calcule le déplacement potentiel en x et en y en fonction des touche préssées
                deplacement = [0, 0]
                if list_directions[0]: # Haut
                    deplacement[1] -= 1
                if list_directions[1]: # Droite
                    deplacement[0] += 1
                if list_directions[2]: # Bas
                    deplacement[1] += 1
                if list_directions[3]: # Gauche
                    deplacement[0] -= 1

                if deplacement[0] != 0 or deplacement[1] != 0: # Si le déplacement n'est pas nul

                    # Si le déplacement est non nul selon les deux coordonées, on se déplace en diagonale, il faut normaliser le vecteur déplacement
                    if deplacement[0] != 0 and deplacement[1] != 0:
                        speed_normalisation = self.SPEED_NORMALISATION
                    else:
                        speed_normalisation = 1

                    # On traite les deux coordonées x et y
                    for coord_id in [0, 1]:
                        # On déplace le sprite et on recalcule la position
                        self.position[coord_id] += deplacement[coord_id]*self.base_walk_speed*speed_multiplier*speed_normalisation
                        self.rect.topleft = self.position
                        self.feet.midbottom = self.rect.midbottom

                        # Si il y a collision, on annule le dernier déplacement
                        if self.is_colliding():
                            self.boop = True # Enregistrement de la collision
                            self.position[coord_id] -= deplacement[coord_id]*self.base_walk_speed*speed_multiplier*speed_normalisation
                            self.rect.topleft = self.position
                            self.feet.midbottom = self.rect.midbottom
                    else:
                        self.is_animated = True
                        self.change_animation(deplacement)
            else:
                self.is_animated = False

    def update(self):
        """Mise à jour graphique"""
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom

        # Recalcul de l'image à utiliser
        animation_cooldown = self.SPRINT_ANIMATION_COOLDOWN if self.is_sprinting else self.WALK_ANIMATION_COOLDOWN
        if self.is_animated == True:
            self.current_sprite = (int(self.game.internal_clock.ticks_since_epoch / animation_cooldown) % 3)
        if self.is_warping:
            self.end_warp()
            self.is_warping = False
            self.can_move = True

    def get_image(self, x, y):
        """Retourne une partie de l'image du joueur"""
        image = pg.Surface([32, 32])
        image.blit(self.sprite_sheet, (0, 0), (x, y, 32, 32))
        return image

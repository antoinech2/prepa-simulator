#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gère la classe primaire des entités du jeu, tels que le joueur et les NPC
"""
#? et des objets ? (ex : l'ordi de la Cave)

import pygame as pg

import save
import debug


class Entity(pg.sprite.Sprite):
    """Classe des objets mouvants comme le joueur et les PNJs"""
    # Constantes de mouvement
    SPEED_NORMA = 1/(2**0.5)        # Normalisation de la vitesse lors des mouvements en diagonale
    SPRINT_MULTIPLIER = 2.2           # Multiplicateur de la vitesse lors d'un sprint
    WALK_ANIMATION_COOLDOWN = 11     # Cooldown entre deux changements d'animations (en frames, marche)
    SPRINT_ANIMATION_COOLDOWN = 3   # Cooldown entre deux changements d'animations (en frames, sprint)

    # Constantes graphiques
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

    def __init__(self, game, id, texture = "m2"):
        super().__init__()

        # Relations avec les autres classes
        self.game = game

        # Variables graphiques
        self.spritesheet = pg.image.load(f"res/textures/{texture}.png")     # Fichier de textures
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
        self.drawing_layer = 1
        self.image = self.get_image(0, 0)  # en bas par défaut
        self.image.set_colorkey([0, 0, 0])  # transparence
        self.rect = self.image.get_rect()                                   # Hitbox du joueur
        self.feet = pg.Rect(0, 0, self.rect.width * 0.5, self.FEET_SIZE)
        self.current_sprite = 0

        # Variables d'état
        self.id = id
        self.is_animated = True         # Le sprite du joueur défile
        self.is_sprinting = False       # Le joueur sprinte
        self.can_move = True            # Le joueur est capable de bouger
        self.boop = False               # Le joueur est en collision

    def draw(self):
        """Dessine le sprite du personnage à l'écran"""
        self.game.screen.blit(self.image, self.rect)
    
    def get_image(self, x, y):
        """Retourne une partie de l'image du joueur"""
        image = pg.Surface([32, 32])
        image.blit(self.spritesheet, (0, 0), (x, y, 32, 32))
        return(image)

    def save(self):
        """Sauvegarde lors de la fermeture du jeu"""
        save.save_config("entities", player = dict(map_id = self.game.map_manager.map_id, position = self.position, speed = self.base_walk_speed, stamina = self.stamina, cash = self.cash))
    #TODO Sauvegarde des PNJs

    def update(self):
        """Mise à jour graphique"""
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom

        # Recalcul de l'image à utiliser
        animation_cooldown = self.SPRINT_ANIMATION_COOLDOWN if self.is_sprinting else self.WALK_ANIMATION_COOLDOWN
        if self.is_animated:
            self.current_sprite = (int(self.game.internal_clock.ticks_since_epoch / animation_cooldown) % 3)
        if self.id == "player":
            if self.is_warping:
                self.end_warp()
                self.is_warping = False
                self.can_move = True
    
    def change_animation(self, direction):  # change l'image en fonction du sens 'sens'
        """Change l'image de l'animation d'une entité"""
        animation = self.ANIMATION_DICT[str(direction[0])+","+str(direction[1])]
        self.image = self.IMAGES[animation][int(self.current_sprite)]
        self.image.set_colorkey([0, 0, 0])  # transparence

    def fix_direction(self, direction):
        """Fixe l'orientation d'une entité"""
        animation = self.ANIMATION_DICT[str(direction[0])+","+str(direction[1])]
        self.image = self.IMAGES[animation][1]
        self.image.set_colorkey([0, 0, 0])  # transparence


class Player(Entity):
    """Classe graphique du joueur"""
    MAX_ENERGY = 300

    def __init__(self, game, id, texture):
        super().__init__(game, id, texture)
        self.is_warping = False         # Le joueur se téléporte

        # Chargement de la position dans la sauvegarde
        config = save.load_config("entities")["player"]
        self.position = config["position"]
        self.base_walk_speed = config["speed"] # Vitesse du joueur sans multiplicateur (en pixel/frame)
        self.stamina = config["stamina"]       # énergie du joueur
        self.cash = config["cash"]
    
    def warp(self, map, coords, direction, old_bgm):
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
        self.game.script_manager.setdirection("player", direction) # On fait tourner le joueur
        self.update()
        self.game.map_manager.draw()
        self.game.map_manager.npc_manager.flip()
        self.game.movement_mem = [elem for elem in self.game.movement_mem if elem[0] == "player"]
        self.game.persistent_move = {}
        self.game.persistent_move_index = {}
        if "player" in self.game.moving_people:
            self.game.moving_people = {"player" : self.game.moving_people["player"]}
        else:
            self.game.moving_people = {}
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
    
    def is_colliding(self):
        """Vérifie la collision avec un mur ou un portail"""
        # Collision avec un portail
        index = self.feet.collidelist(self.game.map_manager.portals)
        if index >= 0:   # Le joueur est dans un portail
            # On récupère l'endroit où téléporter le joueur
            [to_world, to_point] = self.game.game_data_db.execute("SELECT to_world, to_point FROM portals WHERE id = ?", (self.game.map_manager.portals_id[index],)).fetchall()[0]
            try:
                direction = self.game.game_data_db.execute("select spawn_direction from Portals where id = ?", (self.game.map_manager.doors_id[index],)).fetchall()[0][0]
            except:
                direction = "up"    # Valeur par défaut
            old_bgm = self.game.map_manager.sound_manager.music_file
            self.warp(to_world, to_point, direction, old_bgm)
            self.is_warping = True
            return True
        else:
            # Collision avec les murs
            return True if self.feet.collidelist(self.game.map_manager.walls) > -1 else False
    
    def move(self, list_directions, sprinting):
        """Méthode de déplacement du joueur"""
        if list_directions.count(True) > 0: # Si au moins une touche de déplacement est préssée
            if self.can_move: # Le joueur n'est pas en dialogue
                self.boop = False # Le joueur a de nouveau bougé depuis la dernière collision
                speed_multiplier = self.SPRINT_MULTIPLIER if sprinting else 1
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
                        speed_normalisation = self.SPEED_NORMA
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
        else:
            self.is_sprinting = False # Le joueur est immobile


class Npc(Entity):
    """Classe des PNJs"""
    DEFAULT_SPRITESHEET = "m2"

    def __init__(self, map, id, name, coords, direction, script_id, sprite = None):
        self.base_walk_speed = 1.5          #! DEBUG

        if sprite is None:
            super().__init__(map.game, name, self.DEFAULT_SPRITESHEET)
        else:
            super().__init__(map.game, name, sprite)

        # Objet associé
        self.map = map

        # Variables d'état
        self.id = id
        self.name = name
        self.direction = direction if direction is not None else 180        # Direction par défaut
        if script_id is not None:
            self.script = self.map.game.script_manager.get_script_from_id(script_id)
        else:
            self.script = self.map.game.script_manager.find_script_from_name("ordinaryNpc") # Temporaire, tous les NPC disposent du script dummyScript

        # Graphique*
        if sprite == "void":    # Cas du NPC invisible
            self.image.set_alpha(0)
        else:
            self.image.set_colorkey([0, 0, 0])  # transparence
        self.rect.topleft = coords  # placement du npc

        self.position = list(coords)
    
    def is_colliding(self):
        """Vérifie la collision avec un mur ou un portail"""
        return True if self.feet.collidelist(self.game.map_manager.walls) > -1 else False

    def move(self, list_directions, sprinting):
        """Méthode de déplacement du joueur"""
        if list_directions.count(True) > 0: # Si au moins une touche de déplacement est préssée
            if self.can_move: # Le joueur n'est pas en dialogue
                self.boop = False # Le joueur a de nouveau bougé depuis la dernière collision
                speed_multiplier = self.SPRINT_MULTIPLIER if sprinting else 1
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
                        speed_normalisation = self.SPEED_NORMA
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

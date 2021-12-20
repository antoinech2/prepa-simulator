#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gestion des touches
"""

import pygame as pg
# TODO Passer le fichier en yaml lorsqu'on aura implémenté la possibilité de changer les touches

# Contrôle du mouvement
PLAYER_MOVE_UP = pg.K_UP
PLAYER_MOVE_DOWN = pg.K_DOWN
PLAYER_MOVE_LEFT = pg.K_LEFT
PLAYER_MOVE_RIGHT = pg.K_RIGHT
PLAYER_SPRINT = pg.K_LCTRL
PLAYER_SPRINT_SEC = pg.K_RCTRL

# Contrôle des mécanismes du jeu
ACTION_INTERACT = pg.K_SPACE

# Contrôle des menus
MENU_SHOW_SIDEBAR = pg.K_LSHIFT
MENU_MOVE_UP = pg.K_UP
MENU_MOVE_DOWN = pg.K_DOWN
MENU_MOVE_LEFT = pg.K_LEFT
MENU_MOVE_RIGHT = pg.K_RIGHT
MENU_INTERACT = pg.K_SPACE
MENU_CANCEL = pg.K_x

# Contrôle de la fenêtre
GAME_FULLSCREEN = pg.K_F11
GAME_TERMINATE = pg.K_ESCAPE
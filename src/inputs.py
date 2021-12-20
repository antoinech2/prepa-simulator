#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import externe
import pygame as pg

def handle_pressed_key(game):
    """Transmet toutes les touches préssées"""
    pressed = pg.key.get_pressed() # Récupération des touche préssées
    # On envoie le statut des 4 touches de déplacement pour être traité par le joueur
    game.player.move([pressed[pg.K_UP], pressed[pg.K_RIGHT], pressed[pg.K_DOWN], pressed[pg.K_LEFT]], pressed[pg.K_RCTRL] or pressed[pg.K_LCTRL])

def handle_key_down_event(game, event):
    """Transmet l'évènement d'une toucher qui vient d'être pressée"""
    if event.key == pg.K_SPACE:
        if game.dialogue == None:
            game.map_manager.npc_manager.check_talk() # Vérifie la présence d'un npc pour déclencher le nouveau dialogue
        else:
            game.dialogue.next_dialogue() # Passe au dialogue suivant
    elif event.key == pg.K_F11:
        game.change_window_size(fullscreen = (not game.is_fullscreen)) # Basculement du mode plein écran
    elif event.key == pg.K_ESCAPE:
        game.is_running = False # Fermeture du jeu


import pygame as pg
import controls as ctrl

def handle_pressed_key(game):
    """Transmet toutes les touches préssées"""
    pressed = pg.key.get_pressed() #Gestion des touches du clavier
    # On envoie le statut des 4 touches de déplacement pour être traité
    game.player.move([pressed[ctrl.PLAYER_MOVE_UP], pressed[ctrl.PLAYER_MOVE_RIGHT], pressed[ctrl.PLAYER_MOVE_DOWN], pressed[ctrl.PLAYER_MOVE_LEFT]], pressed[ctrl.PLAYER_SPRINT] or pressed[ctrl.PLAYER_SPRINT_SEC])

def handle_key_down_event(game, event):
    """Transmet l'évènement d'une toucher qui vient d'être pressée"""
    if event.key == ctrl.ACTION_INTERACT:  # si Espace est pressée
        if game.dialogue == None:
            game.map_manager.object_manager.pickup_check()
            game.map_manager.npc_manager.check_talk()
        else:
            game.dialogue.next_dialogue()
    elif event.key == ctrl.MENU_SHOW_SIDEBAR:
        game.menu_manager.toggle_sidemenu()
    elif event.key == ctrl.GAME_FULLSCREEN:
        game.change_window_size(fullscreen = (not game.is_fullscreen))
    elif event.key == ctrl.GAME_TERMINATE:
        game.is_running = False

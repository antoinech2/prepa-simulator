
import pygame as pg
import save

def init():
    global controls
    controls = save.load_config("controls")
    for cur_key in controls.keys():
        controls[cur_key] = pg.key.key_code(controls[cur_key])

def handle_pressed_key(game):
    """Transmet toutes les touches préssées"""
    pressed = pg.key.get_pressed() #Gestion des touches du clavier
    # On envoie le statut des 4 touches de déplacement pour être traité
    game.player.move([pressed[controls["PLAYER_MOVE_UP"]], pressed[controls["PLAYER_MOVE_RIGHT"]], pressed[controls["PLAYER_MOVE_DOWN"]], pressed[controls["PLAYER_MOVE_LEFT"]]], pressed[controls["PLAYER_SPRINT"]] or pressed[controls["PLAYER_SPRINT_SEC"]])

def handle_key_down_event(game, event):
    """Transmet l'évènement d'une toucher qui vient d'être pressée"""
    if event.key == controls["ACTION_INTERACT"] and not game.player.menu_is_open:  # si Espace est pressée
        if game.dialogue == None:
            game.map_manager.object_manager.pickup_check()
            game.map_manager.npc_manager.check_talk()
            game.menu_manager.sidemenu.bagmenu.refresh_groups() # Augmentation de la capacité affichée à l'écran de l'objet
        else:
            game.dialogue.next_dialogue()
    elif event.key == controls["MENU_SHOW_SIDEBAR"]:
        game.menu_manager.toggle_sidemenu()
    elif event.key == controls["MENU_INTERACT"] and game.player.menu_is_open:
        game.menu_manager.open_menu()
    elif event.key == controls["MENU_CANCEL"]:
        game.menu_manager.close_menu()
    elif event.key == controls["MENU_MOVE_UP"]:
        game.menu_manager.menu_move("up")
    elif event.key == controls["MENU_MOVE_DOWN"]:
        game.menu_manager.menu_move("down")
    elif event.key == controls["GAME_FULLSCREEN"]:
        game.change_window_size(fullscreen = (not game.is_fullscreen))
    elif event.key == controls["GAME_TERMINATE"]:
        game.is_running = False

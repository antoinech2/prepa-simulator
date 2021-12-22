
import pygame as pg

"""Affichage du menu de débug"""

FONT = "arial"
FONT_SIZE = 18

def show_debug_menu(game):
    text = "Debug menu (F3) \n\
    ==== GAME ==== \n\
Ticks : {}, Dialogue : {}\n\
    ==== Graphic ====   \n\
FPS : {} (expected {}), Tick time : {} ms,\n\
Effective tick time : {} ms,\n\
    ==== Player ====   \n\
World name : {}, World id : {}, \n\
Position : {}, Speed : {}, \n\
Animated : {}, Sprinting : {}, \n\
Talking : {}, Can Move : {}".format(game.tick_count, game.dialogue is not None, round(game.clock.get_fps(), 2), game.TICK_PER_SECOND, game.clock.get_time(), game.clock.get_rawtime(), game.map_manager.map_file, game.map_manager.map_id, [round(pos, 2) for pos in game.player.position], game.player.base_walk_speed * (game.player.SPRINT_WALK_SPEED_MULTIPLIER if game.player.is_sprinting else 1), game.player.is_animated, game.player.is_sprinting, game.player.is_talking, game.player.can_move)
    splited_text = text.split("\n")
    for (number, cur_text) in enumerate(splited_text):
        game.screen.blit(pg.font.SysFont(FONT, FONT_SIZE).render(cur_text, True, (255, 255, 255)), (0,number*(FONT_SIZE + 5)))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Gère les NPC du jeu"""

import pygame as pg
import dialogue

#Temporaire : liste des npc
NPC_LIST = [
        {"id" : 1, "map" : "carte", "coords" : (1500, 1200)},
        {"id" : 2, "map" : "carte", "coords" : (1500, 1300)},
        {"id" : 3, "map" : "carte", "coords" : (1500, 1400)}
        ]

class NpcManager():
    def __init__(self, map):
        self.npc_group = pg.sprite.Group()
        self.map = map

        #On charge les Npc de la map
        for npc in NPC_LIST:
            if npc["map"] == map.current_map:
                new_npc = Npc(map, npc["id"], npc["coords"],)
                self.npc_group.add(new_npc)
                self.map.get_group().add(new_npc)

    def check_talk(self):
        npc_collide_list = pg.sprite.spritecollide(self.map.game.player, self.npc_group, False)
        if len(npc_collide_list) != 0 and not npc_collide_list[0].is_moving:
            self.map.game.dialogue = dialogue.Dialogue(self.map.game, npc_collide_list[0])

    def tick(self):
        for npc in self.npc_group:
            npc.tick()


class Npc(pg.sprite.Sprite):
    TEXTURE_FILE_LOCATION = 'res/textures/player.png'

    def __init__(self, map, id, coords):
        super().__init__()
        self.map = map
        self.id = id
        self.is_moving = False
        self.position = coords
        self.vitesse = 2
        self.moving_list = []

        #Graphique
        self.sprite_sheet = pg.image.load(self.TEXTURE_FILE_LOCATION)
        self.image = pg.Surface([32, 32])  # creation d'une image
        self.image.set_colorkey([0, 0, 0])  # transparence
        self.rect = self.image.get_rect()  # rectangle autour du joueur
        self.rect.topleft = self.position  # placement du npc
        self.image.blit(self.sprite_sheet, (0, 0),
                        (0, 0, 32, 32))  # affichage du npc
        self.feet = pg.Rect(0, 0, self.rect.width * 0.5, 12)
        #temporaire
        if self.id == 1:
            self.points([(50,-50),(-50,0),(50,50),(-50,0)])
        elif self.id == 3:
            self.goto(1500,1300)
            self.goto(1500,1400)
            self.goto(1500,1300)
        else:
            self.points(self.make_cercle(1500,1300,50), relative = False)

    def make_cercle(self, x0, y0, R):
        bas = lambda x: (R**2 - (x-x0)**2)**0.5 + y0
        haut = lambda x: -(R**2 - (x-x0)**2)**0.5 + y0
        return [(x,round(bas(x))) for x in range(x0-R,x0+R+1)] + [(x,round(haut(x))) for x in range(x0+R,x0-R-1,-1)]


    def goto(self, x, y, x0 = None, y0 = None, relative = True):
        if x0 is not None:
            self.moving_list.append({"initx":x0, "inity":y0, "targetx":x, "targety":y, "relative":True})
        elif self.moving_list:
            self.moving_list.append({"initx":self.moving_list[-1].get("targetx"), "inity":self.moving_list[-1].get("targety"), "targetx":x, "targety":y, "relative":True})
        else:
            self.moving_list.append({"initx":self.position[0], "inity":self.position[1], "targetx":x, "targety":y, "relative":True})
        self.is_moving = True


    def avance(self):
        if self.boule_fermee((self.moving_list[0].get("targetx"),self.moving_list[0].get("targety")), 3, self.position):
            del self.moving_list[0]
            if not self.moving_list:
                self.is_moving = False
        else:
            xway = self.moving_list[0].get("targetx") - self.moving_list[0].get("initx")
            yway = self.moving_list[0].get("targety") - self.moving_list[0].get("inity")
            l = (xway**2 + yway**2)**(0.5)
            new_x = self.position[0] + self.vitesse*xway/l
            new_y = self.position[1] + self.vitesse*yway/l
            self.position = (new_x, new_y)
            self.rect.topleft = self.position


    def tick(self):
        if self.is_moving:
            self.avance()

    def boule_fermee(self,c,r,vect):
        return (vect[0] >= c[0]-r) and (vect[0] <= c[0]+r) and (vect[1] >= c[1]-r) and (vect[1] <= c[1]+r)

    def points(self, pts, relative = True, x0 = None, y0 = None):
        for i in range(len(pts)):
            if relative:
                a = self.position[0] + sum(pts[j][0] for j in range(i+1))
                b = self.position[1] + sum(pts[j][1] for j in range(i+1))
                c = a - pts[i][0]
                d = b - pts[i][1]
            else:
                a, b = pts[i]
                if i != 0:
                    c, d = pts[i-1]
                elif x0 is not None:
                    c, d = (x0, y0)
                else:
                    c, d = (None, None)
            self.goto(a, b, c, d)

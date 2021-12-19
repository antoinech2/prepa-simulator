#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#######################################
# Adapted from the pygame wiki:       #
# https://pygame.org/wiki/Spritesheet #
#######################################


# This class handles sprite sheets
# Note: When calling images_at the rect is the format:
# (x, y, x + offset, y + offset)


import pygame as pg

class SpriteSheet:
    def __init__(self, filename):
        try:
            self.sheet = pg.image.load(filename).convert()
        except pg.error:
                  print(f'Unable to load spritesheet image: {filename}')
                  raise SystemExit(pg.error)


    def image_at(self, rectangle, colorkey=None):
        """
        Load a specific image from a specific rectangle
        """
        rect = pg.Rect(rectangle)
        image = pg.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pg.RLEACCEL)
        return image


    def images_at(self, rects, colorkey=None):
        """
        Load a whole bunch of images and return them as a list
        """
        return [self.images_at(rect, colorkey) for rect in rects]


    def load_strip(self, rect, image_count, colorkey=None):
        """
        Load a whole strip of images, and return them as a list
        """
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)


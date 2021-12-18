#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gestion du Sac et de l'inventaire
"""

import objects

class Bag():

    def __init__(self):
        self.contents = {} # Temporaire
        self.object_count = len(self.contents)

    def pickup_object(self, object):
        if not object.id in self.contents:
            self.contents[object.id] = 1
        else:
            self.contents[object.id] += 1
        object.exists = False
        print(self.contents)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gestion du Sac et de l'inventaire
"""

import numpy as np

class Bag():
    """Classe du Sac du joueur"""
    def __init__(self, save):
        self.save_db = save
        data = np.array(self.save_db.cursor().execute("SELECT * FROM bag").fetchall())
        self.contents = dict(zip(data[:,0], data[:,1])) if data != [] else {}

    def pickup_object(self, mapobject):
        """Incrémentation de la quantité d'un objet lorsqu'il est ramassé"""
        self.increment_item(mapobject.parent.id, 1) # Augmentation de la quantité de 1
        mapobject.exists = False
    
    def increment_item(self, object_id, qty):
        """Incrémentation de la quantité d'un objet désigné par son identifiant"""
        if not object_id in self.contents:
            self.contents[object_id] = qty
        else:
            self.contents[object_id] += qty
        if self.contents[object_id] <= 0:
            self.contents[object_id] = 0     # Plus d'objets de ce type

    def save(self):
        """Sauvegarde le contenu du sac dans la base de données"""
        for item, count in self.contents.items():
            self.save_db.cursor().execute("INSERT OR REPLACE INTO bag VALUES (?, ?)", (int(item), int(count)))
        self.save_db.commit()

    def separate(self, interval):
        """Séparation du contenu du Sac en groupes (listes)"""
        print(self.contents)
        objects = list(self.contents.keys())
        amounts = list(self.contents.values())
        corrected_obj = []
        corrected_amt = []
        for obj in range(len(objects)):
            if amounts[obj] != 0:
                corrected_obj.append(objects[obj])
                corrected_amt.append(amounts[obj])
        objects, amounts = corrected_obj, corrected_amt
        groups = []
        current_group = []
        while objects != []:
            current_group.append((objects[0], amounts[0]))
            if len(current_group) >= interval:
                groups.append(current_group)
                current_group = []
            del(objects[0])
            del(amounts[0])
        if current_group != []:
            groups.append(current_group)
        return(groups)

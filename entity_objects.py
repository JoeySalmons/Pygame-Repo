'''
12/22/2022
entity_objects.py
Everything related to entities
'''

import pygame
import random
import numpy as np


# Define the entity class
# This is a base class for entities with inventories
class EntityWithInventory:
    def __init__(self, image, position, inventory):
        self.image = image
        self.position = position  # position on the map
        self.inventory = inventory
        self.width = 100  # pixels, used to scale the entity's image
        self.height = self.image.get_height() * self.width / self.image.get_width()

    # function to get height based on the image and desired width
    def get_height(self):
        pass

    # update function
    # for crafting and other things
    def update(self):
        # update the inventory
        # print("entity update")
        pass

    # bounding box for when the entity is on the map
    def bounding_box(self, camera_position):
        # bounding_box = pygame.Rect(x, y, w, h)
        # map_pos is not the correct position, need to subtract camera position
        x = self.position[0] - camera_position[0]
        y = self.position[1] - camera_position[1]
        return pygame.Rect(x, y, self.image.get_width(), self.image.get_height())

    # To render
    def render(self, window, camera_position):
        # make the image smaller
        desired_width = int(self.width)
        # width, height = self.image.get_size()
        # desired_height = int(height * desired_width / width)
        desired_height = int(self.height)
        smaller_image = pygame.transform.scale(self.image, (desired_width, desired_height))
        # Update position based on player position
        barr_x = self.position[0] - camera_position[0]
        barr_y = self.position[1] - camera_position[1]
        window.blit(smaller_image, (barr_x, barr_y))

    # render the inventory
    # using the inventory render(self, surface, screen_size) function
    def render_inventory(self, window, screen_size):
        self.inventory.render(window, screen_size)


# Define the crafting entity class
# This uses the entity class as a base class
class CraftingEntity(EntityWithInventory):
    def __init__(self, image, position, inventory):
        super().__init__(image, position, inventory)
        self.can_craft = False  # boolean, whether the entity can craft or not
        # player inventories, chests, etc. will have this set to False
        # crafting tables, smelters, etc. will have this set to True
        self.is_crafting = False  # boolean, whether the entity is crafting or not
        self.crafting_timer = 100  # frames

    # crafting function
    def craft(self):
        # in order to craft, the entity must have the correct items
        # in the correct order. The items are removed from the inventory
        # and the crafted item is added to the inventory

        pass

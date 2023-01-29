'''
12/20/22
Items.py
Everything related to items
'''

import pygame
import os
import random
import numpy as np


# Define the item class
class Item:
    def __init__(self, name, image, description, item_rarity, item_type, type_name, value, in_inventory, map_position, screen_position, in_hand, player):
        self.name = name
        self.image = image  # square image
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.image_scale = 50  # pixels, what the image should be scaled to when in the inventory or being held
        self.description = description
        self.item_rarity = item_rarity
        self.item_type = item_type
        self.type_name = type_name
        self.value = value
        self.in_inventory = in_inventory  # True if the item is in an inventory, False if it is on the map
        self.map_position = map_position  # for when the item is on the map and not in the inventory
        self.screen_position = screen_position # for when the item is in the inventory or being moved (in the player's hand)
        self.in_hand = in_hand  # True if the item is being moved (in the player's hand), False if it is in the inventory or on the map
        self.player = player  # the player, to get their position

    # function to get the screen position of the item from the map position and player position
    def get_screen_pos(self, player_position):
        # get the screen position of the item, assuming the map position is accurate
        # this is the top left corner of the item that is drawn on the screen
        # get the screen size
        screen_size = np.array(pygame.display.get_surface().get_size())
        cam_pos = player_position - screen_size / 2
        screen_position = self.map_position - cam_pos
        # print("screen_size: ", screen_size)
        # print("cam_pos: ", cam_pos)
        # print("screen_position: ", screen_position)
        return screen_position

    # function to get the map position of the item from the screen position and player position
    def get_map_pos(self, player_position):
        # get the map position of the item, assuming the screen position is accurate
        # this is the top left corner of the item that is drawn on the map
        # get the screen size
        screen_size = np.array(pygame.display.get_surface().get_size())
        cam_pos = player_position - screen_size / 2
        map_position = self.screen_position + cam_pos
        return map_position

    # bounding box for when the item is on the map
    def bounding_box(self, camera_position):
        # bounding_box = pygame.Rect(x, y, w, h)
        # map_pos is not the correct position, need to subtract camera position
        x = self.map_position[0] - camera_position[0]
        y = self.map_position[1] - camera_position[1]
        return pygame.Rect(x, y, self.image.get_width(), self.image.get_height())

    # bounding box for when the item is in the inventory
    def bounding_box_inventory(self, player_position):
        # it should be in the inventory, so the position is the screen position
        # the image is 50x50, so the bounding box is 50x50 (by default)
        screen_pos = self.get_screen_pos(player_position)
        return pygame.Rect(screen_pos[0], screen_pos[1], self.image_scale, self.image_scale)

    # bounding box for when the item is in the player inventory
    # called when clicking in the player inventory
    def bounding_box_player_inventory(self):
        # it should be in the inventory, so the position is the screen position
        # the image is 50x50, so the bounding box is 50x50 (by default)
        screen_pos = self.screen_position
        return pygame.Rect(screen_pos[0], screen_pos[1], self.image_scale, self.image_scale)

    # To render on the map, when not in the inventory or being held
    def render_on_map(self, window, camera_position):
        # Update position based on player position
        barr_x = self.map_position[0] - camera_position[0]
        barr_y = self.map_position[1] - camera_position[1]
        window.blit(self.image, (barr_x, barr_y))

    # To render on the screen, when in the inventory or being held
    def render_on_screen(self, window, position, being_held):
        # position is the top left corner of the item slot in the inventory,
        # make the image smaller
        smaller_image = pygame.transform.scale(self.image, (self.image_scale, self.image_scale))
        # Update position based on position plus offset if being held
        if being_held:
            self.screen_position = position - np.array([self.image_scale/2, self.image_scale/2])
            window.blit(smaller_image, (self.screen_position[0], self.screen_position[1]))
        else:
            window.blit(smaller_image, (position[0], position[1]))

# Item rarities
rarity = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]

# item values dictionary
item_values = {
    "Common": [1, 2, 4],
    "Uncommon": [5, 6, 8],
    "Rare": [10, 15],
    "Epic": [20, 25],
    "Legendary": [30, 40],
    "Mythic": [50, 75, 100]
}

# Item types
types = ["Weapon", "Armor", "Consumable", "Resource", "Miscellaneous"]

# Item type names dictionary
item_type_names = {
    "Weapon": ["Sword", "Axe"],
    "Armor": ["Helmet"],
    "Consumable": ["Potion"],
    "Resource": ["Wood", "Stone"],
    "Miscellaneous": ["Statue"]
}

# Item type names - unused
weapon_names = ["Sword", "Axe"]
armor_names = ["Helmet"]
consumable_names = ["Potion"]
resource_names = ["Wood", "Stone"]
miscellaneous_names = ["Statue"]

'''
# items that might get used in the future
weapon_names = ["Sword", "Axe", "Bow", "Staff", "Dagger", "Spear", "Mace", "Wand", "Scythe", "Fist"]
armor_names = ["Helmet", "Chestplate", "Leggings", "Boots", "Gloves", "Shield"]
consumable_names = ["Potion", "Scroll", "Food", "Herb", "Elixir"]
resource_names = ["Wood", "Stone", "Metal", "Leather", "Cloth", "Bone", "Crystal", "Jewel", "Oil", "Gems"]
miscellaneous_names = ["Statue", "Key", "Coin", "Gem", "Book", "Scroll", "Map", "Artifact", "Relic", "Trophy", "Token"]
'''


# function to get an image given the item type
# each folder in the \images\items folder is a type (ex. armor, weapons, etc.)
def get_item_image(item_type, type_name):
    # item_type is a string, equal to the item type (ex. "armor", "weapon", etc.)
    # type_name is a string, equal to the item type name (ex. "sword", "helmet", etc.)

    # set the names to lowercase
    item_type = item_type.lower()
    type_name = type_name.lower()

    # get the path to the folder
    path = os.path.join('images', 'items', item_type, type_name)
    # get a list of all the files in the folder
    files = os.listdir(path)
    # get a random file from the list
    file = random.choice(files)
    # get the path to the file
    path = os.path.join('images', 'items', item_type, type_name, file)
    # load the image and return it
    return pygame.image.load(path)


# Define a function to create a random item
def create_rand_item(in_inventory, map_position, player):
    # in_inventory is a boolean, True if the item is in the player's inventory, False if it is on the map
    # map_position is a tuple, the position of the item on the map (x, y) used when not in the inventory
    # parameters for the item class:
    # name, image, description, item_rarity, item_type, type_name, value, in_inventory, map_position, screen_position, in_hand

    # get a random rarity
    item_rarity = random.choice(rarity)

    # get a random item type:
    item_type = random.choice(types)
    # Retrieve the list of names based on the item type
    type_names_list = item_type_names.get(item_type)
    # choose a random name from the list
    type_name = random.choice(type_names_list)

    # name the item
    name = str(item_rarity) + " " + str(item_type) + " " + str(type_name)
    # set item description based on rarity, type, and type name
    description = "This is a " + str(item_rarity) + " " + str(item_type) + " " + str(type_name) + "."

    # load the image
    item_image = get_item_image(item_type, type_name)
    # Set the desired size for the image
    new_width, new_height = 100, 100
    new_size = (new_width, new_height)
    # Resize the image
    resized_image = pygame.transform.scale(item_image, new_size)

    # set the value of the item
    value = random.choice(item_values.get(item_rarity))

    # Create the item
    # params: name, image, description, item_rarity, item_type, type_name, value, in_inventory, map_position, screen_position, in_hand, player
    item = Item(name, resized_image, description, item_rarity, item_type, type_name, value, in_inventory, map_position,
                (0, 0), False, player)
    # Return the item
    return item


# function to create a specific item (image will be randomly chosen based on the item type and type name)
def create_item(in_inventory=False, map_position=(0, 0), name="", description="", rarity="common", item_type="Miscellaneous", type_name="Statue", value=1):
    # if name is empty, create the name using the rarity, type, and type name
    if name == "":
        name = str(rarity) + " " + str(item_type) + " " + str(type_name)
    # if description is empty, set it to "A statue item"
    if description == "":
        description = "A statue item"

    # load the image
    item_image = get_item_image(item_type, type_name)
    # Set the desired size for the image
    new_width, new_height = 100, 100
    new_size = (new_width, new_height)
    # Resize the image
    resized_image = pygame.transform.scale(item_image, new_size)

    # Create the item
    # need the following parameters:
    # name, image, description, item_rarity, item_type, type_name, value, in_inventory, map_position, screen_position, in_hand
    item = Item(name, resized_image, description, rarity, item_type, type_name, value, in_inventory, map_position, (0, 0), False)
    # Return the item
    return item


if __name__ == "__main__":
    # Define the item dict
    items = {}

    # Create a bunch of items
    for i in range(10):
        # Create an item
        item = create_rand_item(False, (0, 0), None)
        # Add the item to the item dict
        items[item.name] = item

    print("Items.py loaded")
    for item in items:
        print("Item:", item, "created")
        print(items[item].name)
        print(items[item].description)
        print("Rarity:", items[item].item_rarity)
        print(items[item].item_type)
        print(items[item].value)

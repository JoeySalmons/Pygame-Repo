'''
12/22/2022
Inventories.py
This file has classes for inventories
'''

# imports, imports, imports (and more imports)
import numpy as np
import pygame


# Define the inventory class for objects with an inventory
class ObjectInventory:
    def __init__(self, screen_size, contents, is_open, map_position, player):
        self.screen_size = screen_size  # numpy array, x and y, screen size
        self.contents = contents  # numpy array of items (x by y, each element is an item)
        self.is_open = is_open  # boolean, whether the inventory is open or not
        self.map_position = map_position  # numpy array, top left corner of the inventory relative to the map
        self.player = player  # the player object, to get the player's position
        self.border_width = 5  # width of the border around the inventory
        self.slot_size = 55  # size of each slot in the inventory
        self.slot_spacing = 10  # spacing between each slot in the inventory
        self.slot_border_width = 5  # width of the border around each slot in the inventory (drawn around each slot)
        self.bottom_right_corner = self.get_bottom_right_corner()  # numpy array, bottom right corner of the inventory

    # function to get the screen position of the inventory
    def get_screen_pos(self):
        # get the screen position of the inventory
        # this is the top left corner of the inventory that is drawn on the screen
        camera_position = self.player.position - self.screen_size / 2
        screen_position = self.map_position - camera_position
        return screen_position

    # function to get the bottom right corner of the inventory, based on the size of the inventory
    def get_bottom_right_corner(self):
        # get the bottom right corner of the inventory
        # this is used to draw the inventory
        # each x/y slot is self.slot_size + self.slot_spacing pixels wide/tall
        # top left corner is screen_position
        screen_position = self.get_screen_pos()
        x_corner = screen_position[0] + 2*self.border_width + self.contents.shape[0] * (self.slot_size + self.slot_spacing) - self.slot_spacing
        y_corner = screen_position[1] + 2*self.border_width + self.contents.shape[1] * (self.slot_size + self.slot_spacing) - self.slot_spacing
        corner = np.array([x_corner, y_corner])
        return corner

    # function to output the coords of the corner of a given inventory slot
    def get_slot_coords(self, x, y):
        screen_position = self.get_screen_pos()
        # x and y are the slot coordinates
        x_corner = screen_position[0] + self.border_width + x * (self.slot_size + self.slot_spacing)
        y_corner = screen_position[1] + self.border_width + y * (self.slot_size + self.slot_spacing)
        return x_corner, y_corner

    # function to check if the mouse is over the inventory
    def mouse_over(self, mouse_position):
        screen_position = self.get_screen_pos()
        bottom_right_corner = self.get_bottom_right_corner()
        # check if the mouse is over the inventory
        if screen_position[0] < mouse_position[0] < bottom_right_corner[0]:
            if screen_position[1] < mouse_position[1] < bottom_right_corner[1]:
                return True
        return False

    # function to calculate the number of items in the inventory
    def num_items(self):
        # calculate the number of items in the inventory
        num = 0
        for i in range(self.contents.shape[0]):
            for j in range(self.contents.shape[1]):
                if self.contents[i, j] is not None:
                    num += 1
        return num

    # function to find an empty slot in the inventory
    def find_empty_slot(self):
        # find an empty slot in the inventory
        for i in range(self.contents.shape[0]):
            for j in range(self.contents.shape[1]):
                if self.contents[i, j] is None:
                    return i, j
        return None, None  # if there are no empty slots

    # item to hand function
    def item_to_hand(self, item, player, mouse_position):
        # this is called when moving an item from the inventory to the player's hand
        # it updates the item's variables and the player's variables
        # find the item position in the inventory, then set the item in the inventory to None
        for i in range(self.contents.shape[0]):
            for j in range(self.contents.shape[1]):
                if self.contents[i, j] == item:
                    self.contents[i, j] = None
                    # print("Item removed: ", item)
                    # print("Inventory contents: ", self.contents)
        item.in_hand = True
        item.in_inventory = False
        player.item_in_hand = item
        # set the item's screen position to the player's hand position
        item.screen_position = mouse_position

    # function to place an item into the inventory
    def place_item(self, item, mouse_pos, player):
        # This is running because the mouse button has been released and it is in the inventory
        print("RUNNING PLACE ITEM")

        # first drop the item to the ground (this will get overwritten if the item is placed in the inventory)
        # second, try to place the item in the inventory slot that the mouse is over
        # if that slot is full, try to place it in any empty slot

        # the item will always not be in the player's hand after this point
        item.in_hand = False
        player.item_in_hand = None
        # by default, drop the item to the map at the player's position
        item.in_inventory = False
        item.map_position = player.position.copy()

        # check if the mouse is over a slot to place the item
        # get the number of slots in the inventory
        x_slots = len(self.contents)
        y_slots = len(self.contents[0])
        # loop through the slots
        for x in range(x_slots):
            for y in range(y_slots):
                # get the x and y coordinates of the slot
                x_corner, y_corner = self.get_slot_coords(x, y)
                # check if the mouse is over the slot
                padding = 1  # padding to make the slot easier to drop items into
                if x_corner - padding < mouse_pos[0] < x_corner + self.slot_size + padding:
                    if y_corner - padding < mouse_pos[1] < y_corner + self.slot_size + padding:
                        # if the slot is empty, put the item in the slot
                        if self.contents[x][y] is None:
                            self.contents[x][y] = item
                            item.in_inventory = True
                            # update the item's screen and map position
                            item.screen_position = np.array([x_corner, y_corner])
                            item.map_position = item.get_map_pos(player.position)
                            break
                        # if the slot is not empty, try putting the item in an empty slot
                        else:
                            # find an empty slot
                            empty_x, empty_y = self.find_empty_slot()
                            # put the item in the empty slot (if inventory is full, item should already be dropped)
                            if empty_x is not None:
                                self.contents[empty_x][empty_y] = item
                                item.in_inventory = True
                                empty_x_corner, empty_y_corner = self.get_slot_coords(empty_x, empty_y)
                                item.screen_position = np.array([empty_x_corner, empty_y_corner])
                                # update the item's screen and map position
                                item.map_position = item.get_map_pos(player.position)
                                break
                            else:
                                print("Inventory full, no empty slot found to place item, dropping item to ground")

    def render(self, surface):
        # Draw the inventory and its slots on the given surface
        # default color scheme
        background_color = (255, 255, 255)
        border_color = (0, 150, 0)
        slot_border_color = (250, 180, 0)
        item_slot_color = (0, 100, 0)

        # Draw the inventory
        # draw a rectangle for the background
        #   pygame.draw.rect takes in the following arguments: surface, color, (top_left x y, bottom_right x y, width)
        top_left = self.get_screen_pos()
        bottom_right = self.get_bottom_right_corner()
        relative_width = bottom_right[0] - top_left[0]
        relative_height = bottom_right[1] - top_left[1]
        pygame.draw.rect(surface, background_color, (top_left[0], top_left[1], relative_width, relative_height))
        # draw a rectangle for the border
        pygame.draw.rect(surface, border_color, (top_left[0], top_left[1], relative_width, relative_height), self.border_width)

        # Draw the slots
        # get the number of slots in the inventory
        x_slots = len(self.contents)
        y_slots = len(self.contents[0])
        # loop through the slots
        for x in range(x_slots):
            for y in range(y_slots):
                # get the x and y coordinates of the slot
                x_corner, y_corner = self.get_slot_coords(x, y)
                # draw a rectangle for the slot
                pygame.draw.rect(surface, item_slot_color, (x_corner, y_corner, self.slot_size, self.slot_size))
                # slot border
                pygame.draw.rect(surface, slot_border_color, (x_corner, y_corner, self.slot_size, self.slot_size), self.slot_border_width)

                # draw the item in the slot
                if self.contents[x][y] is not None:
                    # item method render_on_screen(self, window, position, being_held):
                    self.contents[x][y].render_on_screen(surface, np.array([x_corner, y_corner]), False)


### NEW PLAYER INVENTORY CODE ###
# the following changes are made to the new player inventory class:
# the screen position of the inventory is now static (so no map_position)
#   this means the top left corner of the inventory is always at (0, screen_size[1] - 150)
#   and the bottom right corner will also be static, based on the size of the inventory

# Define the inventory class for the player
# Uses the ObjectInventory class as a base
class PlayerInventory(ObjectInventory):
    def __init__(self, screen_size, contents, player):
        self.screen_position = np.array([0, screen_size[1] - 130]) # top left corner of the inventory on the screen
        super().__init__(screen_size, contents, False, (0, 0), player)

    # override the get_screen_pos method
    ## previous method ##
    # def get_screen_pos(self):
    #     # get the screen position of the inventory
    #     # this is the top left corner of the inventory that is drawn on the screen
    #     camera_position = self.player.position - self.screen_size / 2
    #     screen_position = self.map_position - camera_position
    #     return screen_position
    ## new method ##
    def get_screen_pos(self):
        # get the position of the top left corner of the player's inventory
        # the inventory is positioned in the bottom left corner of the screen
        return self.screen_position

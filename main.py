'''
project started 12/17/2022
main.py
This game is a top-down RPG game.
The player will be able to move around the map and interact with objects and NPCs.
'''

# imports, imports, imports (and more imports)
import time
import numpy as np
import random
import math
import pygame
import sys
import os

# game file imports
from Items import *
from Inventories import *
from entity_objects import *


# Define the player class
class Player:
    def __init__(self, position, velocity, max_velocity, size, color, item_in_hand):
        self.position = position # x and y, numpy array
        self.velocity = velocity # x and y current velocity
        self.max_velocity = max_velocity # max velocity
        self.size = size # radius (pixels)
        self.color = color # color (RGB)
        self.item_in_hand = item_in_hand # item in hand, None if nothing

    def update(self):
        # Update the player's position based on their velocity
        self.position += self.velocity

    def render(self, surface, screen_size):
        # Draw the player on the given surface
        # pygame.draw.circle(surface, self.color, (int(self.position[0]), int(self.position[1])), self.size)
        pygame.draw.circle(surface, self.color, (int(screen_size[0]/2), int(screen_size[1]/2)), self.size)
        pass

    # drop an item in the player's hand to the map
    # converts screen to map_position and updates variables
    def drop_item_to_map(self, mouse_position, game_wrld):
        # Drop the item in the player's hand
        item = self.item_in_hand
        self.item_in_hand = None
        # update the item's map position with an offset based on the size of the item's image
        item.map_position = game_wrld.screen_to_map(mouse_position) - np.array([item.image.get_width()/2, item.image.get_height()/2])
        item.in_hand = False
        item.in_inventory = False


# class for an orbiting object around an entity
# Define the Orbiter class
class Orbiter:
    def __init__(self, size, radius, speed, color):
        self.size = size # size of orbiter (pixels)
        self.radius = radius
        self.speed = speed # speed of rotation
        self.color = color # color (RGB)
        self.angle = 0  # Initialize the angle to 0

    def update(self):
        # Update the angle based on the speed
        self.angle += self.speed

    def render(self, surface, center):
        # Draw the Orbiter on the given surface
        x = center[0] + math.cos(self.angle) * self.radius
        y = center[1] + math.sin(self.angle) * self.radius
        pygame.draw.circle(surface, self.color, (int(x), int(y)), self.size)


# Define the barrier class
# these don't move, and currently act only as part of the background
class Barrier:
    def __init__(self, position, size, shape, color):
        self.position = position # x and y, numpy array
        self.size = size
        self.shape = shape # 0 = circle, 1 = square
        self.color = color

    def render(self, surface, player_position):
        # Draw the barrier on the given surface
        # Update position based on player position
        barr_x = self.position[0] - player_position[0]
        barr_y = self.position[1] - player_position[1]
        if self.shape == 0:
            pygame.draw.circle(surface, self.color, (int(barr_x), int(barr_y)), 10)
        if self.shape == 1:
            pygame.draw.rect(surface, self.color, (int(barr_x), int(barr_y), self.size, self.size))


# Define the game stats class
class GameStats:
    def __init__(self, screen_size, size):
        self.screen_size = screen_size # numpy array of the display screen size
        self.size = size # numpy array of the game map size, unused
        self.score = 0 # unused
        self.drawing = False # boolean, whether drawing barriers with mouse is enabled
        self.mouse_button_released = True # boolean, whether the mouse button is released


# Define the game world class
class GameWorld:
    def __init__(self, game_stats, player, entities, barriers, player_inventory, world_inventories, items):
        self.screen_size = game_stats.screen_size # display size (pixels, x by y, numpy array)
        self.size = game_stats.size # game world dimensions (pixels, x by y)
        self.player = player
        self.entities = entities # list of entities
        self.barriers = barriers # list of barriers
        self.player_inventory = player_inventory # player's inventory, only one of these exists
        self.world_inventories = world_inventories # list of inventories on the map (not including player's inventory)
        self.items = items

    def update(self):
        # Update the player and entities
        self.player.update()
        for entity in self.entities:
            entity.update()
        # Update the orbiting object
        orbiter.update()

    def check_if_on_screen(self, position, object_width=0, object_height=0):
        # object_width and height correspond to the object's image
        # update the position by half of the object image width and height
        position = position + np.array([object_width, object_height]) / 2
        # Check if the given position is on the screen
        # position is a numpy array
        if self.player.position[0] - self.screen_size[0] / 2 < position[0] < self.player.position[0] + self.screen_size[0] / 2:
            if self.player.position[1] - self.screen_size[1] / 2 < position[1] < self.player.position[1] + self.screen_size[1] / 2:
                return True
        return False

    # function to convert screen coords to map coords
    def screen_to_map(self, screen_position):
        # position is a numpy array
        return screen_position + self.player.position - self.screen_size / 2

    # function to make a list of items in an inventory
    def get_inventory_items(self, inventory):
        # get the number of slots in the inventory
        x_slots = len(inventory.contents)
        y_slots = len(inventory.contents[0])
        # loop through the slots
        items_in_inventory = []
        for x in range(x_slots):
            for y in range(y_slots):
                # if the slot is not empty, add the item to the list
                if inventory.contents[x][y] is not None:
                    items_in_inventory.append(inventory.contents[x][y])
        return items_in_inventory

    # function to run whenever the mouse button is released
    def mouse_button_up(self, event):
        # Set the mouse_button_released variable to True
        game_stats.mouse_button_released = True
        # get the mouse position from event argument
        mouse_pos = event.pos

        # item stuff
        # get a list of all open inventories
        open_inventories = []
        for inventory in self.world_inventories:
            if inventory.is_open:
                open_inventories.append(inventory)
        if self.player_inventory.is_open:
            open_inventories.append(self.player_inventory)

        # if all inventories are closed
        if len(open_inventories) == 0:
            # and if the player is holding an item
            if self.player.item_in_hand is not None:
                # drop the item, passing in the mouse position and game world
                self.player.drop_item_to_map(event.pos, game_world)

        # there is an open inventory, so check if there is an item in the player's hand
        elif self.player.item_in_hand is not None:
            item_placed = False # boolean, whether the item has been put somewhere
            # we need to determine where the player is trying to put the item (inventory slot, map, etc.)
            # first, check if the player is trying to put the item in an inventory
            for inventory in open_inventories:
                # check if the mouse is in the inventory's bounding box
                if inventory.mouse_over(mouse_pos):
                    # run the inventory's place_item function
                    inventory.place_item(self.player.item_in_hand, mouse_pos, self.player)
                    item_placed = True
                # if the mouse is not in the inventory's bounding box, continue to the next inventory
                else:
                    continue
            # if the item has not been placed, drop it to the map
            if not item_placed:
                self.player.drop_item_to_map(event.pos, game_world)

    # function to run whenever the mouse button is pressed
    def mouse_button_down(self, event):
        # Set the mouse_button_released variable to False
        game_stats.mouse_button_released = False
        mouse_pos = event.pos
        mouse_x, mouse_y = mouse_pos

        # item stuff
        # get a list of all open inventories
        open_inventories = []
        for inventory in self.world_inventories:
            if inventory.is_open:
                open_inventories.append(inventory)
        if self.player_inventory.is_open:
            open_inventories.append(self.player_inventory)

        # get a list of all items on the map for when the mouse is not over an inventory
        items_on_screen = self.items_on_screen()

        # if there is an open inventory, check if the player is clicking on an item in the inventory
        mouse_over_inventory = False
        if len(open_inventories) > 0:
            for inventory in open_inventories:
                # check if the mouse is in the inventory's bounding box
                if inventory.mouse_over(mouse_pos):
                    mouse_over_inventory = True
                    print("mouse clicked over an inventory")
                    # make a list of items in the inventory
                    items_in_inventory = self.get_inventory_items(inventory)
                    # check if the player is clicking on an item in the inventory
                    for item1 in items_in_inventory:
                        # if this is not the player's inventory
                        if inventory is not self.player_inventory:
                            # check if the mouse is in the item's bounding box
                            if item1.bounding_box_inventory(player.position).collidepoint(mouse_x, mouse_y):
                                print("clicked on item in inventory")
                                # if so run the inventory's item to hand function:
                                inventory.item_to_hand(item1, self.player, mouse_pos)
                                # break out of the for loop
                                break
                        # if this is the player's inventory
                        else:
                            # check if the mouse is in the item's bounding box
                            if item1.bounding_box_player_inventory().collidepoint(mouse_x, mouse_y):
                                print("clicked on item in the player's inventory")
                                # if so run the inventory's item to hand function:
                                inventory.item_to_hand(item1, self.player, mouse_pos)
                                # break out of the for loop
                                break
                    # break out of the for loop
                    break
            # if the mouse is not over an inventory, check if the player is clicking on an item on the map
            if not mouse_over_inventory:
                # check if the player is clicking on an item on the map
                for item in items_on_screen:
                    # check if the mouse is in the item's bounding box
                    camera_position = self.get_camera_position()
                    if item.bounding_box(camera_position).collidepoint(mouse_x, mouse_y):
                        # if so, set the item to be in hand
                        item.in_hand = True
                        player.item_in_hand = item
                        # set the item's map_position to the mouse position
                        item.screen_position = np.array([mouse_x, mouse_y])
                        # break out of the for loop
                        break
        # if all inventories are closed
        else:
            # check if the player is clicking on an item on the map
            for item in items_on_screen:
                # check if the mouse is in the item's bounding box
                camera_position = self.get_camera_position()
                if item.bounding_box(camera_position).collidepoint(mouse_x, mouse_y):
                    # if so, set the item to be in hand
                    item.in_hand = True
                    player.item_in_hand = item
                    # set the item's map_position to the mouse position
                    item.screen_position = np.array([mouse_x, mouse_y])
                    # break out of the for loop
                    break

    # get a list of all items on the map that are also visible on the screen and not in an inventory
    def items_on_screen(self):
        items_on_screen = []
        # Check if any items on the map are also on the screen, then add them to the list
        for item in self.items:
            if self.check_if_on_screen(item.map_position):
                # and the item is not in an inventory
                if not item.in_inventory:
                    items_on_screen.append(item)
        return items_on_screen

    def get_camera_position(self):
        # Get the position of the camera
        # This is the position of the player's center
        return self.player.position - self.screen_size / 2

    # create a barrier
    def create_barrier(self, position, size, shape, color):
        # create a barrier object and add it to the list of barriers
        self.barriers.append(Barrier(position, size, shape, color))

    def render(self, surface):
        # Clear the screen by filling it with a solid color
        surface.fill((0, 0, 0))  # Fill with black color

        # Render the player on the given surface
        self.player.render(surface, screen_size)

        # first we want to make sure to only render what is visible on the screen
        camera_position = self.get_camera_position()
        # render the barriers
        for barrier in self.barriers:
            if self.check_if_on_screen(barrier.position):
                barrier.render(surface, camera_position)

        # render the entities
        for entity in self.entities:
            if self.check_if_on_screen(entity.position, entity.width, entity.height):
                entity.render(surface, camera_position)

        # Render the orbiting object
        orbiter.render(screen, screen_center)

        # Render the items on the map
        for item in self.items:
            # if its in hand don't render it
            if item.in_hand:
                continue
            # if it's not in and inventory and it's on the screen, render it
            elif not item.in_inventory and self.check_if_on_screen(item.map_position, item.width, item.height):
                item.render_on_map(surface, camera_position)

        # Render any other open inventories
        for inventory in self.world_inventories:
            if inventory.is_open:
                inventory.render(surface)

        # Render the player inventory
        if self.player_inventory.is_open:
            self.player_inventory.render(surface)

        # Render the item in hand, after rendering the inventory so it is on top
        item_in_hand = player.item_in_hand
        if item_in_hand is not None:
            item_in_hand.render_on_screen(surface, pygame.mouse.get_pos(), True)


# Set the window size and create a window
screen_size = np.array([800, 800])
screen_center = screen_size / 2
screen_center_x = screen_center[0]
screen_center_y = screen_center[1]

# initialize player at center of screen
player_position = screen_center.copy()
player_velocity = np.array([0.0, 0.0])
player_color = (190, 25, 190)
player_max_velocity = 5.0
player = Player(player_position, player_velocity, player_max_velocity, 10, player_color, None)

# initialize 100 barriers at random positions
num_barriers = 100
bar_max_x = 1000
bar_max_y = 1000
barriers = [Barrier(np.array([random.random()*bar_max_x, random.random()*bar_max_y]), 20, 1, (105, 190, 0)) for _ in range(num_barriers)]
#     def __init__(self, position, size, shape, color):

# initialize 10 red barriers on top side of map
red_barriers = [Barrier(np.array([i*100, 0]), 20, 1, (255, 0, 0)) for i in range(10)]
# add the red barriers to barriers list
barriers.extend(red_barriers)

# initialize player inventory
inventory_x_slots = 5
inventory_y_slots = 2
empty_inventory = np.empty((inventory_x_slots, inventory_y_slots), dtype=object)
# use the new PlayerInventory class: PlayerInventory(ObjectInventory)
#     def __init__(self, screen_size, contents, player):
#         super().__init__(screen_size, contents, False, (0, 0), player)
player_inventory = PlayerInventory(screen_size, empty_inventory, player)

# currently, adding items to the inventory at the start of the game
# does not work, so we will add them to the game world instead
# (items are by default created not in hand)
starting_items = []
# in_inventory = False, map_position = rand_x, rand_y both in range(0, 500)
first_item = create_rand_item(False, (50, 50), player)
starting_items.append(first_item)
# new_item = create_rand_item(False, (random.randint(0, 500), random.randint(0, 500)), player)
# starting_items.append(new_item)

# create some items on the map
for i in range(10):
    new_item = create_rand_item(False, (random.randint(0, 500), random.randint(0, 500)), player)
    starting_items.append(new_item)

# initialize game world inventories
start_world_inventories = []

# first test inventory using the class for objects with an inventory
# class ObjectInventory:
#     def __init__(self, screen_size, contents, is_open, map_position, player):
entity_position = np.array([100, 100])
test_inventory_x_slots = 1
test_inventory_y_slots = 1
empty_test_contents = np.empty((test_inventory_x_slots, test_inventory_y_slots), dtype=object)
test_inventory1 = ObjectInventory(screen_size, empty_test_contents.copy(), False, entity_position, player)
start_world_inventories.append(test_inventory1)

# make an entity to have the inventory using:
# class EntityWithInventory:
#     def __init__(self, image, position, inventory):
image_path = path = os.path.join('images', 'objects', 'smelter', 'furnace.png')
image = pygame.image.load(image_path)
test_entity1 = EntityWithInventory(image, entity_position, test_inventory1)

# second test inventory using the class for objects with an inventory
entity_position = np.array([500, 100])
test_inventory2 = ObjectInventory(screen_size, empty_test_contents.copy(), False, entity_position, player)
start_world_inventories.append(test_inventory2)

# make an entity to have the inventory
test_entity2 = EntityWithInventory(image, entity_position, test_inventory2)


# initialize game stats
map_dim = [900, 900]  # not used yet
game_stats = GameStats(screen_size, map_dim)

entities = [test_entity1, test_entity2]

# Initialize the game world with the player and entities
game_world = GameWorld(game_stats, player, entities, barriers, player_inventory, start_world_inventories, starting_items)


# initialize an orbiting object around the player
orbiter = Orbiter(10, 50, 0.1, (0, 50, 255))

# Initialize Pygame
pygame.init()

# Create a window
screen = pygame.display.set_mode(screen_size)

# Set the window title
pygame.display.set_caption("Game World")

# initial settings
mouse_button_released = True
drawing = False # for drawing barriers with mouse
frame_counter = 0
start_time = time.time()
current_time = start_time
current_frame = 0
update_print_rate = 1000 # how often to print the updates, in frames

# Create a clock object to control the frame rate
clock = pygame.time.Clock()

while True:  # Run the game loop
    frame_counter += 1

    # Limit the frame rate
    clock.tick(80)
    # Calculate the FPS
    fps = clock.get_fps()

    # print some info
    if not frame_counter % update_print_rate:
        # print some info about the game
        print("Player position: ", player.position)
        print("Frame: ", frame_counter)
        # print("Number of barriers: ", len(game_world.barriers))
        print("Time elapsed: ", time.time() - start_time, "seconds")
        if current_time - start_time > 0.5:
            print("Current FPS: ", (frame_counter - current_frame) / (time.time() - current_time))
        current_time = time.time()
        current_frame = frame_counter
        pass

    game_world.render(screen)  # screen is a pygame surface
    game_world.update()

    # Display the FPS on the screen
    fps_text = "FPS: {:.2f}".format(fps)
    font = pygame.font.SysFont("Arial", 20)
    text = font.render(fps_text, True, (155, 155, 255))
    screen.blit(text, (10, 10))

    # Events for if the mouse button is being pressed
    if not mouse_button_released:
        # Drawing on the screen with barriers if drawing is True
        if game_stats.drawing:
            # add a barrier to mouse position
            mouse_x, mouse_y = pygame.mouse.get_pos()
            rel_mouse_pos = np.array([mouse_x, mouse_y]) + game_world.player.position - np.array(screen_size) / 2
            # non random color
            # color = (105, 190, 0)
            # random color
            # color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            # color based on frame (rainbow)
            red = np.sin(frame_counter / 100) * 255
            green = np.sin(frame_counter / 100 + 2 * np.pi / 3) * 255
            blue = np.sin(frame_counter / 100 + 4 * np.pi / 3) * 255
            # make int and abs value
            color = (int(abs(red % 255)), int(abs(green)), int(abs(blue)))
            # Create a barrier if the mouse button is held down
            # position, size, shape, color
            game_world.create_barrier(rel_mouse_pos, 20, 1, color)

    # check keyboard and mouse events
    for event in pygame.event.get():  # Check for player input
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONUP:
            # run the game world event that handles mouse button up
            game_world.mouse_button_up(event)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Set the mouse_button_released variable to False
            mouse_button_released = False

            # Get the mouse position
            mouse_x, mouse_y = pygame.mouse.get_pos()
            print(f"Mouse clicked at position ({mouse_x}, {mouse_y})")

            game_world.mouse_button_down(event)

        # Keyboard press events for: player movement, inventory, and game world
        if event.type == pygame.KEYDOWN:
            # print some stats if "b" is pressed
            if event.key == pygame.K_b:
                # print the player inventory
                print("Player inventory: ", game_world.player_inventory.contents)
                # print items in player hand
                print("Items in player hand: ", game_world.player.item_in_hand)
                # mouse position
                mouse_x, mouse_y = pygame.mouse.get_pos()
                print(f"Mouse position ({mouse_x}, {mouse_y})")

            # if "v" is pressed, open the test entity inventory
            if event.key == pygame.K_v:
                for entity in game_world.entities:
                    if entity.inventory:
                        entity.inventory.is_open = not entity.inventory.is_open
                print("Test inventory is open")
            # Open the player inventory if the E key is pressed
            if event.key == pygame.K_e:
                # Open the player inventory if it is not already open
                game_world.player_inventory.is_open = not game_world.player_inventory.is_open

            velocity = player.max_velocity # for testing
            if event.key == pygame.K_w:
                player.velocity[1] = -velocity  # Move player up
            elif event.key == pygame.K_a:
                player.velocity[0] = -velocity  # Move player left
            elif event.key == pygame.K_s:
                player.velocity[1] = velocity  # Move player down
            elif event.key == pygame.K_d:
                player.velocity[0] = velocity  # Move player right
            # make sure the player doesn't move faster than their max velocity
            # print something if velocity in any direction is greater than max velocity
            if player.velocity[0] > player.max_velocity or player.velocity[0] < -player.max_velocity or player.velocity[1] > player.max_velocity or player.velocity[1] < -player.max_velocity:
                # print("Player is moving too fast!")
                pass

            # if the space bar is pressed reduce the player's velocity by 1/4
            if event.key == pygame.K_SPACE:
                player.velocity = player.velocity / 4
                pass

        elif event.type == pygame.KEYUP:

            if event.key == pygame.K_w or event.key == pygame.K_s:
                player.velocity[1] = 0  # Stop moving player vertically
            elif event.key == pygame.K_a or event.key == pygame.K_d:
                player.velocity[0] = 0  # Stop moving player horizontally

    # scroll the screen to the player's position
    # camera_x = -player.position[0] + screen_center[0]
    # camera_y = -player.position[1] + screen_center[1]
    # screen.scroll(int(camera_x), int(camera_y))
    # screen.blit(screen, (camera_x, camera_y))

    # update the screen
    pygame.display.update()


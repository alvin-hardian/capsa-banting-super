import os
import pygame

"""
class BaseImage :
    sprite  : pygame.Surface
    position: dict {'x','y}
"""
class BaseImage:
    def __init__(self):
        self.sprite = ''
        self.pos = {
            'x' : 0,
            'y' : 0
        }

    def position(self):
        return (self.pos['x'], self.pos['y'])


"""
class Card:
    type    : clover, diamond, heart, spade
    number  : 1 , 2, ..., 13
    sprite  : pygame.Surface
    select  : boolean True or False
    ongoing : boolean True or False
"""
class Card(BaseImage):
    def __init__(self, types, number, sprite):
        BaseImage.__init__(self)
        self.type = types
        self.number = number
        self.sprite = sprite
        self.select = False
        self.ongoing = False

    def __lt__(self, other):
        if self.number != other.number:
            return self.number < other.number
        else :
            return self.type < other.type

"""
class Button :
    name    : button image
    sprite  : array of pygame.Surface object
    index   : 
        0   -> clickable
        1   -> clicked
        2   -> disabled
"""
class Button(BaseImage):
    def __init__(self, name, sprite_non_pressed, sprite_pressed, sprite_disabled):
        BaseImage.__init__(self)
        self.name = name
        self.sprite = [sprite_non_pressed, sprite_pressed, sprite_disabled]
        self.index = 0

    def get_sprite(self):
        return self.sprite[self.index]


"""
class CardLoader :
    PATH        : path to the folder
    card_dict   : dictionary to save card
    card        : array contain flatten card_dict
"""
class CardLoader:
    def __init__(self):
        self.PATH = os.path.join('.','assets','card')
        self.card_dict = {
            'clover' : [0]*13,
            'diamond' : [0]*13,
            'heart' : [0]*13,
            'spade' : [0]*13,
        } 

    def load(self):
        for root, dirs, files in os.walk(self.PATH):
            card_image_path = [os.path.join(root, file) for file in files]
            self.load_image_path(card_image_path)
        self.flatten(self.card_dict)
        return self

    def load_image_path(self, paths):
        for path in paths: 
            card_type = path.split('_')[2][:-4]
            card_number = int(path.split('_')[1])
            card_value = card_number
            card_sprite = pygame.image.load(path).convert()
            if card_value == 1 : card_value = 14
            if card_value == 2 : card_value = 15
            self.card_dict[card_type][card_number-1] = Card(card_type, card_value, card_sprite)

    def flatten(self, card_dict):
        self.card = self.card_dict['diamond'] + self.card_dict['clover'] + self.card_dict['heart'] + self.card_dict['spade']

"""
class BackgroundLoader :
    PATH        : path to the image
    background  : pygame.Surface object
"""
class BackgroundLoader:
    def __init__(self):
        self.PATH = os.path.join('.','assets','background.jpg')

    def load(self):
        self.background = pygame.image.load(self.PATH).convert()
        return self

"""
class ButtonLoader :
    PATH        : path to the folder
    button_dict : dictionary to save image
    button      : dictionary to map between button name and button sprite
"""
class ButtonLoader:
    def __init__(self):
        self.PATH = os.path.join('.','assets','button')
        self.button_dict = {}
        self.button = {}

    def load(self):
        for root, dirs, files in os.walk(self.PATH):
            button_image_path = [os.path.join(root, file) for file in files]
            self.load_image_path(button_image_path)
        self.load_button()
        return self

    def load_image_path(self, paths):
        for path in paths: 
            button_name = path.split(os.sep)[-1].split('.')[0]
            self.button_dict[button_name] = pygame.image.load(path).convert()

    def load_button(self):
        print(self.button_dict)
        self.button['play'] = Button('play', self.button_dict['play'], self.button_dict['play-pressed'], self.button_dict['play-disabled'])
        self.button['pass'] = Button('pass', self.button_dict['pass'], self.button_dict['pass-pressed'], self.button_dict['pass-disabled'])

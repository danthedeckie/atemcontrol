#!/usr/bin/python
# ATEMController Python Project - OMNIvision UI (oui)
# Copyright (C) Daniel Fairhead
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http: //www.gnu.org/licenses/>.

import logging
import pygame
from pygame.locals import *
from defaults import *

#################
#
# 'globals' (well. almost)
#
#################

clickables = []
writer = False

#################
#
# Initialisation for everything.
#
#################

def init():
    global writer

    pygame.init()
    pygame.font.init()

    writer = pygame.font.Font(pygame.font.get_default_font(),
                              SCREEN_TEXT_SIZE)

#################
#
# Stuff you need to call:
#
#################

def do_clickables(x, y, button):
    print "X:%i;Y:%i"%(x, y)
    for (l, t, w, h), control in clickables:
        if  x > l and x < l + w \
        and y > t and y > y + h:
            control.click(x - l, y - t, button)

#################
#
# Useful functions:
#
#################

def highlight_lowlight(color):
    """ Returns a pair of tinted version of the original color, typically
        for use in drawing something '3D'. """

    (h,s,v,a) = color.hsva

    highlight = pygame.Color(255,255,255)
    highlight.hsva = (h, max(0,s-30), min(100,v+20), a)

    lowlight = pygame.Color(0, 0, 0)
    lowlight.hsva = (h, min(100,s+20), max(0, v-50), a)
    
    # Note: There's probabaly a better/faster way than doing this 
    #       via HSVA. Feel free to change it.

    return highlight, lowlight


#################
#
# Our custom controls:
#
#################


class Control(object):
    """ generic simple 'widget' to draw on screen. Probably
        shouldn't be used on it's own, but subclassed out. """

    def __init__(self, surface, position):
        self.surface = surface.subsurface(position)
        self.set_position(position)

    def set_position(self, position):
        # Note: since our 'surface' is a subsurface, coordinates
        #       for drawing are local to the subsurface, thus 0, 0.
        self.real_x, self.real_y, self.w, self.h = position
        self.position = (0, 0, self.w, self.h)
        self.x, self.y = (0, 0)
    
    def draw(self):
        pygame.draw.rect(self.surface, (0,0,0), self.position)

    def click(self, x, y, button):
        self.action()

    def keypress(self, key):
        self.action()

    def action(self):
        pass

    def register_global_keys(self):
        return []



class Button(Control):
    """ simple button widget """

    def __init__(self, surface, position, text, color='default'):
        Control.__init__(self, surface, position)

        clickables.append((position, self))

        self.set_color(color)
        self.highlight, self.lowlight = highlight_lowlight(self.color)

        self.text_color = (255, 255, 255)  # TODO
        self.set_label(text)

    def set_label(self, text):
        self.label = writer.render(text, True, self.text_color)
        self.label_rect = self.label.get_rect()
        self.label_rect.center = (self.x + (self.w / 2), \
                                  self.y + (self.h / 2))

    def set_color(self, color, active=False):
        self.color_name = color
        if active:
            self.color = pygame.Color(*(BUTTON_TYPE_ACOLORS[color]))
        else:
            self.color = pygame.Color(*(BUTTON_TYPE_COLORS[color]))

    def set_active(self, mode=True):
        self.set_color(self.color, mode)

    def draw(self):
        self.surface.fill(self.color, (2, 2, self.w - 2, self.h - 2))
        self.surface.blit(self.label, self.label_rect)

        pygame.draw.lines(self.surface, self.highlight, False, (
            (self.w - 2, 1), 
            (2, 1),
            (1, 2),
            (1, self.h)))

        pygame.draw.lines(self.surface, self.lowlight, False, (
            (self.w - 1, 2),
            (self.w - 1, self.h - 2),
            (self.w - 2, self.h - 1), 
            (2, self.h - 1)))

class Bus(Control):
    """ a set of buttons for drawing a video bus. """

    def __init__(self, surface, position, name, sources, bgcolor=(0,0,0)):
        Control.__init__(self, surface, position)
        self.bgcolor= pygame.Color(*bgcolor)
        self.buttons = []
        self.current_source = 0
        
        button_width = self.w / (len(sources) + 1)
        button_xs = range(button_width, self.w, button_width)

        for source, x, num in zip(sources, button_xs, xrange(10)):
            # TODO: replace '10' magic number with MAX_SOURCES config setting...
            s = source.get('shortname','default')
            t = source.get('type','default')
            self.buttons.append(Button(self.surface, 
                                       (x, 0, button_width, self.h), s, t))

            self.action = lambda: self.set_current(num)

        self.label = writer.render(name, True, (50, 50, 50))  
        # 50, 50, 50 = bus label color TODO - configfile it!
        self.label_rect = self.label.get_rect()
        self.label_rect.center = ((button_width / 2), self.y + (self.h / 2))

    def draw(self):
        
        self.surface.fill(self.bgcolor)
        self.surface.blit(self.label, self.label_rect)

        for button in self.buttons:
            button.draw()

    def set_current(self, source_number, do_action = True):
        self.button[self.current_source].set_active(False)
        self.current_source = source_number
        self.button[source_number].set_active()
        if do_action:
            self.action()

    def action(self):
        """ this has to be specified... """
        pass
    



#!/usr/bin/python
# ATEMController Python Project - main pygame interface
# Copyright (C) Daniel Fairhead
#    Frederik M.J. Vestre (ved/for Studentersamfundet i Trondheim)
#    Daniel Fairhead (OMNIvision) (reorganising/refactoring)
#    Based on perl code/reverse engineering by Michael Potter.
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

import fcntl
import sys
import os
from time import sleep
import logging

import pygame
from pygame.locals import *

from atem import ATEMController
from config import *
from localconfig import *

from gfxconfig import *


##############
#
# Keyboard controls:
#
##############

# Functions we want to put on the keyboard

FADE = ATEMController.fade
TOP = ATEMController.set_pgm_bus
BTM = ATEMController.set_pvw_bus
AUTO = ATEMController.auto_fade
CUT = ATEMController.cut

# Keys, functions, arguments:

keymap = {
    K_RETURN: (AUTO, 0),
    K_SPACE: (CUT, 0),

    K_1: (FADE, 0),
    K_2: (FADE, 111),
    K_3: (FADE, 222),
    K_4: (FADE, 333),
    K_5: (FADE, 444),
    K_6: (FADE, 555),
    K_7: (FADE, 666),
    K_8: (FADE, 777),
    K_9: (FADE, 888),
    K_0: (FADE, 1000),

    K_a: (TOP, 0),
    K_s: (TOP, 1),
    K_d: (TOP, 2),
    K_f: (TOP, 3),
    K_g: (TOP, 4),
    K_h: (TOP, 5),
    K_j: (TOP, 6),

    K_z: (BTM, 0),
    K_x: (BTM, 1),
    K_c: (BTM, 2),
    K_v: (BTM, 3),
    K_b: (BTM, 4),
    K_n: (BTM, 5),
    K_m: (BTM, 6)
}

#################
#
# Initialisation:
#
#################

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode(SCREEN_SIZE)

writer = pygame.font.Font(pygame.font.get_default_font(), SCREEN_TEXT_SIZE)

atem = ATEMController(HOST, PORT)


#################
#
# Main loop:
#
#################

happy_endless_loop = True

while happy_endless_loop:
    atem.step()

    # pygame stuff:

    event = pygame.event.poll()

    if event.type == pygame.QUIT:
        happy_endless_loop = False
    if event.type == KEYDOWN:
        if event.key in keymap:
            func, val = keymap[event.key]
            func(atem, val)
        elif event.key == K_ESCAPE:
            pygame.event.post(pygame.event.Event(QUIT))
        else:
            logging.warn('Unknown keypress')


    # draw pygame surfaces:

    screen.fill(SCREEN_COLOR)

    # PGM bus:

    def draw_buslist(surf, (initial_x,y), active = 0):
        currently = -1
        for x in range(initial_x, initial_x + ((BUTTON_WIDTH + BUTTON_PADDING) * 8), \
                BUTTON_WIDTH + BUTTON_PADDING):
            currently += 1
            if currently == active:
                surf.fill(BUTTON_ACTIVE_COLOR,(x,y,BUTTON_HEIGHT,BUTTON_WIDTH))
            else:
                surf.fill(BUTTON_COLOR,(x,y,BUTTON_HEIGHT,BUTTON_WIDTH))
            label = writer.render(SOURCE_LIST[currently]['shortname'], True, BUTTON_TEXT_COLOR)
            label_rect = label.get_rect()
            label_rect.center = (x + (BUTTON_WIDTH/2), y + (BUTTON_HEIGHT/2))
            surf.blit(label, label_rect)

    draw_buslist(screen, PGM_BUS, atem.pgm_bus)
    draw_buslist(screen, PVW_BUS, atem.pvw_bus)

    pygame.display.flip()


    
    #if line in keymap:
    #    func, val = keymap[line]
    #    func(atem, val)
    #else:
    #    logging.warn('Unknown keypress')
    # 88 18 801c 01e1 0000 0000 01f7 - 000c 0000 4354 5073 0054 01f1 (Example pkg)
    #payload = pack("!HHHHHH", 0x000c, 0x0000, 0x4354, 0x5073, 0x0054, int(line))#value from 0-1000
    #atem.send_pkt(0x88, self.count_in, 0, 0, self.mycount, payload)

atem.close()

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
import oui


##############
#
# Keyboard controls:
#
##############

# Functions we want to put on the keyboard


FADE = ATEMController.fade
PGM = ATEMController.set_pgm_bus
PVW = ATEMController.set_pvw_bus
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

    K_a: (PGM, 0),
    K_s: (PGM, 1),
    K_d: (PGM, 2),
    K_f: (PGM, 3),
    K_g: (PGM, 4),
    K_h: (PGM, 5),
    K_j: (PGM, 6),

    K_z: (PVW, 0),
    K_x: (PVW, 1),
    K_c: (PVW, 2),
    K_v: (PVW, 3),
    K_b: (PVW, 4),
    K_n: (PVW, 5),
    K_m: (PVW, 6)
}


#################
#
# Initialisation:
#
#################

screen = oui.init(SCREEN_SIZE)

#screen = pygame.display.set_mode(SCREEN_SIZE)

atem = ATEMController(HOST, PORT)

BUS_WIDTH = BUTTON_WIDTH * 10

aux1bus = oui.Bus(screen, (10, 100, BUS_WIDTH, BUTTON_HEIGHT), 'Aux1', SOURCE_LIST)
aux2bus = oui.Bus(screen, (10, 160, BUS_WIDTH, BUTTON_HEIGHT), 'Aux2', SOURCE_LIST)
aux3bus = oui.Bus(screen, (10, 220, BUS_WIDTH, BUTTON_HEIGHT), 'Aux3', SOURCE_LIST)

dskbus = oui.Bus(screen, (10, 280, BUS_WIDTH, BUTTON_HEIGHT), 'DSK', SOURCE_LIST)

pgmbus = oui.Bus(screen, (10, 340, BUS_WIDTH, BUTTON_HEIGHT), 'PGM', SOURCE_LIST)
pvwbus = oui.Bus(screen, (10, 400, BUS_WIDTH, BUTTON_HEIGHT), 'PVW', SOURCE_LIST)

pgmbus.action = lambda: atem.set_pgm_bus(pgmbus.current_source)
pvwbus.action = lambda: atem.set_pvw_bus(pvwbus.current_source)



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
    elif event.type == KEYDOWN:
        if event.key in keymap:
            func, val = keymap[event.key]
            func(atem, val)
        elif event.key == K_ESCAPE:
            pygame.event.post(pygame.event.Event(QUIT))
        else:
            logging.warn('Unknown keypress')
    elif event.type == MOUSEBUTTONUP:
        mousex, mousey = event.pos
        screen.click(mousex, mousey, event.button)


    # draw pygame surfaces:

    #screen.surface.fill(SCREEN_COLOR)
    screen.draw()


    aux1bus.draw()
    aux2bus.draw()
    aux3bus.draw()
    dskbus.draw()
    pgmbus.draw()
    pvwbus.draw()

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

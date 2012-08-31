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

import logging

import pygame
from pygame.locals import *

from atem import ATEMController
from config import *
from localconfig import *

from gfxconfig import *
import oui

#######################
#                     #
#   Initialisation:   #
#                     #
#######################

screen = oui.init(SCREEN_SIZE)

atem = ATEMController(HOST, PORT)

aux1bus = oui.Bus(screen, (10, 100, BUS_WIDTH, BUTTON_HEIGHT), 'Aux1', SOURCE_LIST)
aux2bus = oui.Bus(screen, (10, 160, BUS_WIDTH, BUTTON_HEIGHT), 'Aux2', SOURCE_LIST)
aux3bus = oui.Bus(screen, (10, 220, BUS_WIDTH, BUTTON_HEIGHT), 'Aux3', SOURCE_LIST)

dskbus = oui.Bus(screen, (10, 280, BUS_WIDTH, BUTTON_HEIGHT), 'DSK', SOURCE_LIST)

pgmbus = oui.Bus(screen, (10, 340, BUS_WIDTH, BUTTON_HEIGHT), 'PGM', SOURCE_LIST)
pvwbus = oui.Bus(screen, (10, 400, BUS_WIDTH, BUTTON_HEIGHT), 'PVW', SOURCE_LIST)

cutbutton = oui.Button(screen, (BUS_WIDTH + 50, 340, BUTTON_WIDTH, BUTTON_HEIGHT), 'CUT')
autotakebutton = oui.Button(screen, (BUS_WIDTH + 50, 400, BUTTON_WIDTH, BUTTON_HEIGHT), 'FADE')

# by wrapping the actions in lambdas, (or functions) they don't get called until
# the action is called...

pgmbus.action = lambda: atem.set_pgm_bus(pgmbus.current_source)
pvwbus.action = lambda: atem.set_pvw_bus(pvwbus.current_source)

def cut():
    atem.cut()
    pwv = pgmbus.current_source
    pgmbus.set_current(pvwbus.current_source, False)
    pvwbus.set_current(pwv, False)

cutbutton.action = cut
autotakebutton.action = cut

######################
#                    #
# Keyboard controls: #
#                    #
######################

keymap = {}

keymap.update(pgmbus.set_keys([K_a, K_s, K_d, K_f, K_g, K_h, K_j]))

keymap.update(pvwbus.set_keys([K_z, K_x, K_c, K_v, K_b, K_n, K_m]))

keymap[K_RETURN] = autotakebutton.action
keymap[K_SPACE] = cutbutton.action

######################
#                    #
#     Main loop:     #
#                    #
######################

happy_endless_loop = True

while happy_endless_loop:
    atem.step()

    # pygame stuff:

    event = pygame.event.poll()

    if event.type == pygame.QUIT:
        happy_endless_loop = False
    elif event.type == KEYDOWN:
        if event.key in keymap:
            func = keymap[event.key]
            #func(atem, val)
            func()
        elif event.key == K_ESCAPE:
            pygame.event.post(pygame.event.Event(QUIT))
        else:
            logging.warn('Unknown keypress')
    elif event.type == MOUSEBUTTONUP:
        mousex, mousey = event.pos
        screen.click(mousex, mousey, event.button)

    # draw pygame surfaces:
    # TODO: this would be better if the controls register themselves
    #       (with their parents) and get drawn that way. (so we can
    #       hide whole groups of controls/tabs.  Also keymapping stuff.

    screen.draw()

    aux1bus.draw()
    aux2bus.draw()
    aux3bus.draw()
    dskbus.draw()
    pgmbus.draw()
    pvwbus.draw()
    cutbutton.draw()
    autotakebutton.draw()

    pygame.display.flip()

atem.close()

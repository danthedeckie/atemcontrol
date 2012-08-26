#!/usr/bin/python
# ATEMController Python Project - main basic interface
# Copyright (C) 2012
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

from struct import pack, unpack
from binascii import hexlify, unhexlify
import socket
import random
import fcntl
import sys
import os
from time import sleep
import logging

from atem import ATEMController
from config import *
from localconfig import *

has_midi = False

try:
    import pypm
    has_midi = True
except:
    pass


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

# Keys, functions, arguments:

keymap = {
    '`': (AUTO, 0),
    '1': (FADE, 0),
    '2': (FADE, 111),
    '3': (FADE, 222),
    '4': (FADE, 333),
    '5': (FADE, 444),
    '6': (FADE, 555),
    '7': (FADE, 666),
    '8': (FADE, 777),
    '9': (FADE, 888),
    '0': (FADE, 1000),

    'a': (TOP, 0),
    's': (TOP, 1),
    'd': (TOP, 2),
    'f': (TOP, 3),
    'g': (TOP, 4),
    'h': (TOP, 5),
    'j': (TOP, 6),

    'z': (BTM, 0),
    'x': (BTM, 1),
    'c': (BTM, 2),
    'v': (BTM, 3),
    'b': (BTM, 4),
    'n': (BTM, 5),
    'm': (BTM, 6)
}

# Midi stuff.

midiin = None
if has_midi:
    logging.info("Pre midi init")
    interf, name, inp, outp, opened = pypm.GetDeviceInfo(0)
    midiin = pypm.Input(0)
    logging.info("Post midi init")

# make stdin a non-blocking file
fd = sys.stdin.fileno()
fl = fcntl.fcntl(fd, fcntl.F_GETFL)
fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

atem = ATEMController(HOST, PORT)

#################
#
# Main loop:
#
#################

while True:
    if midiin:
        midi_msg = midiin.Read(1)
        if midi_msg:
            data, counter = midi_msg[0]
            bank, instrument, value, val2 = data
            logging.info('|', join([bank, instrument, value]))
            # 88 18 801c 01e1 0000 0000 01f7 - 000c 0000 4354 5073 0054 01f1
            # (Example pkg - value from 0-1000)
            payload = None
            if bank == 176 and instrument == 2:
                #Fader moved
                sval = value * 7.87
                if sval < 15:
                    sval = 0
                elif sval > 985:
                    sval = 1000
                atem.fade(sval)
            if bank == 176 and value == 127:
                if instrument > 22 and instrument < 32:
                    #top pressed
                    atem.set_pgm_bus(instrument-22)
                if instrument > 32  and instrument < 42: 
                    #bottom pressed
                    atem.set_pvw_bus(instrument-32)
                if instrument == 45:
                    #other bottom pressed
                    atem.auto_fade()
            continue
    atem.step()

    #Read from command line

    line = None
    try:
        line = sys.stdin.readline().strip()
    except:
        pass
    if line: #Send mixer info
        if line in keymap:
            func, val = keymap[line]
            func(atem, val)
        else:
            logging.warn('Unknown keypress')
        # 88 18 801c 01e1 0000 0000 01f7 - 000c 0000 4354 5073 0054 01f1 (Example pkg)
        #payload = pack("!HHHHHH", 0x000c, 0x0000, 0x4354, 0x5073, 0x0054, int(line))#value from 0-1000
        #atem.send_pkt(0x88, self.count_in, 0, 0, self.mycount, payload)

atem.close()

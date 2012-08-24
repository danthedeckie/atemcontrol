#License: http://www.gnu.org/licenses/agpl.html
#(c) Frederik M.J. Vestre (ved/for Studentersamfundet i Trondheim)
#    Daniel Fairhead (OMNIvision) (reorganising/refactoring)
#    Based on perl code/reverse engineering by Michael Potter, 
#          and reverse engineering with wireshark
#          Blackmagic ATEM switch control
#Works with Blackmagic ATEM television studio - standard config
#Midi requires pyportmidi

#Reverse engineering info:
# http://atemuser.com/forums/atem-vision-mixers/blackmagic-atems/controlling-atem
#http://sig11.de/~ratte/misc/atem/

from struct import pack, unpack
from binascii import hexlify, unhexlify
import socket
import random
import fcntl
import sys
import os
from time import sleep
from atem import ATEMController
has_midi = False
try:
    import pypm
    has_midi = True
except:
    pass
    
HOST = '192.168.10.240'    # The remote host
PORT = 9910              # The same port as used by the server

# Keyboard control:
#   TODO: put this in a separate class/module???

FADE = ATEMController.fade
TOP = ATEMController.top
BTM = ATEMController.bottom
OTHER = ATEMController.other_bottom

keymap = {
    '1':(FADE,0),
    '2':(FADE,111),
    '3':(FADE,222),
    '4':(FADE,333),
    '5':(FADE,444),
    '6':(FADE,555),
    '7':(FADE,666),
    '8':(FADE,777),
    '9':(FADE,888),
    '0':(FADE,1000),

    'a':(TOP,0),
    's':(TOP,1),
    'd':(TOP,2),
    'f':(TOP,3),
    'g':(TOP,4),
    'h':(TOP,5),
    'j':(TOP,6),

    'z':(BTM,0),
    'x':(BTM,1),
    'c':(BTM,2),
    'v':(BTM,3),
    'b':(BTM,4),
    'n':(BTM,5),
    'm':(BTM,6)
}



midiin = None
if has_midi:
    print "Pre midi init"
    interf,name,inp,outp,opened = pypm.GetDeviceInfo(0)
    midiin = pypm.Input(0)
    print "Post midi init"

# make stdin a non-blocking file
fd = sys.stdin.fileno()
fl = fcntl.fcntl(fd, fcntl.F_GETFL)
fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

atem = ATEMController(HOST,PORT)
    
while True:
    if midiin:
        midi_msg = midiin.Read(1) 
        if midi_msg:
            data, counter = midi_msg[0]
            bank, instrument, value, val2 = data
            print bank,instrument,value
            #88 18 801c 01e1 0000 0000 01f7 - 000c 0000 4354 5073 0054 01f1 (Example pkg - value from 0-1000)
            payload = None
            if bank == 176 and instrument == 2:
                #Fader moved
                sval = value*7.87
                if sval<15:
                    sval=0
                elif sval>985:
                    sval=1000
                atem.fade(sval)

            if bank == 176 and instrument > 22  and instrument < 32 and value == 127:
                #top pressed
                atem.top(instrument-22)
            if bank == 176 and instrument > 32  and instrument < 42 and value == 127:
                #bottom pressed
                atem.bottom(instrument-32)
            if bank == 176 and instrument == 45 and value == 127:
                #bottom pressed
                atem.other_bottom()
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
            func(atem,val)
        else:
            print 'Unknown keypress'
        #print line
        # 88 18 801c 01e1 0000 0000 01f7 - 000c 0000 4354 5073 0054 01f1 (Example pkg)
        #payload = pack("!HHHHHH", 0x000c, 0x0000,0x4354, 0x5073, 0x0054, int(line))#value from 0-1000
        #atem.send_pkt(0x88, self.count_in, 0, 0, self.mycount, payload) 

atem.close()

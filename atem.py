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
has_midi = False
try:
    import pypm
    has_midi = True
except:
    pass
    
HOST = '192.168.10.240'    # The remote host
PORT = 9910              # The same port as used by the server
def rand(max):
    return int(random.uniform(0,max))

class ATEMController(object):

    count_in = 0
    count_out = 0
    mycount = 0

    def __init__(self, ip, port):
        self.connect(ip,port)

    def connect(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.connect((ip, port))
        self.uid = self.send_hello()
        #self.sock.send(unhexlify("1014439d00000000000000000100000000000000"))
        #800c67a50000000000500000
        print self.uid
        hello_finished = False
        self.sock.setblocking(False)

    def send_hello(self):
        self.uid   = (((rand(254) + 1) << 8) + rand(254) + 1) & 0x7FFF
        #self.uid = 0x67a5
        data  = pack("!HHHH", 0x0100, 0x0000, 0x0000, 0x0000)
        print "Data", hexlify(data)
        hello = pack("!BBHHHHH", 0x10, 0x14, self.uid, 0, 0, 0x0000, 0) + data
        print "Hello:", hexlify(hello)
        #101454b200000000000000000100000000000000

        self.sock.send(hello)
        return self.uid
        
    def send_pkt(self, cmd, cout, un1, un2, cin, payload):
        ln = 12 + len(payload)
        cmd += ((ln >> 8) & 0x07)
        pkt = pack("!BBHHHHH", cmd, ln, self.uid, cout, un1, un2, cin) + payload
        #if not ln==12:
        #    print "Send:", hexlify(pkt)
        #    print_pkt(cmd, ln, self.uid, cout, un1, un2, cin, payload)
        self.sock.send(pkt)

    def recv_pkt(self, data):
        pkt = data
        cmd, len, self.uid, self.count_out, unknown1, unknown2, self.count_in = unpack("!BBHHHHH", data[0:12])
        payload = data[12:]
        #(port, ipaddr) = self.sockaddr_in($self.sock->peername)
        len = ((cmd & 0x07) << 8) + len
        cmd = cmd & 0xF8
        return (cmd, len, self.uid, self.count_out, unknown1, unknown2, self.count_in, payload)

    def print_pkt(self, cmd, len, count_out, unknown1, unknown2, count_in, payload):
        print ("Cmd:",
               hex(cmd), "Len:",
               len, "Uid:",
               hex(self.uid), "Unkn1:",
               unknown1, "Unkn2:",
               unknown2, "Cnti:", 
               hex(self.count_in), "Payload:",
               hexlify(payload))

    def step(self):
        try:
            data = self.sock.recv(1024*10)
        except socket.error:
            sleep(0.02)
            return True
        if not data:
            print "Nodat"
            return False
        #print "Recv:", hexlify(data[0:16])
        args = self.recv_pkt(data)
        #print_pkt(*args)
        cmd, ln, self.uid, self.count_out, unknown1, unknown2, self.count_in, payload = args
        if not ln==12:
            print("R")
            print_pkt(*args)
        if cmd & 0x10:
            # hello response
            #undef, new_self.uid, undef, undef = unpack("!HHHH", payload)
            #self.uid = unpack("!HHHH", payload)[1]
            print "Helloresp", self.uid, cmd, cmd&0x10
            #send_pkt(0x80, self.uid, 0x0, 0, 0x00e9, 0, '')
            self.send_pkt(0x80, 0, 0, 0x0050, 0, '')
            return True
        elif cmd & 0x08:
            #print "G8p", self.count_in, hello_finished
            if self.count_in == 0x04 and not hello_finished:
                hello_finished = True
                self.mycount+=1
                print "Hellofinish"
            if hello_finished:
                #print "SHF"
                self.send_pkt(0x80, self.count_in, 0, 0, 0, '')
                self.send_pkt(0x08, 0, 0, 0, self.mycount, '')
                self.mycount+=1
    #else:
    #   self.send_pkt(0x80, 0, 0, self.mycount, 0, '')
    #   self.mycount+=1

        #Sett standard command number
        if (self.mycount == 0 and hello_finished):
            cmd = 0x80


    # Higher level functions:
    # TODO: figure out proper names.

    def fade(self, amount): #amount 1-1000
        payload = pack("!HHHHHH", 0x000c, 0x0000,0x4354, 0x5073, 0x0054, amount)#value from 0-1000
        self.send_pkt(0x88, self.count_in, 0, 0, self.mycount, payload) 
        print "SENDFADE"

    def top(self, channel):
        payload = unhexlify("000c00004350674900")+chr(channel)+unhexlify("0000")
        self.send_pkt(0x08, self.count_in, 0, 0, self.mycount, payload) 
        print "SENDTPKG"

    def bottom(self, channel):
        payload = unhexlify("000c00004350764900")+chr(channel)+unhexlify("0000")
        #payload = unhexlify("000c00004350764900060000")
        self.send_pkt(0x08, self.count_in, 0, 0, self.mycount, payload) 
        print "SENDBPKG"

    def other_bottom(self):
        payload = unhexlify("000c97024441757400000000")
        #payload = unhexlify("000c00004350764900060000")
        atem.send_pkt(0x08, self.count_in, 0, 0, self.mycount, payload) 
        print "SENDATPKG"


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

atem.sock.close()

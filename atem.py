# ATEMController Python Project - Controller Class
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from struct import pack, unpack
from binascii import hexlify, unhexlify
import socket
from random import uniform as rand_uniform
import fcntl
import sys
import os
from time import sleep
import logging

def rand(max):
    return int(rand_uniform(0,max))

class ATEMController(object):

    count_in = 0
    count_out = 0
    mycount = 0
    hello_finished = False

    def __init__(self, ip, port):
        self.connect(ip,port)

    def connect(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.connect((ip, port))
        self.uid = self.send_hello()
        #self.sock.send(unhexlify("1014439d00000000000000000100000000000000"))
        #800c67a50000000000500000
        print self.uid
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
        return (cmd, len, self.count_out, unknown1, unknown2, self.count_in, payload)

    def print_pkt(self, cmd, len, count_out, unknown1, unknown2, count_in, payload):
        print ("Cmd:", hex(cmd), 
               "Len:", len, 
               "Uid:", hex(self.uid),
               "Unkn1:", unknown1,
               "Unkn2:", unknown2,
               "Cnti:", hex(self.count_in),
               "Payload:", hexlify(payload))

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
        cmd, ln, self.count_out, unknown1, unknown2, self.count_in, payload = args
        if not ln==12:
            print ("R")
            self.print_pkt(*args)
        if cmd & 0x10:
            # hello response
            #undef, new_self.uid, undef, undef = unpack("!HHHH", payload)
            #self.uid = unpack("!HHHH", payload)[1]
            print "Helloresp", self.uid, cmd, cmd & 0x10
            #send_pkt(0x80, self.uid, 0x0, 0, 0x00e9, 0, '')
            self.send_pkt(0x80, 0, 0, 0x0050, 0, '')
            return True
        elif cmd & 0x08:
            #print "G8p", self.count_in, hello_finished
            if self.count_in == 0x04 and not self.hello_finished:
                self.hello_finished = True
                self.mycount+=1
                print "Hellofinish"
            if self.hello_finished:
                #print "SHF"
                self.send_pkt(0x80, self.count_in, 0, 0, 0, '')
                self.send_pkt(0x08, 0, 0, 0, self.mycount, '')
                self.mycount+=1
    #else:
    #   self.send_pkt(0x80, 0, 0, self.mycount, 0, '')
    #   self.mycount+=1

        #Sett standard command number
        if (self.mycount == 0 and self.hello_finished):
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
        self.send_pkt(0x08, self.count_in, 0, 0, self.mycount, payload)
        print "SENDATPKG"

    def close(self):
        self.sock.close()

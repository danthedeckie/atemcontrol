# atemcontrol (in python) (WORK IN PROGRESS)

So far a very basic level of control, only.  The aim is to have a simple
flexible python API, which you can plug any interface you choose into (MIDI,
USB, touchscreen, web/html, whatever).  There'll also be a reasonably usable
(but simple) pygame/SDL graphical interface.  This means you can run it
on Raspberry Pi & similar low-power devices (as opposed to the very heavy-weight
official SDK & control programs.)

Obviously, if you need loads of power, with complex effects and keying and stuff,
then the official system and a heavyweight computer will be more to your needs.

But for simple switching & mixing, this should be fine.



Works with Blackmagic ATEM television studio - standard config
Midi requires pyportmidi

##Reverse engineering info:

http://atemuser.com/forums/atem-vision-mixers/blackmagic-atems/controlling-atem
http://sig11.de/~ratte/misc/atem/

## Roadmap:

1. Continue clean up
3. Flesh out library to cover more 'real' API.
4. pygame/SDL interface, and make interfaces in general more generic & plugable.
5. boot-to-controller Raspberry Pi image
6. drink coffee.

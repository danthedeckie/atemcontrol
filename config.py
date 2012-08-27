import logging

HOST = '192.168.10.240'    # The remote host
PORT = 9910              # The same port as used by the server

###logging.basicConfig(level=logging.INFO)

SOURCE_LIST = [ 
    {'shortname': 'CAM1', 'longname': 'Camera 1', 'type':'CAM'},
    {'shortname': 'CAM2', 'longname': 'Camera 2', 'type':'CAM'},
    {'shortname': 'CAM3', 'longname': 'Camera 3', 'type':'CAM'},
    {'shortname': 'GFX1', 'longname': 'Graphics 1', 'type':'GFX'},
    {'shortname': 'GFX2', 'longname': 'Graphics 2', 'type':'GFX'},
    {'shortname': 'RS1',  'longname': 'Router 1'},
    {'shortname': 'RS2',  'longname': 'Router 2'},
    {'shortname': 'BLK',  'longname': 'Black'}
]

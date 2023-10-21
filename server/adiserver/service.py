#!/usr/bin/env python3

'''
    Implementacion del servicio de blobs o paquetes de bytes
'''

import logging

_WRN = logging.warning

class BlobDB:
    '''
        Controla la base de datos persistente del servicio de blobs
    '''

    def __init__(self):
        print("init")
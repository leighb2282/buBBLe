#!/usr/bin/env python
# buBBle-server.py
# Bubble Server
# Version 00.00.01
# 1/13/2016, 11:49:10 AM
# Leigh Burton, lburton@metacache.net

# Import modules
import sys
import socket
import psycopg2
import threading

from Crypto.Cipher import AES
from random import randint

# Set initial variables
port = "8080"       # Port used for ingest.
conn = ""
cur = ""





def main():
    """ Main entry point for the script."""
    global conn
    global cur

    host = getNetworkIp()

    db-conn = psycopg2.connect(database="bubble", user="bubble", password="B3bb13!",host="127.0.0.1", port="5432")
    db-cur = db-conn.cursor()

    db-cur.execute('SELECT * from users WHERE username = %r' % (str(thisistheincomingusernamevariable)))
    row = db-cur.fetchone()
    did = row[1].rstrip()
    dpass = row[2].rstrip()
    db-conn.close()
    pass

def getNetworkIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 0))
    return s.getsockname()[0]

if __name__ == '__main__':
    sys.exit(main())

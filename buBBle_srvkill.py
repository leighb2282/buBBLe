#!/usr/bin/env python
# buBBle_srvkill.py
# Quick script to trip the kill routine on the server.
# Version v1.0.0
# 1/28/2016, 7:42:17 PM
# Leigh Burton, lburton@metacache.net


# Import modules
import socket
import sys
# Variables!
server = "192.168.0.100"
auth_port = "33751"
kill_port = "33754"

def main():
    kill_conn = socket.socket()
    kill_conn.connect((server, int(kill_port)))
    kill_conn.send('mentos')
    kill_conn.shutdown(socket.SHUT_RDWR)
    kill_conn.close()

    auth_conn = socket.socket()
    auth_conn.connect((server, int(auth_port)))
    auth_conn.send('mentos')
    auth_conn.shutdown(socket.SHUT_RDWR)
    auth_conn.close()

    pass

if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python
# buBBle_srvkill.py
# Quick script to trip the kill routine on the server.
# Version v2.0.0
# 2/8/2016, 3:25:18 PM
# Leigh Burton, lburton@metacache.net


# Import modules
import socket
import sys
# Variables!
server = "192.168.0.100"
auth_port = "33751"
post_port = "33752"
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

    post_conn = socket.socket()
    post_conn.connect((server, int(post_port)))
    post_conn.send('mentos')
    post_conn.shutdown(socket.SHUT_RDWR)
    post_conn.close()
    pass

if __name__ == '__main__':
    sys.exit(main())

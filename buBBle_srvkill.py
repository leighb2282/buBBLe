#!/usr/bin/env python
# buBBle_srvkill.py
# Quick script to trip the kill routine on the server.
# Version v3.0.0
# 2/14/2016, 7:33:34 PM
# Leigh Burton, lburton@metacache.net


# Import modules
import socket
import sys
# Variables!
server = "192.168.0.100"
auth_port = "33751"
post_port = "33752"
pull_port = "33753"
kill_port = "33754"

kill_word = "mentos"

def main():
    kill_conn = socket.socket()
    kill_conn.connect((server, int(kill_port)))
    kill_conn.send(kill_word)
    kill_conn.shutdown(socket.SHUT_RDWR)
    kill_conn.close()

    auth_conn = socket.socket()
    auth_conn.connect((server, int(auth_port)))
    auth_conn.send(kill_word)
    auth_conn.shutdown(socket.SHUT_RDWR)
    auth_conn.close()

    post_conn = socket.socket()
    post_conn.connect((server, int(post_port)))
    post_conn.send(kill_word)
    post_conn.shutdown(socket.SHUT_RDWR)
    post_conn.close()

    pull_conn = socket.socket()
    pull_conn.connect((server, int(pull_port)))
    pull_conn.send(kill_word)
    pull_conn.shutdown(socket.SHUT_RDWR)
    pull_conn.close()
    pass

if __name__ == '__main__':
    sys.exit(main())

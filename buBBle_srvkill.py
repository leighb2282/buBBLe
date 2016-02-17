#!/usr/bin/env python
# buBBle_srvkill.py
# Quick script to trip the kill routine on the server.
# Version v3.0.0
# 2/14/2016, 7:33:34 PM
# Copyright (C) 2016 Leigh Burton, lburton@metacache.net

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.


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

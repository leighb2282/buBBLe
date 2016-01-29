#!/usr/bin/env python
# buBBle-server.py
# Bubble Server
# Version v0.0.3
# 1/28/2016, 8:24:50 PM
# Leigh Burton, lburton@metacache.net

# Import modules
import os
import sys
import socket
import threading
import time
import psycopg2

from Crypto.Cipher import AES
from random import randint # Remove once no longer needed.

# Set initial variables

# Network Ports
auth_port = "33751"       # Port used for Authentication.
push_port = "33752"       # Port used for new incoming posts.
pull_port = "33753"       # Port used for requesting posts.
kill_port = "33754"

# Thread status variables
authT_status = 0
postT_status = 0
pullT_status = 0
killT_status = 0

# aKeys is used for encrypting the authentication string when sending it to the server.
aKeys = ['52e85caef63299050e4e94f00b0c67c7',
    '57f9b6a737ed012d213ef7d92452d0e2',
    'f48e91a16995aa418c7c10e1b9c3d093',
    '3d19cb97c2a9ec47e4744ece0ec5da95',
    'c5220c28193b182bac76984fccbc9cfa',
    '50c5e64345c5ae58bc07364a629f4f73',
    '99c0edffd636bec9cebdd182b425cdff',
    '26c4ed27f37e394efe0898de01a2817d',
    '84dafaafacb4ea3b0870ab781f8bdbe0',
    '56535b10858d4d4f53afbc8ad051d0e1']
aKeys_n = len(aKeys)

def main():
    """ Main entry point for the script."""
    global conn
    global cur

    def getNetworkIp():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 0))
        return s.getsockname()[0]

    # Authentication Function.
    # Used to check credentials against the users table. Is used by all 3 threads.
    def auth_chk(un, pw):
        pass

    # Auth Thread.
    # Used to auth users either via the 'Auth button or when someone sends a message.
    def thread_auth():
        server = getNetworkIp()
        global authT_status
        while authT_status == 0:
            print "Waiting for Connection"

            auth_socket = socket.socket()
            auth_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            auth_socket.bind((server, int(auth_port)))
            auth_socket.listen(5)
            client_conn, client_ip = auth_socket.accept()
            client_auth = client_conn.recv(1024)

            keyid = client_auth[:1:1]
            ivid = client_auth[-1:]
            deca = AES.new(aKeys[int(keyid)], AES.MODE_CBC, aKeys[int(ivid)][:16])
            decrypt_auth = deca.decrypt(client_auth[1:-1])
            print client_auth
            print str(keyid) + ' : ' + aKeys[int(keyid)]
            print str(ivid) + ' : ' + aKeys[int(ivid)][:16]
            client_conn.send('1') # We would usually be checking against the PostgreSQL database but for testin purposes we just send '1'

            client_conn.close()
            auth_socket.shutdown(socket.SHUT_RDWR)
            auth_socket.close()
            print "\033[94mConnection from\033[97m %s \033[94mvia port\033[97m %s" % (client_ip[0], client_ip[1]) # Print debug stuff to console
            time.sleep(1)
            print "\033[94mEncrypted: \033[97m" + client_auth
            print "\033[94mDecrypted: \033[97m" + decrypt_auth
            time.sleep(1)
        pass

    # Post Thread.
    # Used to store posts into the relevant databases.
    def daemon_post():
        y = 0
        global postT_status
        while y < 10:
            b = randint(0,5)
            print "\033[92mPost "+ str(y) + " sleeping for " + str(b) + " Seconds.\n"
            time.sleep(b)
            y = y + 1
            postT_status = postT_status + b
        print "\033[91mPost total: " + str(postT_status) + "\n"
        pass

    # Pull Thread
    # Used to deliver posts from the relevant database to a client.
    def daemon_pull():
        z = 0
        global pullT_status
        while z < 10:
            c = randint(0,5)
            print "\033[93mPull "+ str(z) + " sleeping for " + str(c) + " Seconds.\n"
            time.sleep(c)
            z = z + 1
            pullT_status = pullT_status + c
        print "\033[91mPull total: " + str(pullT_status) + "\n"
        pass

    def thread_kill():
        server = getNetworkIp()
        global authT_status
        global postT_status
        global pullT_status
        global killT_status
        while killT_status == 0:
            try:
                kill_socket = socket.socket()
                kill_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                kill_socket.bind((server, int(kill_port)))
                kill_socket.listen(5)
                kill_conn, kill_ip = kill_socket.accept()
                kill_sig = kill_conn.recv(1024)
                kill_conn.close()
                kill_socket.shutdown(socket.SHUT_RDWR)
                kill_socket.close()

                if kill_sig == "mentos":
                    print "Killing Threads"
                    authT_status = 1
                    postT_status = 1
                    pullT_status = 1
                    killT_status = 1
                else:
                    pass
            except:
                print "Kill Thread fucked up."
        pass

    # Setting up the threads.
    auth_d = threading.Thread(name='auth thread', target=thread_auth)
    post_d = threading.Thread(name='post daemon', target=daemon_post)
    pull_d = threading.Thread(name='pull daemon', target=daemon_pull)
    kill_d = threading.Thread(name='kill thread', target=thread_kill)

    # Pretty certain no need for daemonic threading
    #auth_d.setDaemon(True)
    #post_d.setDaemon(True)
    #pull_d.setDaemon(True)

    # Start them threads.
    auth_d.start()
    post_d.start()
    pull_d.start()
    kill_d.start()
    pass



if __name__ == '__main__':
    sys.exit(main())

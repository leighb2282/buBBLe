#!/usr/bin/env python
# buBBle-server.py
# Bubble Server
# Version v1.0.0
# 2/15/2016, 11:02:28 PM
# Leigh Burton, lburton@metacache.net

# Import modules
import os
import sys
import socket
import threading
import hashlib
import time
import psycopg2
import base64

from Crypto.Cipher import AES
from random import randint # Remove once no longer needed.

# Set initial variables
server = "" # Will contain external server IP
kill_safety = "mentos"
# Network Ports
auth_port = "33751"     # Port used for Authentication.
post_port = "33752"     # Port used for new incoming posts.
pull_port = "33753"     # Port used for requesting posts.
kill_port = "33754"     # Port used for gracefully killing the threads, mainly for testing.

# Thread status variables
authT_status = 0
postT_status = 0
pullT_status = 0
killT_status = 0

# During the post process the client re-auths, server will provide a token to the client to provide the post process.
# THe post thread will check this token against this list to confirm clients auth.
# Once the post thread has recieved a bulletin it will remove the token from the list.
post_tokens = {}

# Variable to hold current numebr of posts
general_newest = 0
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
aKeys_n = len(aKeys) -1 # Holds the number of keys in aKeys.

def main():
    """ Main entry point for the script."""
    global server
    global general_newest

    # I would put this in a function but as this is used only once in this particular way
    # I am putting it here to be ran at script startup to get newest post ID
    srv_db = psycopg2.connect(database="bubble", user="bubble", password="B3bb13!",host="127.0.0.1", port="5432") # Connect to DB
    srv_cur = srv_db.cursor() #generate a cursor
    srv_cur.execute("SELECT COUNT(*) from general") # Get a count of all entries
    general_newest = int(str(srv_cur.fetchall()).replace("[(", "").replace("L,)]", "")) # Manage that into a single integer held in general_newest
    srv_db.close() # Close connection to the DB

    def getNetworkIp():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 0))
        return s.getsockname()[0]

    server = getNetworkIp()

    # Authentication Function.
    # Used to check credentials against the users table. Is used by all 3 threads.
    def auth_chk(un, pw):
        pass

    # Generate a token
    def token_gen():
        global post_tokens
        token_sel = ['','']
        a = str(randint(10000,60000))
        b = aKeys[randint(0,aKeys_n)][:22]
        c = str(randint(10000,60000))
        d = str(randint(10000,60000)) + aKeys[randint(0,aKeys_n)][:22] + str(randint(10000,60000))
        token_in = hashlib.md5(d).hexdigest()
        token_sel[0] = randint(0,aKeys_n)
        token_sel[1] = randint(0,aKeys_n)

        print "\033[94mUnencrypted Token: \033[97m" + token_in
        token_crypt = AES.new(aKeys[token_sel[0]], AES.MODE_CBC, aKeys[token_sel[1]][:16])
        token_out = str(token_sel[0]) + token_crypt.encrypt(token_in) + str(token_sel[1])
        return [token_out, token_in]

    # Auth Thread.
    # Used to auth users either via the 'Auth button or when someone sends a message.
    def thread_auth():
        global kill_safety
        global server
        global authT_status
        while authT_status == 0:
            print "\033[97mWaiting for Connection"

            auth_socket = socket.socket()
            auth_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            auth_socket.bind((server, int(auth_port)))
            auth_socket.listen(5)
            auth_conn, client_ip = auth_socket.accept()
            client_auth = auth_conn.recv(1024)
            if client_auth == kill_safety:
                auth_conn.close()
                auth_socket.shutdown(socket.SHUT_RDWR)
                auth_socket.close()
                break
            keyid = client_auth[:1:1]
            ivid = client_auth[-1:]
            deca = AES.new(aKeys[int(keyid)], AES.MODE_CBC, aKeys[int(ivid)][:16])
            decrypt_auth = deca.decrypt(client_auth[1:-1])

            print "\033[94mConnection from\033[97m %s \033[94mvia port\033[97m %s" % (client_ip[0], client_ip[1]) # Print debug stuff to console
            print "\033[94mEncrypted: \033[97m" + client_auth
            print "\033[94mDecrypted: \033[97m" + decrypt_auth
            auth_split = decrypt_auth.split("/")
            auth_user = str(auth_split[0])
            auth_pass = str(auth_split[1])[:32]

            try:
                auth_db = psycopg2.connect(database="bubble", user="bubble", password="B3bb13!",host="127.0.0.1", port="5432")
                auth_cur = auth_db.cursor()

                auth_cur.execute('SELECT * from users WHERE username = %r' % (str(auth_user)))
                row = auth_cur.fetchone()
                db_id = row[0]
                db_user = row[1].rstrip()
                db_pass = row[2].rstrip()
                auth_db.close()
                print " \033[94mEncoder Derived Hash: \033[97m" + auth_pass
                print "\033[94mDatabase Derived Hash: \033[97m" + db_pass
                if auth_pass == db_pass:
                    print "\033[92mACCEPT CONNECTION (Auth Successful)"
                    token,token_raw = token_gen()
                    post_tokens[token_raw] = db_id
                    auth_conn.send(str('1') + token)
                else:
                    print "\033[91mREJECT CONNECTION"
                    auth_conn.send('0')
            except:
                print "Something borked."
                auth_conn.send('0')
            auth_conn.close()
            auth_socket.shutdown(socket.SHUT_RDWR)
            auth_socket.close()

            time.sleep(1)
        print "Auth Thread Ending"
        pass

    # Post Thread.
    # Used to store posts into the relevant databases.
    def thread_post():
        global kill_safety
        global server
        global postT_status
        global general_newest
        while postT_status == 0:
            post_socket = socket.socket()
            post_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            post_socket.bind((server, int(post_port)))
            post_socket.listen(5)
            post_conn, client_ip = post_socket.accept()
            token_post = post_conn.recv(1024)
            if token_post == kill_safety:
                post_conn.close()
                post_socket.shutdown(socket.SHUT_RDWR)
                post_socket.close()
                break
            key_token = token_post[:1:1]
            iv_token = token_post[-1:]
            token_dec = AES.new(aKeys[int(key_token)], AES.MODE_CBC, aKeys[int(iv_token)][:16])
            client_token = token_dec.decrypt(token_post[1:-1])
            print client_token
            # Here wil be decrypt for token post_token will be variable.
            if client_token in post_tokens:
                print post_tokens[client_token]
                post_conn.send('1') # Inform good token!
                bb_post = post_conn.recv(1024) #Recieve BB Post.
                postid = bb_post[:1:1]
                postiv = bb_post[-1:]
                bb_post64 = base64.b64encode(bb_post)
                post_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                try:
                    post_db = psycopg2.connect(database="bubble", user="bubble", password="B3bb13!",host="127.0.0.1", port="5432")
                    post_cur = post_db.cursor()
                    post_cur.execute('INSERT INTO general (ID_user, content, pdate, viewable) VALUES (%s, %s, %s, %s)', (post_tokens[client_token], bb_post64, post_time, True))
                    post_cur.execute('SELECT COUNT(*) from general')
                    general_newest = int(str(post_cur.fetchall()).replace("[(", "").replace("L,)]", ""))
                    post_db.commit()
                    post_db.close()
                    print "Commit Successful!"
                except:
                    print "Commit Failed."
            post_conn.close()
            post_socket.shutdown(socket.SHUT_RDWR)
            post_socket.close()
        print "Post Thread Ending"
        pass

    # Pull Thread
    # Used to deliver posts from the relevant database to a client.
    def thread_pull():
        global kill_safety
        global server
        global general_newest
        global pullT_status
        while pullT_status == 0:
            pull_socket = socket.socket()
            pull_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            pull_socket.bind((server, int(pull_port)))
            pull_socket.listen(5)
            pull_conn, client_ip = pull_socket.accept()
            token_pull = pull_conn.recv(1024)
            if token_pull == kill_safety:
                pull_conn.close()
                pull_socket.shutdown(socket.SHUT_RDWR)
                pull_socket.close()
                break
            key_token = token_pull[:1:1]
            iv_token = token_pull[-1:]
            token_dec = AES.new(aKeys[int(key_token)], AES.MODE_CBC, aKeys[int(iv_token)][:16])
            client_token = token_dec.decrypt(token_pull[1:-1])
            #print client_token
            if client_token in post_tokens:
                #print "yay! existing Token!"
                #print post_tokens[client_token]
                pull_conn.send('1|' + str(general_newest)) # Inform good token & send newest post ID
                postID = pull_conn.recv(1024) #Recieve post ID
                if postID == 'axe':
                    #print "Client had latest Post."
                    pass
                else:
                    print "Requested post: " + postID
                    try:
                        pull_db = psycopg2.connect(database="bubble", user="bubble", password="B3bb13!",host="127.0.0.1", port="5432")
                        pull_cur = pull_db.cursor()
                        pull_cur.execute('SELECT * from general WHERE ID_general = %r' % (str(postID)))
                        rowg = pull_cur.fetchone()
                        pull_cur.execute('SELECT * from users WHERE ID_user = %r' % (str(rowg[1])))
                        rowu = pull_cur.fetchone()
                        pull_db.close()

                        db_gid = rowg[0]
                        db_user = rowu[1].strip()
                        db_content = rowg[2].strip()
                        db_date = rowg[3].strip()
                        db_viewable = rowg[4]
                    except:
                        print "DB request failed."
                    if db_viewable == False:
                        pre_pull = "d" + "|" + str(db_gid) + "|" + db_user + "|" + "Content Marked Private" + "|" + db_date
                    else:
                        pre_pull = "v" + "|" + str(db_gid) + "|" + db_user + "|" + db_content + "|" + db_date
                    pull_conn.send(base64.b64encode(pre_pull))
            pull_conn.close()
            pull_socket.shutdown(socket.SHUT_RDWR)
            pull_socket.close()
        print "Pull Thread Ending"
        pass

    def thread_kill():
        global kill_safety
        global server
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

                if kill_sig == kill_safety:
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
    post_d = threading.Thread(name='post daemon', target=thread_post)
    pull_d = threading.Thread(name='pull daemon', target=thread_pull)
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

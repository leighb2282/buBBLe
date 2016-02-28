#!/usr/bin/env python
# buBBle-server.py
# Bubble Server
# Version v1.0.1
# 2/19/2016, 2:49:31 PM
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
import os
import sys
import socket
import threading
import hashlib
import time
import psycopg2
import base64

from Crypto.Cipher import AES
from random import randint

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

    # getNetworkIP function to get the public facng ip automagically, we do that by trying to connect to a known external IP and querying the sockets getsockname.
    def getNetworkIp():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 0))
        return s.getsockname()[0]

    server = getNetworkIp() # Actually invoking the above and storing the result in 'server'.

    # token_gen - used to generate a token for a client once they have authenticated, token is used for posting and retrieving messages.
    def token_gen():
        global post_tokens
        token_sel = ['','']
        d = str(randint(10000,60000)) + aKeys[randint(0,aKeys_n)][:22] + str(randint(10000,60000)) # THis is pretty sketchy in how its set up,
        token_in = hashlib.md5(d).hexdigest() # we then gett eh md5 hash of the sketchiness.
        token_sel[0] = randint(0,aKeys_n) # find out which auth key we will use to send the token to the client.
        token_sel[1] = randint(0,aKeys_n) # Find out which IV we will use to send the token to the client.

        token_crypt = AES.new(aKeys[token_sel[0]], AES.MODE_CBC, aKeys[token_sel[1]][:16]) # Set up the AES encryption usign the above values for key and IV
        token_out = str(token_sel[0]) + token_crypt.encrypt(token_in) + str(token_sel[1]) # Encrypt the token.
        return [token_out, token_in] # Return the token_out (ciphertext token) and the not-encrypted token back to the thread_auth function.

    # Auth Thread.
    # Used to auth users.
    def thread_auth():
        global kill_safety
        global server
        global authT_status
        while authT_status == 0: #while loopy loop AUTH AUTH STYLE.
            print "\033[97mWaiting for Connection"

            auth_socket = socket.socket() # Create a socket
            auth_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Set some socket options.
            auth_socket.bind((server, int(auth_port))) # Bind that socket to our public IP and auth port.
            auth_socket.listen(5) # Wait for a connection!
            auth_conn, client_ip = auth_socket.accept() # Accept a connection and also get the IP of the connecting device (currently not used but in place for future logging!)
            client_auth = auth_conn.recv(1024) # Recieve an auth request and but the data into clent_auth.
            if client_auth == kill_safety: # We check here if the server's been requested to end.
                auth_conn.close() # Close the onnection.
                auth_socket.shutdown(socket.SHUT_RDWR) # Shutdown the socket.
                auth_socket.close() # Close the socket.
                break # And end the auth thread.
            keyid = client_auth[:1:1] # Scrape the Key
            ivid = client_auth[-1:] # Scrape the IV
            deca = AES.new(aKeys[int(keyid)], AES.MODE_CBC, aKeys[int(ivid)][:16]) # Set up the AES encryption usign the above values for key and IV
            decrypt_auth = deca.decrypt(client_auth[1:-1]) # Decrypt the auth string.

            print "\033[94mConnection from\033[97m %s \033[94mvia port\033[97m %s" % (client_ip[0], client_ip[1]) # Print debug stuff to console
            print "\033[94mDecrypted: \033[97m" + decrypt_auth # Just show the auth string.
            auth_split = decrypt_auth.split("/") # Split the username and password into a list.
            auth_user = str(auth_split[0]) # Just place the username into its own variable.
            auth_pass = str(auth_split[1])[:32] # Just place the password into its own variable and make sure no whitespace hangs around.

            try:
                auth_db = psycopg2.connect(database="bubble", user="bubble", password="B3bb13!",host="127.0.0.1", port="5432") # Try to connect to the database
                auth_cur = auth_db.cursor() # Create a cursor to interract with the database.

                auth_cur.execute('SELECT * from users WHERE username = %r' % (str(auth_user))) # try to select the row that includes the username
                row = auth_cur.fetchone() # Fetch 1 result (there should only be one result)
                db_id = row[0] # Place the stored ID into a variable.
                db_user = row[1].rstrip() # Place the stored username into a variable.
                db_pass = row[2].rstrip() # Place the stored password into a variable.
                auth_db.close() # Close DB connection.
                print "  \033[94mClient Derived Hash: \033[97m" + auth_pass # Report what the client provided.
                print "\033[94mDatabase Derived Hash: \033[97m" + db_pass   # And what the server has on file.
                if auth_pass == db_pass: # See if they match.
                    print "\033[92mACCEPT CONNECTION (Auth Successful)" # Just throw on console a match
                    token,token_raw = token_gen() # Generate the tokens, 1 in ciphertext form to send to client, 1 to hold to check posts and requests.
                    post_tokens[token_raw] = db_id # send the ciphertext token to the client.
                    auth_conn.send(str('1') + token) # And store the unencrypted token in a dictionary to check against later.
                else:
                    print "\033[91mREJECT CONNECTION"
                    auth_conn.send('0') # sending back a '0' to the client = auth failed.
            except:
                print "Something borked."
                auth_conn.send('0') # sending back a '0' to the client = they probably tried to submit a username tat doesn't exist, or db issues.
            auth_conn.close() # Close connection.
            auth_socket.shutdown(socket.SHUT_RDWR) # Shutdown socket.
            auth_socket.close() # CLose socket.

            time.sleep(1) # Sleep for a second before we do it all again
        print "Auth Thread Ending"
        pass

    # Post Thread.
    # Used to store posts into the relevant databases.
    def thread_post():
        global kill_safety
        global server
        global postT_status
        global general_newest

        while postT_status == 0: #while loopy loop POST POST STYLE.
            post_socket = socket.socket() # Create a socket.
            post_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Set some socket options.
            post_socket.bind((server, int(post_port))) # Bind that socket to our public IP and post port.
            post_socket.listen(5) # Wait for a connection!
            post_conn, client_ip = post_socket.accept() # Accept a connection and also get the IP of the connecting device (currently not used but in place for future logging!).
            token_post = post_conn.recv(1024) # Recieve a token auth request (or kill word).

            if token_post == kill_safety: # We check here if the server's been requested to end.
                post_conn.close() # Close the onnection.
                post_socket.shutdown(socket.SHUT_RDWR) # Shutdown the socket.
                post_socket.close() # Close the socket.
                break # And end the post thread.

            key_token = token_post[:1:1] # Scrape the Key.
            iv_token = token_post[-1:] # Scrape the IV.
            token_dec = AES.new(aKeys[int(key_token)], AES.MODE_CBC, aKeys[int(iv_token)][:16]) # Set up the AES encryption usign the above values for key and IV.
            client_token = token_dec.decrypt(token_post[1:-1]) # Decrypt the token.

            if client_token in post_tokens: # If we find the client provided token is in our tokens dictionary.
                post_conn.send('1') # Inform good token!
                bb_post = post_conn.recv(1024) #Recieve BB Post.
                bb_post64 = base64.b64encode(bb_post) # Encode the post into base64 so we can store the post in a char field, I should probably look into basea to avoid this?
                post_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) # get the current server time to add to post data.

                try:
                    post_db = psycopg2.connect(database="bubble", user="bubble", password="B3bb13!",host="127.0.0.1", port="5432") # Try to connect to the database.
                    post_cur = post_db.cursor() # Create a cursor to interract with the database.
                    post_cur.execute('INSERT INTO general (ID_user, content, pdate, viewable) VALUES (%s, %s, %s, %s)', (post_tokens[client_token], bb_post64, post_time, True)) # Insert our data into a new DB row.
                    post_cur.execute('SELECT COUNT(*) from general') # Get a new count on number of entries.
                    general_newest = int(str(post_cur.fetchall()).replace("[(", "").replace("L,)]", "")) # update our general_newest variable.
                    post_db.commit() # Commit our data to the DB.
                    post_db.close() # Close the DB connection.
                    print "Commit Successful!"
                except:
                    print "Commit Failed."

            post_conn.close() # Close connection.
            post_socket.shutdown(socket.SHUT_RDWR) # Shutdown socket.
            post_socket.close()
        print "Post Thread Ending"
        pass # Close socket.

    # Pull Thread
    # Used to deliver posts from the relevant database to a client.
    def thread_pull():
        global kill_safety
        global server
        global general_newest
        global pullT_status

        while pullT_status == 0: # While loopy loop PULL PULL STYLE.
            pull_socket = socket.socket() # Create a socket.
            pull_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Set some socket options.
            pull_socket.bind((server, int(pull_port))) # Bind that socket to our public IP and pull port.
            pull_socket.listen(5) # Wait for a connection!
            pull_conn, client_ip = pull_socket.accept() # Accept a connection and also get the IP of the connecting device (currently not used but in place for future logging!).
            token_pull = pull_conn.recv(1024) # Recieve a token auth request (or kill word).

            if token_pull == kill_safety: # We check here if the server's been requested to end.
                pull_conn.close() # Close the onnection.
                pull_socket.shutdown(socket.SHUT_RDWR) # Shutdown the socket.
                pull_socket.close() # Close the socket.
                break # And end the post thread.

            key_token = token_pull[:1:1] # Scrape the Key.
            iv_token = token_pull[-1:] # Scrape the IV.
            token_dec = AES.new(aKeys[int(key_token)], AES.MODE_CBC, aKeys[int(iv_token)][:16]) # Set up the AES encryption usign the above values for key and IV.
            client_token = token_dec.decrypt(token_pull[1:-1]) # Decrypt the token.

            if client_token in post_tokens: # If we find the client provided token is in our tokens dictionary.
                pull_conn.send('1|' + str(general_newest)) # Inform good token.
                postID = pull_conn.recv(1024) #Recieve post ID.
                if postID == 'axe': # If we recieved the word 'axe' instead of an int here end it.
                    # Client had latest Post.
                    pass
                else:
                    try:
                        pull_db = psycopg2.connect(database="bubble", user="bubble", password="B3bb13!",host="127.0.0.1", port="5432") # Try to connect to the database.
                        pull_cur = pull_db.cursor() # Create a cursor to interract with the database.
                        pull_cur.execute('SELECT * from general WHERE ID_general = %r' % (str(postID))) # Select a row which matches the requested post ID.
                        rowg = pull_cur.fetchone() # Fetch a single row from the general table
                        pull_cur.execute('SELECT * from users WHERE ID_user = %r' % (str(rowg[1]))) # Select a row which matches the user ID in the requested message.
                        rowu = pull_cur.fetchone() # fetchthat row.
                        pull_db.close() # Close the DB connection.

                        db_gid = rowg[0] # grab the post ID from the requested post.
                        db_user = rowu[1].strip() # Grab the username from the users entry we got via rowg[1].
                        db_content = rowg[2].strip() # Grab the ciphertext message from the requested post.
                        db_date = rowg[3].strip() # Grab the date we stored from when the post was added.
                        db_viewable = rowg[4] # Grab the posts status.
                    except:
                        print "DB request failed."
                    if db_viewable == False: # We see if it is marked viewable or private.
                        pre_pull = "d" + "|" + str(db_gid) + "|" + db_user + "|" + "Content Marked Private" + "|" + db_date # if marked Private return a simple string informing client of that.
                    else:
                        pre_pull = "v" + "|" + str(db_gid) + "|" + db_user + "|" + db_content + "|" + db_date # if marked public return the actual ciphertext message.
                    pull_conn.send(base64.b64encode(pre_pull)) # encode the whole lot in base64 for ease of sending and send it on back to the client.
            else:
                pull_conn.send('0') # If we don't receive a valid token send back 0 status.
            pull_conn.close() # Close the onnection.
            pull_socket.shutdown(socket.SHUT_RDWR) # Shutdown the socket.
            pull_socket.close() # Close the socket.
        print "Pull Thread Ending"
        pass

    # This is here for while we develop the UI to aid in graceful shutdown of the server.
    # It recieves a killword and then flips all the thread's status variables to 1, which breaks the while loops.
    # WIll be depreciated once we have a UI as that will handle things like this.
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

    # Start them threads.
    auth_d.start()
    post_d.start()
    pull_d.start()
    kill_d.start()
    pass



if __name__ == '__main__':
    sys.exit(main())

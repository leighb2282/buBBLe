buBBle-Sphere v1.0.0
====================

A Connectivity Collection of encryption-focused tools.
------------------------------------------------------

Written as a Project for me to learn a lot more about Python, GUI programming via wx, socket networking, encryption, postgreSQL server maintenance, psycopg2 python interaction, and more! Be forewarned, the code is ugly but in a beautiful way! (To me at least!)

Requires: wx.python for the client, psycopg2 for the server.

The client uses a 'keydeck' loaded into the client to encrypt messages, only clients with the same keys in their keydeck will be able to read the messages.
The messages are stored on the server in encrypted form - even the server does not have the ability to decrypt messages, it is simply used for message storage.

Now v1.0.0 is out of it all I will be slowly, steadily improving all aspects of the collection as time permits, those improvements for the most part are detailed below.

All tools fully commented in-line for easy reading.

Tool Versions.
--------------
- Client:   v1.0.1 - Client app used for sending and receiving messages from the server.
- Server:   v1.0.1 - Server app used to authenticate users, store, and deliver messages.
- KrEYate:  v2.0.1 - A tool used to create a KeyDeck used in the client app for encrypting messages.
- deKrEYpt: v1.0.2 - A tool used to check/verify a KeyDeck can be decrypted.
- srv_kill: v1.0.1 - A tool to end the server threads gracefully while the server does not have a dedicated UI.

Additional Files.
-----------------
- DB stuff: Contains the steps I used to install and set up the PostgreSQL database as well as the table schema for user and general tables. recommend you use a different password to the example one given.

Planned future improvements
---------------------------

* Client:
  * Add ability to save to file the chat log.
  * Add ability to use load on the fly different KeyDecks.
  * Format / Prettify the chat text.

* Server:
  * Add srv_kill functionality into the server itself via...
  * Add interactive UI element to the server to manage bulletin boards, manage users, token management, etc.
  * Add logging for:
    * Authentication.
    * Bulletin posting.
    * Bulletin requests.
    * Management based tasks.

* KrEYate/deKrEYpt:
  * Improve the UI for these tools and merge them into 1 tool.

* srv_kill:
  * Depreciate this tool by adding it's functionality into the server itself, srv_kill was written to aid development of the server and is not meant to be a long-term tool.

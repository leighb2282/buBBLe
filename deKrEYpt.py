#!/usr/bin/env python
# deKrEYpt.py
# quick Key-Deck decryption tool
# Version v1.0.2
# 1/26/2016, 12:04:28 AM
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

import sys
import hashlib
from Crypto.Cipher import AES

infile = "bubble_keys.crypt"
keydecrypted = []

def main():
    try:
        cryptokey = raw_input("\033[93mFile Phrase:\033[97m ")
        open_keyfile = open(infile, "r")
        cryptohash = hashlib.md5(cryptokey).hexdigest()

        to_decrypt = open_keyfile.read()
        decrypto = AES.new(cryptohash, AES.MODE_CBC, cryptohash[:16])
        decrypted = decrypto.decrypt(str(to_decrypt))

        keydecrypted = decrypted.replace(" ", "").replace("[", "").replace("]", "").replace("'", "").split(",")
        open_keyfile.close()
        if keydecrypted[0] == 'VALID':
            print "Decrypted Successfully"
            del keydecrypted[0]
            print "KeyDeck Title: " + keydecrypted[0]
            del keydecrypted[0]
            for key in keydecrypted:
                print key
        else:
            print "Decrypt Failed."
    except:
        print "Error Occured"
if __name__ == '__main__':
    sys.exit(main())

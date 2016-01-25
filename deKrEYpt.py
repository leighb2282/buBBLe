#!/usr/bin/env python
# deKrEYpt.py
# quick Key-Deck decryption tool
# Version v1.0.0
# 1/25/2016, 2:28:33 PM
# Leigh Burton, lburton@metacache.net

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

        for key in keydecrypted:
            print key
    except:
        print "Error Occured"
if __name__ == '__main__':
    sys.exit(main())
#!/usr/bin/env python
# KrEYate.py
# quick Key-Deck creation tool
# Version v1.2.0
# 1/25/2016, 2:28:46 PM
# Leigh Burton, lburton@metacache.net

import sys
import hashlib
from Crypto.Cipher import AES

infile = "input.txt"
outfile = "bubble_keys.crypt"
keysetup = []
def main():
    try:
        open_input = open(infile, "r")
        for i in open_input:
            outhash = hashlib.md5(i).hexdigest()
            keysetup.append(outhash)
        open_input.close()
        uncrypt = str(keysetup)
        messlen = len(uncrypt)
        num2fill = 16 - (messlen % 16)
        tocrypt = (uncrypt + " " * num2fill)

        cryptokey = raw_input("\033[93mFile Phrase:\033[97m ")
        cryptohash = hashlib.md5(cryptokey).hexdigest()
        crypto = AES.new(cryptohash, AES.MODE_CBC, cryptohash[:16])
        encrypted = crypto.encrypt(tocrypt)

        f = open(outfile, "w")
        f.write(str(encrypted))
        f.close()
    except:
        print "Error Occured"
if __name__ == '__main__':
    sys.exit(main())

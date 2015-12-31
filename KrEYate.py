#!/usr/bin/env python
# KrEYate.py
# quick keypass creation tool
# Version v00.00.01
# Tue 15 Dec 2015 22:07:39
# Leigh Burton, lburton@metacache.net

import sys
import hashlib
from random import randint

inputfile = "input.txt"

keysetup = []

def main():
    x = 0
    try:
        open_input = open(inputfile, "r")
        for i in open_input:
            outhash = hashlib.md5(i).hexdigest()
            keysetup.append(outhash)
            x = x + 1
        print "keys = " + str(keysetup)
    except:
        print "Error Occured"
if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python
# deKrEYpt.py
# quick Key-Deck decryption tool
# Version v1.0.2
# 2/17/2016, 6:20:47 PM
# Copyright (C) 2016 Leigh Burton, leighb2282@gmail.com

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

infile = "bubble_keys.crypt" # Default file to check.
keydecrypted = [] #List we put the decrypted keys into.

def main():
    try:
        cryptokey = raw_input("\033[93mFile Phrase:\033[97m ") # Get the passphrase of the KeyDeck from the user.
        open_keyfile = open(infile, "r") # Open the KeyDeck.
        cryptohash = hashlib.md5(cryptokey).hexdigest() # convert the passphrase the user gave into the hashed version.

        to_decrypt = open_keyfile.read() #read the KeyDeck and place it into a string variable.
        decrypto = AES.new(cryptohash, AES.MODE_CBC, cryptohash[:16]) # Set us the AES protocols read for decryption (hased password used for key and IV).
        decrypted = decrypto.decrypt(str(to_decrypt)) # decrypt the ciphertext.

        keydecrypted = decrypted.replace(" ", "").replace("[", "").replace("]", "").replace("'", "").split(",") # do mad replaces to get rid of the spaces, brackets, and place the result into a list by splitting it  using the comma.
        open_keyfile.close() # close the KeyDeck.
        if keydecrypted[0] == 'VALID': # read the first list item and if it can read as VALID  we decrypted successfully.
            print "Decrypted Successfully"
            del keydecrypted[0] # Delete the first list item ('VALID').
            print "KeyDeck Title: " + keydecrypted[0] # Print the ttle (which is now the first list item).
            del keydecrypted[0] # Delete the first list item (again).
            for key in keydecrypted:    # Iterate through the remaining entries
                print key               # And print them.
        else: # If we don't find 'VALID' in teh first position
            print "Decrypt Failed." # Let user know.
    except:
        print "Error Occured"
if __name__ == '__main__':
    sys.exit(main())

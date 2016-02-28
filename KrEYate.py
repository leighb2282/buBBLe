#!/usr/bin/env python
# KrEYate.py
# quick Key-Deck creation tool
# Version v2.0.1
# 2/17/2016, 5:40:39 PM
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

import wx
import sys
import hashlib
import threading
import time
from Crypto.Cipher import AES

outfile = "bubble_keys.crypt" # Output File.
tctstat = 0 # used to handle state of thread which checks for textCtrl content

def main():
    """ Main entry point for buBBle."""
    class KrEYate(wx.Frame):
        def __init__(self, parent, title):
            wx.Frame.__init__(self, parent, title=title, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MINIMIZE_BOX ^ wx.MAXIMIZE_BOX) # Init the frame, no resze, mini or mani buttons.
            self.Bind(wx.EVT_CLOSE, self.OnClose) # Bind the window 'x'

            panel = wx.Panel(self,wx.ID_ANY) # Create a panel

            self.titlelabel = wx.StaticText(panel, label="   Title: ") # KeyDeck name label
            self.titleBox = wx.TextCtrl(panel, style=wx.TE_LEFT) # Key-Deck name
            self.passlabel = wx.StaticText(panel, label="Password: ") # KeyDeck password label
            self.passBox = wx.TextCtrl(panel, style=wx.TE_LEFT) # Key-Deck password
            self.k0label = wx.StaticText(panel, label="0: ") # Key 0 Label
            self.k0box = wx.TextCtrl(panel, style=wx.TE_LEFT) # Key 0 Textbox

            self.k1label = wx.StaticText(panel, label="1: ") # Key 1 Label
            self.k1box = wx.TextCtrl(panel, style=wx.TE_LEFT) # Key 1 Textbox

            self.k2label = wx.StaticText(panel, label="2: ") # Key 2 Label
            self.k2box = wx.TextCtrl(panel, style=wx.TE_LEFT) # Key 2 Textbox

            self.k3label = wx.StaticText(panel, label="3: ") # Key 3 Label
            self.k3box = wx.TextCtrl(panel, style=wx.TE_LEFT) # Key 3 Textbox

            self.k4label = wx.StaticText(panel, label="4: ") # Key 4 Label
            self.k4box = wx.TextCtrl(panel, style=wx.TE_LEFT) # Key 4 Textbox

            self.k5label = wx.StaticText(panel, label=" :5") # Key 5 Label
            self.k5box = wx.TextCtrl(panel, style=wx.TE_RIGHT) # Key 5 Textbox

            self.k6label = wx.StaticText(panel, label=" :6") # Key 6 Label
            self.k6box = wx.TextCtrl(panel, style=wx.TE_RIGHT) # Key 6 Textbox

            self.k7label = wx.StaticText(panel, label=" :7") # Key 7 Label
            self.k7box = wx.TextCtrl(panel, style=wx.TE_RIGHT) # Key 7 Textbox

            self.k8label = wx.StaticText(panel, label=" :8") # Key 8 Label
            self.k8box = wx.TextCtrl(panel, style=wx.TE_RIGHT) # Key 8 Textbox

            self.k9label = wx.StaticText(panel, label=" :9") # Key 9 Label
            self.k9box = wx.TextCtrl(panel, style=wx.TE_RIGHT) # Key 9 Textbox

            self.okButton = wx.Button(panel, label="Create KeyDeck") # Button to write the Keydeck to file.

            self.Bind(wx.EVT_BUTTON, self.onOK, self.okButton) # Bind for the Create Button.

            #Sizers!
            topSizer        = wx.BoxSizer(wx.VERTICAL) # Outer Sizer.
            keySizer        = wx.BoxSizer(wx.HORIZONTAL) # Holds the keyLSizer and keyRSizer.
            titleSizer      = wx.BoxSizer(wx.HORIZONTAL) # Holds title label and textCtrl.
            passSizer       = wx.BoxSizer(wx.HORIZONTAL) # Holds password label and textCtrl.
            keyLSizer       = wx.BoxSizer(wx.VERTICAL) # Holds left column of key textCtrls.
            keyRSizer       = wx.BoxSizer(wx.VERTICAL) # Holds right column of key textCtrls.
            loc0Sizer       = wx.BoxSizer(wx.HORIZONTAL) # Holds label & textCtrl for key #0
            loc1Sizer       = wx.BoxSizer(wx.HORIZONTAL) # Holds label & textCtrl for key #1
            loc2Sizer       = wx.BoxSizer(wx.HORIZONTAL) # Holds label & textCtrl for key #2
            loc3Sizer       = wx.BoxSizer(wx.HORIZONTAL) # Holds label & textCtrl for key #3
            loc4Sizer       = wx.BoxSizer(wx.HORIZONTAL) # Holds label & textCtrl for key #4
            loc5Sizer       = wx.BoxSizer(wx.HORIZONTAL) # Holds label & textCtrl for key #5
            loc6Sizer       = wx.BoxSizer(wx.HORIZONTAL) # Holds label & textCtrl for key #6
            loc7Sizer       = wx.BoxSizer(wx.HORIZONTAL) # Holds label & textCtrl for key #7
            loc8Sizer       = wx.BoxSizer(wx.HORIZONTAL) # Holds label & textCtrl for key #8
            loc9Sizer       = wx.BoxSizer(wx.HORIZONTAL) # Holds label & textCtrl for key #9
            btnSizer        = wx.BoxSizer(wx.HORIZONTAL) # Holds 'Create' Button.

            titleSizer.Add(self.titlelabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2) # Add title label to the titleSizer
            titleSizer.Add(self.titleBox, 1, wx.ALL|wx.EXPAND, 2) # Add title textCtrl to the titleSizer

            passSizer.Add(self.passlabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2) # Add password label to the passSizer
            passSizer.Add(self.passBox, 1, wx.ALL|wx.EXPAND, 2) # Add password textCtrl to the passSizer

            loc0Sizer.Add(self.k0label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2) # Add key #0 label to the locSizers
            loc0Sizer.Add(self.k0box, 1, wx.ALL|wx.EXPAND, 2) # Add key #0 textCtrl to the locSizers

            loc1Sizer.Add(self.k1label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2) # Add key #1 label to the tlocSizers
            loc1Sizer.Add(self.k1box, 1, wx.ALL|wx.EXPAND, 2) # Add key #1 textCtrl to the locSizers

            loc2Sizer.Add(self.k2label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2) # Add key #2 label to the locSizers
            loc2Sizer.Add(self.k2box, 1, wx.ALL|wx.EXPAND, 2) # Add key #2 textCtrl to the locSizers

            loc3Sizer.Add(self.k3label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2) # Add key #3 label to the locSizers
            loc3Sizer.Add(self.k3box, 1, wx.ALL|wx.EXPAND, 2) # Add key #3 textCtrl to the locSizers

            loc4Sizer.Add(self.k4label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2) # Add key #4 label to the locSizers
            loc4Sizer.Add(self.k4box, 1, wx.ALL|wx.EXPAND, 2) # Add key #4 textCtrl to the locSizers

            loc5Sizer.Add(self.k5box, 1, wx.ALL|wx.EXPAND, 2) # Add key #5 textCtrl to the locSizers
            loc5Sizer.Add(self.k5label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2) # Add key #5 label to the locSizers

            loc6Sizer.Add(self.k6box, 1, wx.ALL|wx.EXPAND, 2) # Add key #6 textCtrl to the locSizers
            loc6Sizer.Add(self.k6label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2) # Add key #6 label to the locSizers

            loc7Sizer.Add(self.k7box, 1, wx.ALL|wx.EXPAND, 2) # Add key #7 textCtrl to the locSizers
            loc7Sizer.Add(self.k7label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2) # Add key #7 label to the locSizers

            loc8Sizer.Add(self.k8box, 1, wx.ALL|wx.EXPAND, 2) # Add key #8 textCtrl to the locSizers
            loc8Sizer.Add(self.k8label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2) # Add key #8 label to the locSizers

            loc9Sizer.Add(self.k9box, 1, wx.ALL|wx.EXPAND, 2) # Add key #9 textCtrl to the locSizers
            loc9Sizer.Add(self.k9label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2) # Add key #9 label to the locSizers

            btnSizer.Add(self.okButton, 0, wx.ALL, 2) # Add Create Button to the btnSizer

            # Add locSizers for key0-4 to the keyLSizer
            keyLSizer.Add(loc0Sizer, 1, wx.ALL|wx.EXPAND, 1)
            keyLSizer.Add(loc1Sizer, 1, wx.ALL|wx.EXPAND, 1)
            keyLSizer.Add(loc2Sizer, 1, wx.ALL|wx.EXPAND, 1)
            keyLSizer.Add(loc3Sizer, 1, wx.ALL|wx.EXPAND, 1)
            keyLSizer.Add(loc4Sizer, 1, wx.ALL|wx.EXPAND, 1)

            # Add locSizers for key5-9 to the keyRSizer
            keyRSizer.Add(loc5Sizer, 1, wx.ALL|wx.EXPAND, 1)
            keyRSizer.Add(loc6Sizer, 1, wx.ALL|wx.EXPAND, 1)
            keyRSizer.Add(loc7Sizer, 1, wx.ALL|wx.EXPAND, 1)
            keyRSizer.Add(loc8Sizer, 1, wx.ALL|wx.EXPAND, 1)
            keyRSizer.Add(loc9Sizer, 1, wx.ALL|wx.EXPAND, 1)

            # Add left and right set of locSizers to the main keySizer
            keySizer.Add(keyLSizer, 1, wx.ALL|wx.EXPAND, 1)
            keySizer.Add(keyRSizer, 1, wx.ALL|wx.EXPAND, 1)

            # put the title, password, keysizer and button sizer all together!
            topSizer.Add(titleSizer, 0, wx.ALL|wx.EXPAND, 0)
            topSizer.Add(passSizer, 0, wx.ALL|wx.EXPAND, 0)
            topSizer.Add(wx.StaticLine(panel, size=(520, 1)), 0, wx.ALL|wx.EXPAND, 0)
            topSizer.Add(keySizer, 1, wx.ALL|wx.EXPAND, 0)
            topSizer.Add(wx.StaticLine(panel, size=(520, 1)), 0, wx.ALL|wx.EXPAND, 0)
            topSizer.Add(btnSizer, 0, wx.ALL|wx.CENTER, 5)

            panel.SetSizer(topSizer) # Connect the panel to the topSizer
            topSizer.Fit(self) # Use the frame's size as the sizer's size.
            self.okButton.Enable(False) # Disable the Create button at start
            panel.Layout()
            self.Show(True) # Show the GUI

            # Function to check if fields are empty, f any field is empty disable the button.
            def thread_tct():
                global tctstat # so we can get tctstat's value
                while tctstat == 0: # Keep going until it isn't '0'
                    # INCOMING SUPER LONG SET OF IF STATEMENTS, THERE HAS TO BE A BETTER WAY!?!?!?!
                    if self.titleBox.GetValue() == "" or self.passBox.GetValue() == "" or self.k0box.GetValue() == "" or self.k1box.GetValue() == "" or self.k2box.GetValue() == "" or self.k3box.GetValue() == "" or self.k4box.GetValue() == "" or self.k5box.GetValue() == "" or self.k6box.GetValue() == "" or self.k7box.GetValue() == "" or self.k8box.GetValue() == "" or self.k9box.GetValue() == "":
                        self.okButton.Enable(False) # Disable Create button until all fields populated.
                    else:
                        self.okButton.Enable(True) # If every textCtrl has stuff in it enable the Create button.
                pass

            tct_d = threading.Thread(name='TextCTRL Check', target=thread_tct) # Setting up the thread (thread runs the thread named 'thread_tct')
            tct_d.start() # Start the thread.

        # Function to close the program
        def OnClose(self,event):
            global tctstat # Imported so we can end the textCtrl checking thread (thread_tct function)
            dlg = wx.MessageDialog(self,                            # Dialog Box
                "Do you really want to close this application?",    # to confirm
                "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)   # User Quit.
            result = dlg.ShowModal() # Get results from dialog box
            dlg.Destroy() # kill Dialog box
            if result == wx.ID_OK: # Checking to see if user confirmed quit
                tctstat = 1 # setting thread status to 1 (kill thread)
                self.Destroy() # Kill GUI
                sys.exit() # Kill everything
            else:
                pass # Just do nothing, User chose not to exit.

        # Function to actually create the Key-Deck!
        def onOK(self, event):
            keysetup = [] # list used for actual generation of they KeyDeck
            rawstore = ['','','','','','','','','',''] # Temp storage of the data from the GUI

            #THis is ugly but basically pulls data from all the textCtrl and dumps it in a specific location in the rawstore list.
            rawstore[0] = self.k0box.GetValue()
            rawstore[1] = self.k1box.GetValue()
            rawstore[2] = self.k2box.GetValue()
            rawstore[3] = self.k3box.GetValue()
            rawstore[4] = self.k4box.GetValue()
            rawstore[5] = self.k5box.GetValue()
            rawstore[6] = self.k6box.GetValue()
            rawstore[7] = self.k7box.GetValue()
            rawstore[8] = self.k8box.GetValue()
            rawstore[9] = self.k9box.GetValue()

            try:
                keysetup.append('VALID') # We add Valid here because this is how the client knows it has decrypted a KeyDeck correctly.
                keysetup.append(self.titleBox.GetValue()) # Grabs the titlebox's content. THis will become more useful when the client can handle oading different keydecks beyond a default one (bubble_keys.crypt)
                for i in rawstore:
                    keysetup.append(hashlib.md5(i).hexdigest()) # Iterate through each list item in rawstore and create a 32char hash of that word, this will become the encryption keys in the client.
                uncrypt = str(keysetup) # probably redundant, but makes a string of the entire list.
                messlen = len(uncrypt) # grabs its length.
                num2fill = 16 - (messlen % 16) # Calculates the number of chars missing to make it divisible by 16.
                tocrypt = (uncrypt + " " * num2fill) # Adds that number to the end (string needs to be divisible by 16 for the cryptography).

                cryptohash = hashlib.md5(self.passBox.GetValue()).hexdigest() # Get the password from the password textctrl and make a 32 char hash of it.
                crypto = AES.new(cryptohash, AES.MODE_CBC, cryptohash[:16]) # Set up the AES encryption using the aforementioned hashed pasword for key and IV (yes I know its bad to use part of the key for the IV)
                encrypted = crypto.encrypt(tocrypt) # Encrypt the keys in the string from above.

                f = open(outfile, "w") # Open the output file for editting
                f.write(str(encrypted)) # write our encrypted string into it.
                f.close() # Close the file for editting.
                mcr = wx.MessageDialog(self,                    # Just informing user of success
                "KeyDeck Created Successfully, Closing App",    # If the process fails at any point
                "Keydeck Complete.", wx.OK|wx.ICON_QUESTION)    # The try: should mean the user doesn't see this
                result = mcr.ShowModal()                        # We could down the road actually check for file
                mcr.Destroy()                                   # And test decrypt it to make sure we can read the 'VALID'
            except:
                print "Error Occured"


    app = wx.App(False)
    frame = KrEYate(None, 'KrEYate - Keydeck Creator')
    app.MainLoop()
    pass


if __name__ == '__main__':
  sys.exit(main())

#!/usr/bin/env python
# buBBle_client.py
# Client for buBBle BBS
# Version v1.0.1
# 2/19/2016, 12:27:44 AM
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
import wx
import os
import sys
import socket
import hashlib
import threading
import time
import base64
import webbrowser

from Crypto.Cipher import AES
from random import randint

vinfo = 'v1.0.1'
# Server IP (or FQDN)
server = "192.168.0.100"

# Network Ports
auth_port = "33751"       # Port used for Authentication.
post_port = "33752"       # Port used for new incoming posts.
pull_port = "33753"       # Port used for requesting posts.

# Various Images (App Icon, in-app buttons)
appicon = "res/bbicon.ico"
srvon = "res/srv_online.png"
srvoff = "res/srv_offline.png"
usron = "res/usr_auth.png"
usroff = "res/usr_unauth.png"

srv_imgon = wx.Image(srvon, wx.BITMAP_TYPE_PNG)
srv_imgoff = wx.Image(srvoff, wx.BITMAP_TYPE_PNG)
usr_imgon = wx.Image(usron, wx.BITMAP_TYPE_PNG)
usr_imgoff = wx.Image(usroff, wx.BITMAP_TYPE_PNG)

# Pull thread related variables
pullT_status = 0 # The status of the thread, 0 = active, 1 = end the thread
pullT_current = 0 # the ID of the latest post pulled from the server
pullT_Newest = 0 # the ID of the newest post ON the server

usr_auth = '0' # Client auth status, 0 is unauthorized, 1 is Authorized

# Key-Deck location for mkeys, v1.0.0 will only have ability to load existing keydeck file created by KrEYate.py.
# User will be asked to enter their Key-Deck passphrase when looking in the KeyDeck options.
# OR when Authenticating against the server (will redirect to Key-Deck options if a key-deck not loaded).
keydeck = "bubble_keys.crypt"

# mKeys is used for message encryption, loaded via a Key-Deck.
mKeys = [] # Holds the different encryption keys.
mKeys_n = len(mKeys) - 1 # Holds the number of keys in mKeys.
mKeys_t = "" # Holds the Key-Deck's Title.
mKeys_s = "" # Holds the Key-Deck's Status.

# aKeys is used for encrypting the authentication string when sending it to the server.
# This really only provides a degree of encryption against on-the-wire attempts at getting credentials.
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


usr_cred = ['','',''] # Location for Username and Password credentials.
#auth_out = "" # Variable to hold Auth string.
auth_str = "" #
post_token = "" # Post Token used to confirm authentication while posting a bulletin

def main():
    """ Main entry point for buBBle."""

    ########################################################
    # Start of Key Deck Options Class code and subroutines #
    ########################################################
    class keydeckFrame(wx.Frame):
        def __init__(self, parent, id):
            global keydeck
            wx.Frame.__init__(self, parent, -1,
                              title="Key-Deck Options",
                              style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MINIMIZE_BOX ^ wx.MAXIMIZE_BOX)
            self.picon = wx.Icon(appicon, wx.BITMAP_TYPE_ICO)
            self.SetIcon(self.picon)
            panel = wx.Panel(self,wx.ID_ANY)

            self.titleBox = wx.TextCtrl(panel, style=wx.TE_LEFT|wx.TE_READONLY) # Key-Deck name

            self.k0label = wx.StaticText(panel, label="0: ") # Key 0 Label
            self.k0box = wx.TextCtrl(panel, style=wx.TE_LEFT|wx.TE_READONLY) # Key 0 Textbox

            self.k1label = wx.StaticText(panel, label="1: ") # Key 1 Label
            self.k1box = wx.TextCtrl(panel, style=wx.TE_LEFT|wx.TE_READONLY) # Key 1 Textbox

            self.k2label = wx.StaticText(panel, label="2: ") # Key 2 Label
            self.k2box = wx.TextCtrl(panel, style=wx.TE_LEFT|wx.TE_READONLY) # Key 2 Textbox

            self.k3label = wx.StaticText(panel, label="3: ") # Key 3 Label
            self.k3box = wx.TextCtrl(panel, style=wx.TE_LEFT|wx.TE_READONLY) # Key 3 Textbox

            self.k4label = wx.StaticText(panel, label="4: ") # Key 4 Label
            self.k4box = wx.TextCtrl(panel, style=wx.TE_LEFT|wx.TE_READONLY) # Key 4 Textbox

            self.k5label = wx.StaticText(panel, label=" :5") # Key 5 Label
            self.k5box = wx.TextCtrl(panel, style=wx.TE_RIGHT|wx.TE_READONLY) # Key 5 Textbox

            self.k6label = wx.StaticText(panel, label=" :6") # Key 6 Label
            self.k6box = wx.TextCtrl(panel, style=wx.TE_RIGHT|wx.TE_READONLY) # Key 6 Textbox

            self.k7label = wx.StaticText(panel, label=" :7") # Key 7 Label
            self.k7box = wx.TextCtrl(panel, style=wx.TE_RIGHT|wx.TE_READONLY) # Key 7 Textbox

            self.k8label = wx.StaticText(panel, label=" :8") # Key 8 Label
            self.k8box = wx.TextCtrl(panel, style=wx.TE_RIGHT|wx.TE_READONLY) # Key 8 Textbox

            self.k9label = wx.StaticText(panel, label=" :9") # Key 9 Label
            self.k9box = wx.TextCtrl(panel, style=wx.TE_RIGHT|wx.TE_READONLY) # Key 9 Textbox

            self.okButton = wx.Button(panel, label="OK")
            #self.cancelButton = wx.Button(panel, label="Cancel")

            self.Bind(wx.EVT_BUTTON, self.onOK, self.okButton)
            #self.Bind(wx.EVT_BUTTON, self.onClose, self.cancelButton)
            self.Bind(wx.EVT_CLOSE, self.onOK)

            #Sizers!
            topSizer        = wx.BoxSizer(wx.VERTICAL) # Outer Sizer.
            keySizer        = wx.BoxSizer(wx.HORIZONTAL) # Holds the keyLSizer and keyRSizer.
            titleSizer      = wx.BoxSizer(wx.HORIZONTAL) # Holds title label and textCtrl.
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

            titleSizer.Add(self.titleBox, 1, wx.ALL|wx.EXPAND, 2) # Add title label to the titleSizer
            titleSizer.Add(self.titleBox, 1, wx.ALL|wx.EXPAND, 2) # Add title textCtrl to the titleSizer

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
            topSizer.Add(wx.StaticLine(panel, size=(520, 1)), 0, wx.ALL|wx.EXPAND, 0)
            topSizer.Add(keySizer, 1, wx.ALL|wx.EXPAND, 0)
            topSizer.Add(wx.StaticLine(panel, size=(520, 1)), 0, wx.ALL|wx.EXPAND, 0)
            topSizer.Add(btnSizer, 0, wx.ALL|wx.CENTER, 5)

            panel.SetSizer(topSizer) # Connect the panel to the topSizer.
            topSizer.Fit(self) # Use the frame's size as the sizer's size.


            self.CenterOnParent() # Center this sub-frame on the parent app's frame.
            self.GetParent().Enable(False) # Disable the main page.
            self.Show(True) # Show the KeyDeck Frame.
            self.onLoad(keydeck) # Invoke the onLoad Function

            if mKeys_s == "VALID": # If we have a valid keydeck after running onLoad.
                self.__eventLoop = wx.EventLoop() # Set up an Event Loop.
                self.__eventLoop.Run() # run said event loop.

        # FUnction to close the KeyDeck frame
        def onOK(self, event):
            self.GetParent().Enable(True) #Enable the main frame
            self.__eventLoop.Exit() # Eit the KeyDeck event loop
            self.Destroy() #Destroy the KeyDeck frame,

        def onLoad(self, event):
            global mKeys_s
            global mKeys_n
            global mKeys_t
            global mKeys
            try:
                if mKeys_s == 'VALID': # CHeck if mKeys_s has been set as 'VALID' if it has set they textCtrl's content to the keys
                    self.titleBox.SetValue(mKeys_t) # get the KeyDeck title and put it in here
                    # The below is kinda ugly but gets the job done, gets all they keys from mKeys and puts em in the right textCtrls
                    self.k0box.SetValue(mKeys[0])
                    self.k1box.SetValue(mKeys[1])
                    self.k2box.SetValue(mKeys[2])
                    self.k3box.SetValue(mKeys[3])
                    self.k4box.SetValue(mKeys[4])
                    self.k5box.SetValue(mKeys[5])
                    self.k6box.SetValue(mKeys[6])
                    self.k7box.SetValue(mKeys[7])
                    self.k8box.SetValue(mKeys[8])
                    self.k9box.SetValue(mKeys[9])
                else: #If a KeyDeck hasn't already been loaded, load it!
                    dlg = wx.TextEntryDialog(None,"Enter Key-Deck's Passphrase") # Simple dialog to get user' password.
                    ret = dlg.ShowModal() # plop the dialog's return code to 'ret'

                    if ret == wx.ID_OK: # If they pressed ok...
                        cryptokey = dlg.GetValue() # Get the input and dump it in cryptokey.
                        open_keyfile = open(keydeck, "r") # Open the KeyDeck file for read access.
                        cryptohash = hashlib.md5(cryptokey).hexdigest() # Hash the password they entered.
                        to_decrypt = open_keyfile.read() # Throw the ciphertext into to_decrypt.
                        decrypto = AES.new(cryptohash, AES.MODE_CBC, cryptohash[:16]) # Set us the AES protocols read for decryption (hased password used for key and IV).
                        decrypted = decrypto.decrypt(str(to_decrypt)) # decrypt the ciphertext.

                        mKeys = decrypted.replace(" ", "").replace("[", "").replace("]", "").replace("'", "").split(",") # do mad replaces to get rid of the spaces, brackets, and place the result into a list by splitting it  using the comma.
                        open_keyfile.close()# close the KeyDeck.

                        if mKeys[0] == 'VALID': # read the first list item and if it can read as VALID  we decrypted successfully.
                            mKeys_s = mKeys[0] # put the 0 location content into mKeys_s ('valid').
                            del mKeys[0] # Delete the first list item ('VALID').
                            mKeys_t = mKeys[0] # put the 0 location content into mKeys_t (KeyDeck title).
                            self.titleBox.SetValue(mKeys_t) # Set the titleBox textCtrl to mKeys_t.
                            del mKeys[0] # Delete the first list item (KeyDeck title).
                            mKeys_n = len(mKeys) -1 # find out the number of keys (we -1 because we address the keys starting at 0 not 1)
                            # The below is kinda ugly but gets the job done, gets all they keys from mKeys and puts em in the right textCtrls
                            self.k0box.SetValue(mKeys[0])
                            self.k1box.SetValue(mKeys[1])
                            self.k2box.SetValue(mKeys[2])
                            self.k3box.SetValue(mKeys[3])
                            self.k4box.SetValue(mKeys[4])
                            self.k5box.SetValue(mKeys[5])
                            self.k6box.SetValue(mKeys[6])
                            self.k7box.SetValue(mKeys[7])
                            self.k8box.SetValue(mKeys[8])
                            self.k9box.SetValue(mKeys[9])
                        else: #If a KeyDeck once it has been decrypted can't be read inform user via dialog.
                            ips = wx.MessageDialog(self,
                            "Invalid Passphrase entered.",
                            "Decrypt Failed", wx.OK|wx.ICON_QUESTION)
                            result = ips.ShowModal()
                            ips.Destroy() # Destroy Dialog.
                            self.GetParent().Enable(True) # Enable the parent frame again (the actual app).
                            self.Destroy() # Destroy the KeyDeck frame.
                    else: # If they just close the password request.
                        dlg.Destroy() # Kill the password dialog.
                        self.GetParent().Enable(True) # Enable the parent frame again (the actual app).
                        self.Destroy() # Destroy the KeyDeck frame.
                    dlg.Destroy() # Kill the password dialog.
            except:
                print "Error Occured"

    ##################################################
    # Start of AboutFrame Class code and subroutines #
    ##################################################
    class AboutFrame(wx.Frame):
        ''' AboutFrame launched from Menu '''
        def __init__(self, parent, id):
            wx.Frame.__init__(self, parent, -1, title="About BuBBle", style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MINIMIZE_BOX ^ wx.MAXIMIZE_BOX)

            # Set the App's Icon
            self.picon = wx.Icon(appicon, wx.BITMAP_TYPE_ICO)
            self.SetIcon(self.picon)

            panel = wx.Panel(self, -1)  # Create a panel for GUI awesomeness.

            blogo = wx.EmptyImage(64,64) # Create an empty image to host our icon.
            blogo = wx.Image(appicon, wx.BITMAP_TYPE_ICO) # Add our app icon to the image.
            self.bubb = wx.StaticBitmap(panel, wx.ID_ANY, wx.BitmapFromImage(blogo)) # Add a StaticBitmap to our panel with our app icon.

            self.titlelabel = wx.StaticText(panel, label="BuBBle Client " + vinfo) # Title label.
            titleFont = wx.Font(20, wx.DECORATIVE, wx.NORMAL, wx.BOLD) # set up text attributes.
            self.titlelabel.SetFont(titleFont) # Set them for the title.

            self.blurb1label = wx.StaticText(panel, label=" BuBBle Client is the client-side app for the 'BuBBlesphere' ")  # A brief synopsys of buBBle
            self.blurb2label = wx.StaticText(panel, label="The BuBBlesphere includes the client, server and utilities.")    # Obviously more will be explained on Github.
            blurbFont = wx.Font(10, wx.DECORATIVE, wx.NORMAL, wx.NORMAL) # set up text attributes.
            self.blurb1label.SetFont(blurbFont) # Set them for the blurby blurb.
            self.blurb2label.SetFont(blurbFont) # Set them for the blurby blurb.

            self.copyrlabel = wx.StaticText(panel, label="Copyright 2016 Leigh Burton") # copyright Label
            copyFont = wx.Font(8, wx.DECORATIVE, wx.NORMAL, wx.NORMAL) # set up text attributes.
            self.copyrlabel.SetFont(copyFont)# Set em for the copyright notice.

            self.closeButton = wx.Button(panel, label="Close", pos=(210, 235)) # Close button!

            self.Bind(wx.EVT_BUTTON, self.onClose, self.closeButton) # Bind the close button.
            self.Bind(wx.EVT_CLOSE, self.onClose) # (Allows frame's title-bar close to work)

            # Sizers!
            topSizer        = wx.BoxSizer(wx.VERTICAL)
            iconSizer      = wx.BoxSizer(wx.HORIZONTAL)
            appverSizer   = wx.BoxSizer(wx.HORIZONTAL)
            blurb1Sizer   = wx.BoxSizer(wx.VERTICAL)
            blurb2Sizer   = wx.BoxSizer(wx.VERTICAL)
            copySizer   = wx.BoxSizer(wx.HORIZONTAL)
            btnSizer        = wx.BoxSizer(wx.HORIZONTAL)

            #Sub-SIzers!
            iconSizer.Add(self.bubb, 0, wx.ALL, 5)
            appverSizer.Add(self.titlelabel, 0, wx.ALL, 5)
            blurb1Sizer.Add(self.blurb1label, 0, wx.ALL, 0)
            blurb2Sizer.Add(self.blurb2label, 0, wx.ALL, 0)
            copySizer.Add(self.copyrlabel, 0, wx.ALL, 5)
            btnSizer.Add(self.closeButton, 0, wx.ALL, 5)

            #Add thsoe Sub-Sizers to TopSizer!
            topSizer.Add(iconSizer, 0, wx.CENTER)
            topSizer.Add(appverSizer, 0, wx.CENTER, 5)
            topSizer.Add(blurb1Sizer, 0, wx.CENTER, 5)
            topSizer.Add(blurb2Sizer, 0, wx.CENTER, 5)
            topSizer.Add(copySizer, 0, wx.CENTER, 5)
            topSizer.Add(btnSizer, 0, wx.ALIGN_RIGHT, 5)

            panel.SetSizer(topSizer) # Connect the panel to the topSizer.
            topSizer.Fit(self) # Use the frame's size as the sizer's size.

            self.CenterOnParent() # Center the about on top of the bubble frame.
            self.GetParent().Enable(False) # Disable the main frame.
            self.Show(True) # Show the about page!

            self.__eventLoop = wx.EventLoop() # Create an event loopy.
            self.__eventLoop.Run() # RUn it!

        def onClose(self, event):
            self.GetParent().Enable(True) # Enable the main frame.
            self.__eventLoop.Exit() # Exit the event loop.
            self.Destroy() # destroy the about frame.

    ################################################
    # Start of Main GUI Class code and subroutines #
    ################################################
    class buBBle_client(wx.Frame):
        def __init__(self, parent, title):
            wx.Frame.__init__(self, parent, title=title, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MINIMIZE_BOX ^ wx.MAXIMIZE_BOX) # Init the frame.

            self.Bind(wx.EVT_CLOSE, self.OnClose) # Bind the 'x' to the OnClose function.

            # Set App's Icon.
            self.picon = wx.Icon(appicon, wx.BITMAP_TYPE_ICO)
            self.SetIcon(self.picon)

            menuBar = wx.MenuBar() # We Want Menus!

            # Define the File Menu.
            f_menu = wx.Menu()
            self.f_keys = f_menu.Append(wx.ID_SAVE, "&Key-Deck\tAlt-K", "Key-Deck Options") # to load a KeyDeck.
            #self.f_save = f_menu.Append(wx.ID_SAVE, "&Save\tAlt-S", "Save Chatlog.") # Chatlog will be added eventually.
            self.f_exit = f_menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.") # Self explainatory.

            self.Bind(wx.EVT_MENU, self.OnKeyOpts, self.f_keys) # Bind KeyDeck-Options to OnKeyOpts function.
            self.Bind(wx.EVT_MENU, self.OnClose, self.f_exit) # Bind te Exit menu option to OnClose.
            menuBar.Append(f_menu, "&File") # Append the file menu to the menubar.

            # Define the Help Menu
            h_menu = wx.Menu()
            self.h_about = h_menu.Append(wx.ID_ABOUT, "About", "About buBBle.") # Quick and dirty about page link
            self.h_github = h_menu.Append(wx.ID_VIEW_DETAILS, "GitHub", "Github Project page.") # Link to the Github repo for the project.
            self.Bind(wx.EVT_MENU, self.OnAbout, self.h_about) # Bind the about menu option to OnAbout.
            self.Bind(wx.EVT_MENU, self.OnGitHub, self.h_github) # Bind the about menu option to OnAbout.
            menuBar.Append(h_menu, "&Help") # Append the Help menu to the menubar.

            self.SetMenuBar(menuBar) # Set menuBar as THE menubar.

            panel = wx.Panel(self) # Create a panel for GUI awesomeness.

            emptyimg = wx.EmptyImage(32,32) # Just set up an empty image.

            self.statusbar = self.CreateStatusBar() # Define the Status Bar.

            # Text boxes for Username and Password.
            self.userLabel = wx.StaticText(panel, label="Username:", size=(65, -1), style=wx.ALIGN_RIGHT) # Username label.
            self.userBox = wx.TextCtrl(panel, 5150, size=(265, -1), style=wx.TE_LEFT) # Username Textbox.
            self.passLabel = wx.StaticText(panel, label="  Password:", size=(65, -1), style=wx.ALIGN_RIGHT) # Password Label.
            self.passBox = wx.TextCtrl(panel, 5151, size=(265, -1), style=wx.TE_PASSWORD) # Password Textbox.

            # Authenticate button and server status image.
            self.connButton = wx.Button(panel, size=(100, -1), label="AUTH!") # Auth Button.
            self.Bind(wx.EVT_BUTTON, self.OnAuth, self.connButton) # Bind the above auth button to the OnAuth function.

            self.usrstatBitmap = wx.StaticBitmap(panel, wx.ID_ANY, wx.BitmapFromImage(usr_imgoff)) # The User status icon.
            self.srvstatBitmap = wx.StaticBitmap(panel, wx.ID_ANY, wx.BitmapFromImage(emptyimg)) # The Server status icon.

            # Chat box, Message box and Send Button.
            self.chatBox = wx.TextCtrl(panel, 5250, size=(500, 300), style=wx.TE_LEFT|wx.TE_MULTILINE|wx.TE_READONLY) # Chat Textbox.
            self.messageBox = wx.TextCtrl(panel, 5251, size=(-1, 50),style=wx.TE_LEFT|wx.TE_MULTILINE) # Message Textbox.
            self.sendButton = wx.Button(panel, label="SEND!") # Send button.

            # Binds!
            self.userBox.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseOver) #Hover On Refresh
            self.userBox.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave) #Hover Off Refresh
            self.passBox.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseOver) #Hover On Refresh
            self.passBox.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave) #Hover Off Refresh
            self.chatBox.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseOver) #Hover On Refresh
            self.chatBox.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave) #Hover Off Refresh
            self.messageBox.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseOver) #Hover On Refresh
            self.messageBox.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave) #Hover Off Refresh
            self.Bind(wx.EVT_BUTTON, self.OnSend, self.sendButton) # Bind the send button to the OnSend function.

            # Disable a bunch of the UI because the user shouldn't be able to access it until certain requirements are met.
            # THose requirements are tested in the thread_srvstat function.
            self.messageBox.Enable(False)
            self.messageBox.Enable(False)
            self.sendButton.Enable(False)
            self.userBox.Enable(False)
            self.passBox.Enable(False)
            self.connButton.Enable(False)

            # Sizers!
            topSizer        = wx.BoxSizer(wx.VERTICAL)
            upperSizer      = wx.BoxSizer(wx.HORIZONTAL)
            loginSizer      = wx.BoxSizer(wx.VERTICAL)
            statSizer       = wx.BoxSizer(wx.VERTICAL)
            userSizer       = wx.BoxSizer(wx.HORIZONTAL)
            passSizer       = wx.BoxSizer(wx.HORIZONTAL)
            midSizer        = wx.BoxSizer(wx.HORIZONTAL)
            lowerSizer      = wx.BoxSizer(wx.HORIZONTAL)

            # Add stuff to userSizer.
            userSizer.Add(self.userLabel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 2)
            userSizer.Add(self.userBox, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 2)

            # Add stuff to passSizer.
            passSizer.Add(self.passLabel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 2)
            passSizer.Add(self.passBox, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 2)

            # Add stuff to statSizer.
            statSizer.Add(self.usrstatBitmap, 0, wx.ALL|wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL, 2)
            statSizer.Add(self.srvstatBitmap, 0, wx.ALL|wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL, 2)

            # Add stuff to loginSizer.
            loginSizer.Add(userSizer, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 2)
            loginSizer.Add(passSizer, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 2)

            # Add stuff to upperSizer.
            upperSizer.Add(loginSizer, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 2)
            upperSizer.Add(self.connButton,  0, wx.ALL|wx.ALIGN_CENTER|wx.EXPAND, 5)
            upperSizer.Add(statSizer, 0, wx.ALL|wx.EXPAND, 2)

            # Add stuff to the midSizer.
            midSizer.Add(self.chatBox, 1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 2)

            # Add stuff to lower Sizer.
            lowerSizer.Add(self.messageBox, 1, wx.ALL|wx.EXPAND, 0)
            lowerSizer.Add(self.sendButton, 0, wx.RIGHT|wx.EXPAND, 0)

            # Add stuff to topSizer.
            topSizer.Add(upperSizer, 0, wx.ALL|wx.EXPAND, 2)
            topSizer.Add(midSizer, 0, wx.ALL|wx.EXPAND, 2)
            topSizer.Add(lowerSizer, 0, wx.ALL|wx.EXPAND, 2)

            panel.SetSizer(topSizer) # Connect the panel to the topSizer.
            topSizer.Fit(self) # Use the frame's size as the sizer's size.

            panel.Layout()
            self.Show(True) # Show the main GUI!.

            # The thread_srvstat function, is nvoked as a thread.
            # Its use is to check to see if it can reach the server.
            # It also checks to see if the client has been authenticated.
            # It also invoked the OnPull function which is what actually checks for new posts.
            # Finally, it also handles actuall quitting of the app.
            def thread_srvstat():
                global pullT_status # status variable for the thread 0 means keep going, anything other than 0 to quit.

                try:
                    while pullT_status == 0: # if 0 (active) run me some stuff.
                        srvping = os.system("ping -W 1 -qc 1 " + server + "> /dev/null 2>&1") # Ping the server, 1 time, wait for 1 second.
                        if srvping == 0: # if it comes back 0 (good) run more stuff.
                            self.srvstatBitmap.SetBitmap(wx.BitmapFromImage(srv_imgon)) # Set the server status icon to on.
                            if usr_auth == '0': # If the user auth = 0 (not authenticated).
                                self.messageBox.Enable(False) # Disable the messagebox.
                                self.sendButton.Enable(False) # Disable the send button.
                                self.userBox.Enable(True) # Keep the username textCtrl enabled.
                                self.passBox.Enable(True) # Keep the password textCtrl enabled.
                                self.connButton.Enable(True) # Keep the Authenticate button enabled.
                            elif usr_auth == '1': # if the usr_auth = 1 (authenticated).
                                self.messageBox.Enable(True) # Enable the messagebox so people can type a message.
                                self.sendButton.Enable(True) # Enable the send button so people can actually send a message.
                                self.userBox.Enable(False) # Disable the username textCtrl.
                                self.passBox.Enable(False) # Disable the username textCtrl.
                                self.connButton.Enable(False) # Disable the Authenticate button.
                                self.OnPull(1) # Invoke the OnPull function identifying as 1 (the request was from the continually checking thread).
                        else: # If we don't get a '0' back from the ping test...
                            self.srvstatBitmap.SetBitmap(wx.BitmapFromImage(srv_imgoff)) # Set teh server's icon to not reachable.
                            self.messageBox.Enable(False) # disable the message textCtrl.
                            self.sendButton.Enable(False) # disable the send Button.
                            self.userBox.Enable(False) # Disable the username textCtrl.
                            self.passBox.Enable(False) # Disable the password textCtrl.
                            self.connButton.Enable(False) # Disable the connection Button.
                        time.sleep(2) # Sleep 2 seconds (to avoid flooding the server).
                except:
                    print "Error in Daemon."
                self.Destroy() # If the pullT_status set set to anything other than 0 the while loop will end and dump us here destorying the GUI.
                sys.exit() # As well as the whole script.

            srv_d = threading.Thread(name='recv thread', target=thread_srvstat) # Setting up the thread to check server and grab posts.
            srv_d.start()

        # File>Key-Deck Options.
        def OnKeyOpts(self,event):
            dialog = keydeckFrame(self, -1) # This invokes the KeyDeck frame, I don't actually think that returns anything to truly capture in the dialog variable however.

        # Help>About
        def OnAbout(self,event):
            dialog = AboutFrame(self, -1) # This invokes the About Frame

        # Help>GitHub
        def OnGitHub(self, event):
            gh_href = "https://github.com/leighb2282/buBBLe" # Set the Github URL for the project.
            webbrowser.open(gh_href) # Open that in the defualt browser.

        # OnPull function to get posts from server This is the function that actually pulls posts.
        def OnPull(self, event):
            global pullT_current
            global pullT_Newest
            try:
                token_sel = ['',''] # list to hold which keys are used for AES key and IV for the Token.
                post_sel = ['',''] # list to hold the scraped auth keys used.
                token_sel[0] = randint(0,aKeys_n) # Choose a random key from 0 to aKeys_n for AES encrypt key.
                token_sel[1] = randint(0,aKeys_n) # Choose a random key from 0 to aKeys_n for AES IV.
                token_crypt = AES.new(aKeys[token_sel[0]], AES.MODE_CBC, aKeys[token_sel[1]][:16]) # Set up the AES encryption.
                token_enc = str(token_sel[0]) + token_crypt.encrypt(post_token) + str(token_sel[1]) #ncrypt the token ready to send to the server.
                self.pull_conn = socket.socket() # Create a socket.
                self.pull_conn.connect((server, int(pull_port))) #create a socket connection to the server and pull port.
                self.pull_conn.send(token_enc) # Send the ciphertext'ed token.
                token_resp = self.pull_conn.recv(1024).split('|') # Receieve a response from the server splitting its results. (first split will be auth status, second will be newest post #).

                if token_resp[0] == '1': # If token exists:
                    pullT_Newest = token_resp[1] # Set the newest post variable to the number help in token_resp[1] (the second split from above).
                    if int(pullT_current) == int(pullT_Newest): # If the currently displayed message is the newest...
                        self.pull_conn.send('axe') # Send an 'axe' message to teh server indicating it should stop.
                    else:
                        pullT_post = pullT_current + 1 # Get teh NEXT post.
                        self.pull_conn.send(str(pullT_post)) # Send to the server what post the client needs.
                        post_return = base64.b64decode(self.pull_conn.recv(1024)) # Recieve all that information (which will come base64 encoded.) and decode that.
                        post_split = post_return.split('|') # Split the recieved info at the | marks.
                        pullT_current = pullT_current + 1 # Increment the current post.
                        if post_split[0] == 'v': # the first split is a 'v' or 'd', 'v' indicates it is a viewable message and therefore encrypted.
                            post = base64.b64decode(post_split[3]) # decode the 'content' part of the string, its saved base64 encoded in the database,
                            post_sel[0] = post[:1:1] # AES key Token is the first char.
                            post_sel[1] = post[-1:] # AES IV is the last char.
                            post_t = post[1:-1] # Actual post data is between the key and IV,
                            msg_dec = AES.new(mKeys[int(post_sel[0])], AES.MODE_CBC, mKeys[int(post_sel[1])][:16]) # Set up the AES protocol with the scraped keys..
                            post_decrypted = msg_dec.decrypt(post_t) #Decrypt that stuff!
                            self.chatBox.AppendText('#' + str(post_split[1]) + ': ' + str(post_split[2]) + ': ' + str(post_split[4]).strip() + '\n' + str(post_decrypted).strip() + '\n') # Display!
                        elif post_split[0] == 'd':
                            # If we recieve a 'd' instead of a 'v' that means in the database something/someone has marked the message private.
                            # This means the ciphertext message wasn't included in the recieved string and we can just post the 'Content Marked Private' message
                            self.chatBox.AppendText('#' + str(post_split[1]) + ': ' + str(post_split[2]) + ': ' + str(post_split[4]).strip() + '\n' + str(post_split[3]).strip() + '\n') # Display!
            except:
                print "FAIL SILENTLY!!!! (THIS IS NOT SILENT BTW)"
            self.pull_conn.shutdown(socket.SHUT_RDWR) # Shutdown the pull connection.
            self.pull_conn.close() # Close hte pull connection.

        # OnAuth function used to send a message to the server
        def OnAuth(self, event):
            global mKeys_s
            global keydeck
            global usr_auth
            global usr_cred
            global auth_str
            global post_token

            auth_sel = ['',''] # Set up a list to hold the randomized key identifiers.

            if mKeys_s == "VALID": # If we have a KeyDeck Loaded try to authenticate.
                ###########################################
                # THIS IS WHERE WE START THE AUTH PROCESS #
                ###########################################
                usr_cred[0] = self.userBox.GetValue() # Place Username textbox data into the usr_cred list.
                usr_cred[1] = self.passBox.GetValue() # Place Password textbox data into the usr_cred list.

                if usr_cred[0] == '' or usr_cred[1] == '': # Check if we have any empty Usr/Pass textboxes.
                    # If we end up here it is because username or password was empty.
                    mcr = wx.MessageDialog(self,
                    "Username or Password fields Empty.",
                    "Empty Fields!", wx.OK|wx.ICON_QUESTION)
                    result = mcr.ShowModal() # Display Dialog informing empty fields.
                    mcr.Destroy() # Kill Dialog.
                else:
                    # If we end up here both username and password had *something* in them.
                    # Now to write functionality to check against database!
                    usr_cred[2] = usr_cred[0] + "/" + hashlib.md5(usr_cred[1]).hexdigest() # We basically add the username, an '/' character and the hashed password into the list in position [2].
                    authlen = len(usr_cred[2]) # grabs the length of the auth string.
                    auth2fill = 16 - (authlen % 16) # Calculates the number of chars missing to make it divisible by 16.
                    auth_str = (usr_cred[2] + " " * auth2fill) # Adds that number to the end (string needs to be divisible by 16 for the cryptography).

                    auth_sel[0] = randint(0,aKeys_n) # generate a random number from 0 - aKeys_n, for the random selection of a key for AES encrypton.
                    auth_sel[1] = randint(0,aKeys_n) # generate a random number from 0 - aKeys_n, for the random selection of an IV for AES encrypton.

                    acrypt = AES.new(aKeys[auth_sel[0]], AES.MODE_CBC, aKeys[auth_sel[1]][:16]) # Set up the AES protocol with the chosen keys.
                    auth_out = str(auth_sel[0]) + acrypt.encrypt(auth_str) + str(auth_sel[1]) # Encrypt the Auth string and place the ciphertext into auth_out.

                    # Yep, actual server auth request is handled via a separate function!
                    # That way it can also be used when sending a message and requesting the message list.
                    usr_auth_token = self.AuthPush(auth_out) # Invoke the AuthPush function giving it the auth string ciphertext as input.

                    if usr_auth_token[:1] == '1': # Check to see if server authenticated.
                        # If we end up here we were successful.
                        usr_auth = '1' # make the global auth variable 1, meaning authenticated.
                        token_encrypted = usr_auth_token[1:] # encrypted token is the usr_auth_token minus first char. (which we used to let the client know if it was authed.)
                        key_token = token_encrypted[:1:1] # AES key Token is the first char.
                        iv_token = token_encrypted[-1:] # AES IV is the last char.
                        token_dec = AES.new(aKeys[int(key_token)], AES.MODE_CBC, aKeys[int(iv_token)][:16]) # Set up the AES protocol with the stripped details from above.
                        post_token = token_dec.decrypt(token_encrypted[1:-1]) # Decrypt the ciphertext token (not including the first and last chars).
                        aac = wx.MessageDialog(self,
                        "Authentication Successful, You may now send and recieve bulletins from the server",
                        "Authentication Successful.", wx.OK|wx.ICON_QUESTION)
                        result = aac.ShowModal() # Display Dialog informing empty fields.
                        aac.Destroy() # Kill Dialog.
                        self.usrstatBitmap.SetBitmap(wx.BitmapFromImage(usr_imgon)) # Set the user status icon to authenticated/blue dude.
                    else: # if we don't recieve auth successful.
                        adc = wx.MessageDialog(self, # Display an 'auth failed' message dialog.
                        "Authentication Failed, Please Try Again",
                        "Authentication Failed.", wx.OK|wx.ICON_QUESTION)
                        result = adc.ShowModal()
                        adc.Destroy() # kill the message dialog.

            else: # If no Key-Deck is loaded inform the user and push them to the Key-Deck Options.
                mcd = wx.MessageDialog(self,
                "No Key-Deck has been Loaded, please enter your Keydeck passphrase to continue.",
                "No Key-Deck Loaded", wx.OK|wx.ICON_QUESTION)
                result = mcd.ShowModal() # Display Dialog informing empty fields.
                mcd.Destroy() # Kill Dialog.
                self.OnKeyOpts(keydeck)

        # AuthPush function used check credentials against server.
        # This is invoked from inside the OnAuth function.
        def AuthPush(self, auth_string):
            try:
                self.auth_conn = socket.socket() # Create a socket.
                self.auth_conn.connect((server, int(auth_port))) # Connect to the specificed server via the auth port.
                self.auth_conn.send(auth_string) # Send the Auth string ciphertext.
                srv_resp = self.auth_conn.recv(1024) # recieve a response from the server with the results of the auth request.
                self.auth_conn.shutdown(socket.SHUT_RDWR) # Shutdown the socket.
                self.auth_conn.close() # Close the socket.
                return srv_resp # Return the server's response back to the OnAuth function.
            except:
                return '0'

        # OnSend function used to send a message to the server
        def OnSend(self, event):
            mesk = ['','']
            # With Authentication handled and a token provided we can now push messages to the server.
            # Using the token for authentication.
            if self.messageBox.GetValue() == '': # Check if we have any empty Usr/Pass textboxes.
                # If we end up here it is because username or password was empty.
                mcr = wx.MessageDialog(self,
                "You currently have no text in your messagebox, please add your message.",
                "Empty MessageBox!", wx.OK|wx.ICON_QUESTION)
                result = mcr.ShowModal() # Display Dialog informing empty fields.
                mcr.Destroy() # Kill Dialog.
            else:
                try:
                    token_sel = ['',''] # list to hold which keys are used for AES key and IV for the Token.
                    token_sel[0] = randint(0,aKeys_n) # Choose a random key from 0 to aKeys_n for AES encrypt key.
                    token_sel[1] = randint(0,aKeys_n) # Choose a random key from 0 to aKeys_n for AES IV.
                    token_crypt = AES.new(aKeys[token_sel[0]], AES.MODE_CBC, aKeys[token_sel[1]][:16]) # Set up the AES encryption.
                    token_enc = str(token_sel[0]) + token_crypt.encrypt(post_token) + str(token_sel[1]) #ncrypt the token ready to send to the server.
                    self.post_conn = socket.socket() # Create a socket.
                    self.post_conn.connect((server, int(post_port))) #create a socket connection to the server and post port.
                    self.post_conn.send(token_enc) # Send the ciphertext'ed token.
                    token_resp = self.post_conn.recv(1024) # Receieve a response from the server.
                    if token_resp == '1': # If we get a response of '1' (token exists)
                        msg = self.messageBox.GetValue() # Put the contents of the message textCtrl into 'msg'
                        mesk[0] = randint(0,mKeys_n) # Choose a random key from 0 to mKeys_n for AES encrypt key.
                        mesk[1] = randint(0,mKeys_n) # Choose a random key from 0 to mKeys_n for AES IV.
                        messlen = len(msg) # Get the length of the message
                        num2fill = 16 - (messlen % 16) # Calculates the number of chars missing to make it divisible by 16.
                        msg = (msg + " " * num2fill) # Adds that number to the end (string needs to be divisible by 16 for the cryptography).
                        post_crypt = AES.new(mKeys[mesk[0]], AES.MODE_CBC, mKeys[mesk[1]][:16]) # Set up the AES protocol with the chosen keys.
                        post_enc = str(mesk[0]) + post_crypt.encrypt(msg) + str(mesk[1]) # Encrypt the Auth string and place the ciphertext into auth_out.
                        self.post_conn.send(post_enc) # Send the ciphertext message to the post thread on the server.
                        self.messageBox.SetValue('') # Reset the messagebox to blank ready for a new message.
                        self.OnPull(0) # Invoke OnPull to get any new messages.
                    self.post_conn.shutdown(socket.SHUT_RDWR) # Shutdown the socket.
                    self.post_conn.close() # Close the socket.
                except:
                    print "Send Failed"

        # OnMouseOver functions for widgets.
        # This is to give the user some direction.
        def OnMouseOver(self,event):
            widget_id = event.GetId()
            if widget_id == 5150: # The username textCtrl
                self.statusbar.SetStatusText('Please type your username here.')
            elif widget_id == 5151: # The password textCtrl
                self.statusbar.SetStatusText('Please type your password here.')
            elif widget_id == 5250: # The chat textCtrl
                self.statusbar.SetStatusText('The Posts will appear here.')
            elif widget_id == 5251: # The message textCtrl
                self.statusbar.SetStatusText('Type in your message to send here.')

        # OnMouseLeave function for widgets.
        # This is to clear the status bar (after a mouseover for a widget).
        def OnMouseLeave(self,event):
            self.statusbar.SetStatusText('')

        # OnClose Function called when a user closes the encoder.
        def OnClose(self,event):
            global pullT_status
            dlg = wx.MessageDialog(self,                            # We confirm with the user if they truly want to quit.
                "Do you really want to close this application?",    # Because I don't want to be an ass and just quit it.
                "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_OK:
                pullT_status = 1 # Send a status of 1 to the pullT_status thread which handles ending app.
            else:
                pass # Just do nothing, User chose not to exit.

    app = wx.App(False)
    frame = buBBle_client(None, 'buBBle BBS Client')
    app.MainLoop()
    pass


if __name__ == '__main__':
    sys.exit(main())

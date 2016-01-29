#!/usr/bin/env python
# buBBle_client.py
# Client for buBBle BBS
# Version v0.2.1
# 1/28/2016, 8:21:55 PM
# Leigh Burton, lburton@metacache.net

# Import modules
import wx
import os
import sys
import socket
import hashlib
import threading
import time

from Crypto.Cipher import AES
from random import randint

# Server IP (or FQDN)
server = "192.168.0.100"

# Network Ports
auth_port = "33751"       # Port used for Authentication.
push_port = "33752"       # Port used for new incoming posts.
pull_port = "33753"       # Port used for requesting posts.

# Various Images (App Icon, in-app buttons)
appicon = "res/bbicon.ico"
srvon = "res/srv_online.png"
srvoff = "res/srv_offline.png"
usron = "res/usr_auth.png"
usroff = "res/usr_unauth.png"

# Pull thread status code
pullT_status = 0

# Status codes for Auth status and server status.
usr_auth = '0' # 0 is unauthorized, 1 is Authorized
srv_stat = '0' # 0 is Offline, 1 is Online

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

# Location for Username and Password credentials.
usr_cred = ['','','']

# Variable to hold Auth string.
auth_out = ""

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
            self.Bind(wx.EVT_CLOSE, self.onClose)

            #Sizers!
            topSizer        = wx.BoxSizer(wx.VERTICAL)
            keySizer      = wx.BoxSizer(wx.HORIZONTAL)
            titleSizer      = wx.BoxSizer(wx.HORIZONTAL)
            keyLSizer      = wx.BoxSizer(wx.VERTICAL)
            keyRSizer      = wx.BoxSizer(wx.VERTICAL)
            loc0Sizer   = wx.BoxSizer(wx.HORIZONTAL)
            loc1Sizer   = wx.BoxSizer(wx.HORIZONTAL)
            loc2Sizer   = wx.BoxSizer(wx.HORIZONTAL)
            loc3Sizer   = wx.BoxSizer(wx.HORIZONTAL)
            loc4Sizer   = wx.BoxSizer(wx.HORIZONTAL)
            loc5Sizer   = wx.BoxSizer(wx.HORIZONTAL)
            loc6Sizer   = wx.BoxSizer(wx.HORIZONTAL)
            loc7Sizer   = wx.BoxSizer(wx.HORIZONTAL)
            loc8Sizer   = wx.BoxSizer(wx.HORIZONTAL)
            loc9Sizer   = wx.BoxSizer(wx.HORIZONTAL)
            btnSizer        = wx.BoxSizer(wx.HORIZONTAL)

            titleSizer.Add(self.titleBox, 1, wx.ALL|wx.EXPAND, 2)

            loc0Sizer.Add(self.k0label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)
            loc0Sizer.Add(self.k0box, 1, wx.ALL|wx.EXPAND, 2)

            loc1Sizer.Add(self.k1label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)
            loc1Sizer.Add(self.k1box, 1, wx.ALL|wx.EXPAND, 2)

            loc2Sizer.Add(self.k2label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)
            loc2Sizer.Add(self.k2box, 1, wx.ALL|wx.EXPAND, 2)

            loc3Sizer.Add(self.k3label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)
            loc3Sizer.Add(self.k3box, 1, wx.ALL|wx.EXPAND, 2)

            loc4Sizer.Add(self.k4label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)
            loc4Sizer.Add(self.k4box, 1, wx.ALL|wx.EXPAND, 2)

            loc5Sizer.Add(self.k5box, 1, wx.ALL|wx.EXPAND, 2)
            loc5Sizer.Add(self.k5label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)

            loc6Sizer.Add(self.k6box, 1, wx.ALL|wx.EXPAND, 2)
            loc6Sizer.Add(self.k6label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)

            loc7Sizer.Add(self.k7box, 1, wx.ALL|wx.EXPAND, 2)
            loc7Sizer.Add(self.k7label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)

            loc8Sizer.Add(self.k8box, 1, wx.ALL|wx.EXPAND, 2)
            loc8Sizer.Add(self.k8label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)

            loc9Sizer.Add(self.k9box, 1, wx.ALL|wx.EXPAND, 2)
            loc9Sizer.Add(self.k9label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)

            btnSizer.Add(self.okButton, 0, wx.ALL, 2)
            #btnSizer.Add(self.cancelButton, 0, wx.ALL, 2)

            keyLSizer.Add(loc0Sizer, 1, wx.ALL|wx.EXPAND, 1)
            keyLSizer.Add(loc1Sizer, 1, wx.ALL|wx.EXPAND, 1)
            keyLSizer.Add(loc2Sizer, 1, wx.ALL|wx.EXPAND, 1)
            keyLSizer.Add(loc3Sizer, 1, wx.ALL|wx.EXPAND, 1)
            keyLSizer.Add(loc4Sizer, 1, wx.ALL|wx.EXPAND, 1)

            keyRSizer.Add(loc5Sizer, 1, wx.ALL|wx.EXPAND, 1)
            keyRSizer.Add(loc6Sizer, 1, wx.ALL|wx.EXPAND, 1)
            keyRSizer.Add(loc7Sizer, 1, wx.ALL|wx.EXPAND, 1)
            keyRSizer.Add(loc8Sizer, 1, wx.ALL|wx.EXPAND, 1)
            keyRSizer.Add(loc9Sizer, 1, wx.ALL|wx.EXPAND, 1)

            keySizer.Add(keyLSizer, 1, wx.ALL|wx.EXPAND, 1)
            keySizer.Add(keyRSizer, 1, wx.ALL|wx.EXPAND, 1)

            topSizer.Add(titleSizer, 0, wx.ALL|wx.EXPAND, 0)
            topSizer.Add(wx.StaticLine(panel, size=(520, 1)), 0, wx.ALL|wx.EXPAND, 0)
            topSizer.Add(keySizer, 1, wx.ALL|wx.EXPAND, 0)
            topSizer.Add(wx.StaticLine(panel, size=(520, 1)), 0, wx.ALL|wx.EXPAND, 0)
            topSizer.Add(btnSizer, 0, wx.ALL|wx.CENTER, 5)

            panel.SetSizer(topSizer)
            topSizer.Fit(self)


            self.CenterOnParent()
            self.GetParent().Enable(False)
            self.Show(True)
            self.onLoad(keydeck)

            if mKeys_s == "VALID":
                self.__eventLoop = wx.EventLoop()
                self.__eventLoop.Run()


        def onClose(self, event):
            self.GetParent().Enable(True)
            self.__eventLoop.Exit()
            self.Destroy()

        def onOK(self, event):
            self.GetParent().Enable(True)
            self.__eventLoop.Exit()
            self.Destroy()

        def onLoad(self, event):
            global mKeys_s
            global mKeys_n
            global mKeys_t
            global mKeys
            try:
                if mKeys_s == 'VALID':
                    self.titleBox.SetValue(mKeys_t)
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
                else:
                    dlg = wx.TextEntryDialog(None,"Enter Key-Deck's Passphrase")
                    ret = dlg.ShowModal()
                    if ret == wx.ID_OK:
                        cryptokey = dlg.GetValue()
                        open_keyfile = open(keydeck, "r")
                        cryptohash = hashlib.md5(cryptokey).hexdigest()

                        to_decrypt = open_keyfile.read()
                        decrypto = AES.new(cryptohash, AES.MODE_CBC, cryptohash[:16])
                        decrypted = decrypto.decrypt(str(to_decrypt))

                        mKeys = decrypted.replace(" ", "").replace("[", "").replace("]", "").replace("'", "").split(",")
                        open_keyfile.close()
                        if mKeys[0] == 'VALID':
                            print "Decrypted Successfully"
                            mKeys_s = mKeys[0]
                            del mKeys[0]
                            mKeys_t = mKeys[0]
                            self.titleBox.SetValue(mKeys_t)
                            del mKeys[0]
                            mKeys_n = len(mKeys)
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
                        else:
                            ips = wx.MessageDialog(self,
                            "Invalid Passphrase entered.",
                            "Decrypt Failed", wx.OK|wx.ICON_QUESTION)
                            result = ips.ShowModal()
                            ips.Destroy()
                            self.GetParent().Enable(True)
                            self.Destroy()
                    else:
                        dlg.Destroy()
                        self.GetParent().Enable(True)
                        self.Destroy()
                    dlg.Destroy()
            except:
                print "Error Occured"


    ################################################
    # Start of Main GUI Class code and subroutines #
    ################################################
    class buBBle_client(wx.Frame):
        def __init__(self, parent, title):
            wx.Frame.__init__(self, parent, title=title, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MINIMIZE_BOX ^ wx.MAXIMIZE_BOX) # Init the frame

            self.Bind(wx.EVT_CLOSE, self.OnClose)

            # Set App's Icon
            self.picon = wx.Icon(appicon, wx.BITMAP_TYPE_ICO)
            self.SetIcon(self.picon)

            menuBar = wx.MenuBar()

            # Define the File Menu.
            f_menu = wx.Menu()
            self.f_keys = f_menu.Append(wx.ID_SAVE, "&Key-Deck\tAlt-K", "Key-Deck Options")
            self.f_save = f_menu.Append(wx.ID_SAVE, "&Save\tAlt-S", "Save Chatlog.")
            self.f_exit = f_menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")

            self.Bind(wx.EVT_MENU, self.OnKeyOpts, self.f_keys)
            self.Bind(wx.EVT_MENU, self.OnClose, self.f_exit)
            menuBar.Append(f_menu, "&File")

            # Define the Help Menu
            h_menu = wx.Menu()
            self.e_about = h_menu.Append(wx.ID_ABOUT, "About", "About buBBle.")
            #self.Bind(wx.EVT_MENU, self.OnAbout, self.e_about)
            menuBar.Append(h_menu, "&Help")

            self.SetMenuBar(menuBar)

            panel = wx.Panel(self)

            emptyimg = wx.EmptyImage(32,32)
            srv_imgon = wx.Image(srvon, wx.BITMAP_TYPE_PNG)
            srv_imgoff = wx.Image(srvoff, wx.BITMAP_TYPE_PNG)
            usr_imgon = wx.Image(usron, wx.BITMAP_TYPE_PNG)
            usr_imgoff = wx.Image(usroff, wx.BITMAP_TYPE_PNG)


            # Define the Status Bar
            self.statusbar = self.CreateStatusBar()

            # Text boxes for Username and Password
            self.userLabel = wx.StaticText(panel, label="Username:", size=(65, -1), style=wx.ALIGN_RIGHT) # Username label
            self.userBox = wx.TextCtrl(panel, 5150, size=(265, -1), style=wx.TE_LEFT) # Username Textbox
            self.passLabel = wx.StaticText(panel, label="  Password:", size=(65, -1), style=wx.ALIGN_RIGHT) # Password Label
            self.passBox = wx.TextCtrl(panel, 5151, size=(265, -1), style=wx.TE_PASSWORD) # Password Textbox

            # Authenticate button and server status image
            self.connButton = wx.Button(panel, size=(100, -1), label="AUTH!")
            self.Bind(wx.EVT_BUTTON, self.OnAuth, self.connButton)

            self.usrstatBitmap = wx.StaticBitmap(panel, wx.ID_ANY, wx.BitmapFromImage(usr_imgoff))
            self.srvstatBitmap = wx.StaticBitmap(panel, wx.ID_ANY, wx.BitmapFromImage(emptyimg))

            # Chat box, Message box and Send Button
            self.chatBox = wx.TextCtrl(panel, 5250, size=(500, 300), style=wx.TE_LEFT|wx.TE_MULTILINE|wx.TE_READONLY) # Chat Textbox
            self.messageBox = wx.TextCtrl(panel, 5251, size=(-1, 50),style=wx.TE_LEFT|wx.TE_MULTILINE) # Message Textbox
            self.sendButton = wx.Button(panel, label="SEND!")

            # Binds!
            self.userBox.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseOver) #Hover On Refresh
            self.userBox.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave) #Hover Off Refresh
            self.passBox.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseOver) #Hover On Refresh
            self.passBox.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave) #Hover Off Refresh
            self.chatBox.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseOver) #Hover On Refresh
            self.chatBox.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave) #Hover Off Refresh
            self.messageBox.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseOver) #Hover On Refresh
            self.messageBox.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave) #Hover Off Refresh
            self.Bind(wx.EVT_BUTTON, self.OnSend, self.sendButton)

            self.messageBox.Enable(False)
            self.messageBox.Enable(False)
            self.sendButton.Enable(False)
            self.userBox.Enable(False)
            self.passBox.Enable(False)
            self.connButton.Enable(False)

            # Sizers!
            topSizer = wx.BoxSizer(wx.VERTICAL)
            upperSizer      = wx.BoxSizer(wx.HORIZONTAL)
            loginSizer      = wx.BoxSizer(wx.VERTICAL)
            statSizer       = wx.BoxSizer(wx.VERTICAL)
            userSizer       = wx.BoxSizer(wx.HORIZONTAL)
            passSizer       = wx.BoxSizer(wx.HORIZONTAL)
            midSizer        = wx.BoxSizer(wx.HORIZONTAL)
            lowerSizer      = wx.BoxSizer(wx.HORIZONTAL)

            # Add stuff to userSizer
            userSizer.Add(self.userLabel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 2)
            userSizer.Add(self.userBox, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 2)

            # Add stuff to passSizer
            passSizer.Add(self.passLabel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 2)
            passSizer.Add(self.passBox, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 2)

            # Add stuff to statSizer
            statSizer.Add(self.usrstatBitmap, 0, wx.ALL|wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL, 2)
            statSizer.Add(self.srvstatBitmap, 0, wx.ALL|wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL, 2)
            # Add stuff to upSizer
            loginSizer.Add(userSizer, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 2)
            loginSizer.Add(passSizer, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 2)

            upperSizer.Add(loginSizer, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 2)
            upperSizer.Add(self.connButton,  0, wx.ALL|wx.ALIGN_CENTER|wx.EXPAND, 5)
            upperSizer.Add(statSizer, 0, wx.ALL|wx.EXPAND, 2)

            # Add stuff to the midSizer
            midSizer.Add(self.chatBox, 1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 2)

            # Add stuff to lower Sizer
            lowerSizer.Add(self.messageBox, 1, wx.ALL|wx.EXPAND, 0)
            lowerSizer.Add(self.sendButton, 0, wx.RIGHT|wx.EXPAND, 0)

            # Add stuff to topSizer
            topSizer.Add(upperSizer, 0, wx.ALL|wx.EXPAND, 2)
            topSizer.Add(midSizer, 0, wx.ALL|wx.EXPAND, 2)
            topSizer.Add(lowerSizer, 0, wx.ALL|wx.EXPAND, 2)

            panel.SetSizer(topSizer)
            topSizer.Fit(self)

            panel.Layout()
            self.Show(True) # show shit!

            def daemon_srvstat():
                global pullT_status
                global srv_stat

                #try:
                while pullT_status == 0:
                    #print "Daemon: " + str(pullT_status)
                    srvping = os.system("ping -W 1 -qc 1 " + server + "> /dev/null 2>&1")
                    #print "Ping: " + str(srvping)
                    if srvping == 0:
                        self.srvstatBitmap.SetBitmap(wx.BitmapFromImage(srv_imgon))
                        srv_stat = 1
                        if usr_auth == '0':
                            self.messageBox.Enable(False)
                            self.sendButton.Enable(False)
                            self.userBox.Enable(True)
                            self.passBox.Enable(True)
                            self.connButton.Enable(True)
                        elif usr_auth == '1':
                            self.messageBox.Enable(True)
                            self.sendButton.Enable(True)
                            self.userBox.Enable(False)
                            self.passBox.Enable(False)
                            self.connButton.Enable(False)
                    else:
                        self.srvstatBitmap.SetBitmap(wx.BitmapFromImage(srv_imgoff))
                        srv_stat = 0
                        self.messageBox.Enable(False)
                        self.sendButton.Enable(False)
                        self.userBox.Enable(False)
                        self.passBox.Enable(False)
                        self.connButton.Enable(False)
                    time.sleep(1)
                #except:
                #    print "Error in Daemon."
                self.Destroy() # GUI dedded :(
                sys.exit() # App dedded :(

            srv_d = threading.Thread(name='recv daemon', target=daemon_srvstat)
            #srv_d.setDaemon(True)
            srv_d.start()

        # File>Key-Deck Options
        def OnKeyOpts(self,event):
            dialog = keydeckFrame(self, -1)

        # OnPull function to get posts from server
        def OnPull(self):
            pass

        # OnAuth function used to send a message to the server
        def OnAuth(self, event):
            global mKeys_s
            global keydeck
            global usr_auth
            global usr_cred
            global auth_out

            auth_sel = ['','']

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
                    print "WOOP! NOT EMPTY FIELDS"
                    usr_cred[2] = usr_cred[0] + "/" + hashlib.md5(usr_cred[1]).hexdigest()
                    print usr_cred[2]
                    authlen = len(usr_cred[2])
                    auth2fill = 16 - (authlen % 16)
                    authstr = (usr_cred[2] + " " * auth2fill)

                    auth_sel[0] = randint(0,aKeys_n)
                    auth_sel[1] = randint(0,aKeys_n)

                    acrypt = AES.new(aKeys[auth_sel[0]], AES.MODE_CBC, aKeys[auth_sel[1]][:16])
                    auth_out = str(auth_sel[0]) + acrypt.encrypt(authstr) + str(auth_sel[1])
                    print auth_out
                    print str(auth_sel[0]) + ' : ' + aKeys[auth_sel[0]]
                    print str(auth_sel[1]) + ' : ' + aKeys[auth_sel[1]][:16]
                    # Yep, actual server auth request is handled via a separate function!
                    # That way it can also be used when sending a message and requesting the message list.
                    usr_auth = self.AuthPush(auth_out)
                    if usr_auth == '1': # Check to see if server authenticated
                        # If we end up here we were successful.
                        aac = wx.MessageDialog(self,
                        "Authentication Successful, You may now send and recieve bulletins from the server",
                        "Authentication Successful.", wx.OK|wx.ICON_QUESTION)
                        result = aac.ShowModal() # Display Dialog informing empty fields.
                        aac.Destroy() # Kill Dialog.
                        pass
                    else:
                        adc = wx.MessageDialog(self,
                        "Authentication Failed, Please Try Again",
                        "Authentication Failed.", wx.OK|wx.ICON_QUESTION)
                        result = adc.ShowModal() # Display Dialog informing empty fields.
                        adc.Destroy()
                        pass
            else: # If no Key-Deck is loaded inform the user and push them to the Key-Deck Options.
                mcd = wx.MessageDialog(self,
                "No Key-Deck has been Loaded, please enter your Keydeck passphrase to continue.",
                "No Key-Deck Loaded", wx.OK|wx.ICON_QUESTION)
                result = mcd.ShowModal() # Display Dialog informing empty fields.
                mcd.Destroy() # Kill Dialog.
                self.OnKeyOpts(keydeck)
            pass

        # AuthPush function used to send a message to the server
        def AuthPush(self, auth_string):
            try:
                self.auth_conn = socket.socket()
                self.auth_conn.connect((server, int(auth_port)))
                self.auth_conn.send(auth_string)
                srv_resp = self.auth_conn.recv(1024)
                self.auth_conn.shutdown(socket.SHUT_RDWR)
                self.auth_conn.close()
                return srv_resp
                pass
            except:
                return '0'
                pass

        # OnSend function used to send a message to the server
        def OnSend(self, event):
            x = 5
            a = randint(0,x)
            b = randint(0,x)
            c = randint(0,x)
            print "\033[91mX: \033[97m" + str(x) + "\033[91m A: \033[97m" + str(a) + "\033[91m B: \033[97m" + str(b) + "\033[91m C: \033[97m" + str(c)
            pass

        # OnMouseOver functions for widgets
        def OnMouseOver(self,event):
            widget_id = event.GetId()
            if widget_id == 5150:
                self.statusbar.SetStatusText('Username')
            elif widget_id == 5151:
                self.statusbar.SetStatusText('Password')
            elif widget_id == 5250:
                self.statusbar.SetStatusText('Chat Box')
            elif widget_id == 5251:
                self.statusbar.SetStatusText('MessageBox')

        #OnMouseLeave function for widgets
        def OnMouseLeave(self,event):
            self.statusbar.SetStatusText('')

        # OnClose Function called when a user closes the encoder.
        def OnClose(self,event):
            global pullT_status
            dlg = wx.MessageDialog(self,
                "Do you really want to close this application?",
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

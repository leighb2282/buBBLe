#!/usr/bin/env python
# buBBle_client.py
# Client for buBBle BBS
# Version v00.00.01
# Sat 26 Dec 2015 18:39:07
# Leigh Burton, lburton@metacache.net

# Import modules

import wx
import sys
import socket
import threading

from Crypto.Cipher import AES
from random import randint

# Set initial variables
server = "192.168.0.100"
port = "8080"
appicon = "res/bbicon.ico"

keys = ["70002a3a92fb7a081fd277e9a80c227e",
    "a5494db10f395190b8f90249366f095d",
    "86f4b69a25537d96ecda6c6686057c53",
    "c06cfd9462fd84a2183be13b3931b39e",
    "b8d9b19e70295ec7c2fc50fbee2fc780",
    "c64ef4ffca2551988e79f2005a8fb8a7"]

def main():
    """ Main entry point for the script."""


    # Start of GUI happiness
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
            self.m_save = f_menu.Append(wx.ID_SAVE, "&Save\tAlt-S", "Save Chatlog.")
            self.m_exit = f_menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
            self.Bind(wx.EVT_MENU, self.OnClose, self.m_exit)
            menuBar.Append(f_menu, "&File")

            # Define the Help Menu
            h_menu = wx.Menu()
            self.e_about = h_menu.Append(wx.ID_ABOUT, "About", "About Puddle.")
            #self.Bind(wx.EVT_MENU, self.OnAbout, self.e_about)
            menuBar.Append(h_menu, "&Help")

            self.SetMenuBar(menuBar)

            panel = wx.Panel(self)

            # Define the Status Bar
            self.statusbar = self.CreateStatusBar()

            self.userlabel = wx.StaticText(panel, label="Username:", size=(65, -1), style=wx.ALIGN_RIGHT) # Username label
            self.userbox = wx.TextCtrl(panel, 5150, size=(265, -1), style=wx.TE_LEFT) # Username Textbox
            self.passlabel = wx.StaticText(panel, label="  Password:", size=(65, -1), style=wx.ALIGN_RIGHT) # Password Label
            self.passbox = wx.TextCtrl(panel, 5151, size=(265, -1), style=wx.TE_PASSWORD) # Password Textbox

            self.chatBox = wx.TextCtrl(panel, 5155, size=(500, 300), style=wx.TE_LEFT|wx.TE_MULTILINE) # Chat Textbox
            self.messageBox = wx.TextCtrl(panel, 5155, size=(-1, 50),style=wx.TE_LEFT|wx.TE_MULTILINE) # Message Textbox
            self.sendButton = wx.Button(panel, label="SEND!")


            # Binds!
            self.userbox.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseOver) #Hover On Refresh
            self.userbox.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave) #Hover Off Refresh
            self.passbox.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseOver) #Hover On Refresh
            self.passbox.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave) #Hover Off Refresh
            #self.Bind(wx.EVT_BUTTON, self.OnSend, self.sendButton)

            # Sizers!
            topSizer        = wx.BoxSizer(wx.VERTICAL)
            #upperSizer      = wx.BoxSizer(wx.HORIZONTAL)
            userSizer       = wx.BoxSizer(wx.HORIZONTAL)
            passSizer       = wx.BoxSizer(wx.HORIZONTAL)
            midSizer       = wx.BoxSizer(wx.HORIZONTAL)
            lowerSizer   = wx.BoxSizer(wx.HORIZONTAL)

            # Add stuff to userSizer
            userSizer.Add(self.userlabel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 2)
            userSizer.Add(self.userbox, 0, wx.ALL|wx.EXPAND, 2)

            # Add stuff to passSizer
            passSizer.Add(self.passlabel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 2)
            passSizer.Add(self.passbox, 0, wx.ALL|wx.EXPAND, 2)

            # Add stuff to the midSizer
            midSizer.Add(self.chatBox, 1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 2)

            # Add stuff to lower Sizer
            lowerSizer.Add(self.messageBox, 1, wx.ALL|wx.EXPAND, 0)
            lowerSizer.Add(self.sendButton, 0, wx.RIGHT|wx.EXPAND, 0)

            # Add stuff to topSizer
            topSizer.Add(userSizer, 0, wx.ALL|wx.EXPAND, 2)
            topSizer.Add(passSizer, 0, wx.ALL|wx.EXPAND, 2)
            topSizer.Add(midSizer, 0, wx.ALL|wx.EXPAND, 2)
            topSizer.Add(lowerSizer, 0, wx.ALL|wx.EXPAND, 2)

            panel.SetSizer(topSizer)
            topSizer.Fit(self)

            panel.Layout()
            self.Show(True) # show shit!

        # On-Hover functions for the refresh and settings buttons
        def OnMouseOver(self,event):
            widget_id = event.GetId()
            if widget_id == 5150:
                self.statusbar.SetStatusText('5150')
            elif widget_id == 5250:
                self.statusbar.SetStatusText('5250')
        def OnMouseLeave(self,event):
            self.statusbar.SetStatusText('')

        # Function called when a user closes the encoder.
        def OnClose(self,event):
            dlg = wx.MessageDialog(self,
                "Do you really want to close this application?",
                "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_OK:
                self.Destroy() # GUI dedded :(
                print "\033[91mApp killed by File|Exit or App's 'x' button"
                sys.exit() # App dedded :(
            else:
                print "\033[93mUser chose not to close the App."

    app = wx.App(False)
    frame = buBBle_client(None, 'buBBle BBS Client')
    app.MainLoop()
    pass


if __name__ == '__main__':
    sys.exit(main())

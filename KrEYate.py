#!/usr/bin/env python
# KrEYate.py
# quick Key-Deck creation tool
# Version v2.0.0
# 2/16/2016, 7:11:27 PM
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

outfile = "bubble_keys.crypt"
keysetup = []
tctstat = 0

def main():
    """ Main entry point for buBBle."""
    class KrEYate(wx.Frame):
        def __init__(self, parent, title):
            wx.Frame.__init__(self, parent, title=title, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MINIMIZE_BOX ^ wx.MAXIMIZE_BOX) # Init the frame
            self.Bind(wx.EVT_CLOSE, self.OnClose)

            panel = wx.Panel(self,wx.ID_ANY)

            self.titleBox = wx.TextCtrl(panel, style=wx.TE_LEFT) # Key-Deck name
            self.passBox = wx.TextCtrl(panel, style=wx.TE_LEFT) # Key-Deck name
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

            self.okButton = wx.Button(panel, label="SAVE")

            self.Bind(wx.EVT_BUTTON, self.onOK, self.okButton)
            self.Bind(wx.EVT_CLOSE, self.OnClose)

            #Sizers!
            topSizer        = wx.BoxSizer(wx.VERTICAL)
            keySizer      = wx.BoxSizer(wx.HORIZONTAL)
            titleSizer      = wx.BoxSizer(wx.HORIZONTAL)
            passSizer      = wx.BoxSizer(wx.HORIZONTAL)
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
            passSizer.Add(self.passBox, 1, wx.ALL|wx.EXPAND, 2)

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
            topSizer.Add(passSizer, 0, wx.ALL|wx.EXPAND, 0)
            topSizer.Add(wx.StaticLine(panel, size=(520, 1)), 0, wx.ALL|wx.EXPAND, 0)
            topSizer.Add(keySizer, 1, wx.ALL|wx.EXPAND, 0)
            topSizer.Add(wx.StaticLine(panel, size=(520, 1)), 0, wx.ALL|wx.EXPAND, 0)
            topSizer.Add(btnSizer, 0, wx.ALL|wx.CENTER, 5)

            panel.SetSizer(topSizer)
            topSizer.Fit(self)
            self.okButton.Enable(False)
            panel.Layout()
            self.Show(True) # show shit!
            def thread_tct():
                global tctstat
                while tctstat == 0:
                    if self.titleBox.GetValue() == "" or self.passBox.GetValue() == "" or self.k0box.GetValue() == "" or self.k1box.GetValue() == "" or self.k2box.GetValue() == "" or self.k3box.GetValue() == "" or self.k4box.GetValue() == "" or self.k5box.GetValue() == "" or self.k6box.GetValue() == "" or self.k7box.GetValue() == "" or self.k8box.GetValue() == "" or self.k9box.GetValue() == "":
                        self.okButton.Enable(False)
                    else:
                        self.okButton.Enable(True)
                pass

            tct_d = threading.Thread(name='TextCTRL Check', target=thread_tct)
            tct_d.start()

        def OnClose(self,event):
            global tctstat
            dlg = wx.MessageDialog(self,
                "Do you really want to close this application?",
                "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_OK:
                tctstat = 1
                self.Destroy() # GUI dedded :(
                sys.exit() # App dedded :(
            else:
                pass # Just do nothing, User chose not to exit.

        def onOK(self, event):
            global keysetup
            global tctstat
            rawstore = ['','','','','','','','','','']
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
                keysetup.append('VALID')
                keysetup.append(self.titleBox.GetValue())
                for i in rawstore:
                    print i
                    keysetup.append(hashlib.md5(i).hexdigest())
                uncrypt = str(keysetup)
                messlen = len(uncrypt)
                num2fill = 16 - (messlen % 16)
                tocrypt = (uncrypt + " " * num2fill)

                cryptokey = self.passBox.GetValue()
                cryptohash = hashlib.md5(cryptokey).hexdigest()
                crypto = AES.new(cryptohash, AES.MODE_CBC, cryptohash[:16])
                encrypted = crypto.encrypt(tocrypt)

                f = open(outfile, "w")
                f.write(str(encrypted))
                f.close()
                mcr = wx.MessageDialog(self,
                "KeyDeck Created Successfully, Closing App",
                "Keydeck Complete.", wx.OK|wx.ICON_QUESTION)
                result = mcr.ShowModal()
                mcr.Destroy()
            except:
                print "Error Occured"


    app = wx.App(False)
    frame = KrEYate(None, 'KrEYate - Keydeck Creator')
    app.MainLoop()
    pass


if __name__ == '__main__':
  sys.exit(main())

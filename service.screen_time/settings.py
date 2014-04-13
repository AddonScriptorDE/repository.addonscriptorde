#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import hashlib
import xbmc
import urllib


def setTime():
    kb = xbmc.Keyboard(time, "Set the daily screen time (in minutes)")
    kb.doModal()
    if kb.isConfirmed():
        minutesPerDay = int(kb.getText())
        fh = open(timeFile, 'w')
        fh.write(str(minutesPerDay))
        fh.close()


def setMessage():
    kb = xbmc.Keyboard(message, "Enter a custom message")
    kb.doModal()
    if kb.isConfirmed():
        fh = open(messageFile, 'w')
        fh.write(kb.getText())
        fh.close()


def setPin():
    kb = xbmc.Keyboard("", "Enter a new 4-digit PIN")
    kb.doModal()
    if kb.isConfirmed():
        fh = open(pinFile, 'w')
        fh.write(hashlib.sha1(kb.getText()).hexdigest())
        fh.close()


addonID = 'service.screen_time'
userDataDir = xbmc.translatePath("special://profile/addon_data/"+addonID)
workingDir = os.path.join(userDataDir, 'times')
timeFile = os.path.join(userDataDir, 'time')
messageFile = os.path.join(userDataDir, 'message')
pinFile = os.path.join(userDataDir, 'pin')
pinHash = ""
if os.path.exists(pinFile):
    fh = open(pinFile, 'r')
    pinHash = fh.read()
    fh.close()
time = ""
if os.path.exists(timeFile):
    fh = open(timeFile, 'r')
    time = fh.read()
    fh.close()
message = ""
if os.path.exists(messageFile):
    fh = open(messageFile, 'r')
    message = fh.read()
    fh.close()
enteredPin = ""
if pinHash:
    kb = xbmc.Keyboard("", "Enter your PIN")
    kb.doModal()
    if kb.isConfirmed():
        enteredPin = kb.getText()
        while enteredPin and pinHash!=hashlib.sha1(enteredPin).hexdigest():
            kb = xbmc.Keyboard("", "Wrong PIN! Try again...")
            kb.doModal()
            if kb.isConfirmed():
                enteredPin = kb.getText()


mode = urllib.unquote_plus(sys.argv[1])

if mode=="setTime" and pinHash and pinHash==hashlib.sha1(enteredPin).hexdigest():
    setTime()
elif mode=="setMessage" and pinHash and pinHash==hashlib.sha1(enteredPin).hexdigest():
    setMessage()
elif mode=="setPin" and pinHash and pinHash==hashlib.sha1(enteredPin).hexdigest():
    setPin()

import os, xbmc, xbmcaddon, datetime, hashlib

#addon = xbmcaddon.Addon()
#addonID = addon.getAddonInfo('id')
addonID = 'service.screen_time'
addon = xbmcaddon.Addon(id=addonID)
userDataDir = xbmc.translatePath("special://profile/addon_data/"+addonID)
workingDir = os.path.join(userDataDir, 'times')
timeFile = os.path.join(userDataDir, 'time')
messageFile = os.path.join(userDataDir, 'message')
pinFile = os.path.join(userDataDir, 'pin')
minutesPerDay = 0
customMessage = ""

if not os.path.isdir(userDataDir):
    os.mkdir(userDataDir)
if not os.path.isdir(workingDir):
    os.mkdir(workingDir)

class PlayerEvents(xbmc.Player):
    def onPlayBackStarted(self):
        if self.isPlayingVideo():
            fileToday = os.path.join(workingDir, datetime.date.today().strftime("%Y-%m-%d"))
            minutes=0
            if os.path.exists(fileToday):
                fh = open(fileToday, 'r')
                minutes = int(fh.read())
                fh.close()
                if minutes>=minutesPerDay:
                    xbmc.executebuiltin('XBMC.PlayerControl(stop)')
                    if customMessage:
                        xbmc.executebuiltin('XBMC.Notification(Info:,'+customMessage+',5000)')
                    else:
                        xbmc.executebuiltin('XBMC.Notification(Info:,'+translation(30002)+',5000)')
            xbmc.sleep(1000)
            while self.isPlayingVideo():
                xbmc.sleep(60000)
                minutes+=1
                fh = open(fileToday, 'w')
                fh.write(str(minutes))
                fh.close()
                if minutes>=minutesPerDay:
                    xbmc.executebuiltin('XBMC.PlayerControl(stop)')
                    if customMessage:
                        xbmc.executebuiltin('XBMC.Notification(Info:,'+customMessage+',5000)')
                    else:
                        xbmc.executebuiltin('XBMC.Notification(Info:,'+translation(30002)+',5000)')
        

def translation(id):
    return addon.getLocalizedString(id).encode('utf-8')

if not os.path.exists(pinFile):
    kb = xbmc.Keyboard("0000", "Screen Time: Choose your 4-digit PIN")
    kb.doModal()
    if kb.isConfirmed():
        fh = open(pinFile, 'w')
        fh.write(hashlib.sha1(kb.getText()).hexdigest())
        fh.close()

if not os.path.exists(timeFile) and os.path.exists(pinFile):
    kb = xbmc.Keyboard("60", "Set the daily screen time (in minutes)")
    kb.doModal()
    if kb.isConfirmed():
        minutesPerDay = int(kb.getText())
        fh = open(timeFile, 'w')
        fh.write(str(minutesPerDay))
        fh.close()
elif os.path.exists(timeFile):
    fh = open(timeFile, 'r')
    minutesPerDay = int(fh.read())
    fh.close()

if os.path.exists(messageFile):
    fh = open(messageFile, 'r')
    customMessage = fh.read()
    fh.close()

if os.path.exists(timeFile):
    player=PlayerEvents()
    while (not xbmc.abortRequested):
        xbmc.sleep(100)

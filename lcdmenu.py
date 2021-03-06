#!/usr/local/bin/python3.5
#
# Created by Alan Aufderheide, February 2013
#
# This provides a menu driven application using the LCD Plates
# from Adafruit Electronics.

# import commands
import subprocess
import os
# from string import split
from time import sleep, strftime, localtime, gmtime
from datetime import datetime, timedelta
from xml.dom.minidom import *
# from Adafruit_I2C import Adafruit_I2C
# from Adafruit_MCP230xx import Adafruit_MCP230XX
# from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate
from Adafruit_CharLCD import Adafruit_CharLCDPlate
from ListSelector import ListSelector
import xml.etree.ElementTree as etree
from omxplayer.player import OMXPlayer, OMXPlayerDeadError
from dbus import DBusException
from math import floor

import smbus2 as smbus

keyboard_import = True
try:
    import keyboard
except ImportError:
    keyboard_import = False



configfile = '/home/pi//RaspberryPiLcdMenu/lcdmenu.xml'
# set DEBUG=1 for print debug statements
DEBUG = 1
DISPLAY_ROWS = 2
DISPLAY_COLS = 16

# Char LCD plate button names.
SELECT = 0
RIGHT = 1
DOWN = 2
UP = 3
LEFT = 4


# set to 0 if you want the LCD to stay on, 1 to turn off and on auto
AUTO_OFF_LCD = 0

# set busnum param to the correct value for your pi
lcd = Adafruit_CharLCDPlate(busnum=1)


# in case you add custom logic to lcd to check if it is connected (useful)
# if lcd.connected == 0:
#    quit()

# lcd.begin(DISPLAY_COLS, DISPLAY_ROWS)
# #lcd.backlight(lcd.OFF)

class Music_player():

    def __init__(self):
        self.playing = False
        self.song = ''
        self.song_str = ''

    def play(self, x):
        self.song_str = x
        self.song = OMXPlayer(x)
        self.song.set_volume(-1000)
        self.playing = True
        


# commands
def UpdateSongs():
    tree = etree.parse(configfile)
    root = tree.getroot()
    # This breaks if i move the sogs folder in XML doc
    songs = root[2][0]
    cur_songs = []
    for current in songs:
        cur_songs.append(current.attrib['text'])
    
    ls = os.listdir('Music/')
    for song in ls:
        if song[:16] not in cur_songs:
            if DEBUG:
                print(song)
            el = xml.etree.ElementTree.Element('widget')
            el.attrib['text'] = song[:16]
            el.attrib['function'] = 'PlaySong("' + os.getcwd() +'/Music/' + song + '")'
            # l = len('PlaySong("')
            # el.text = el.text[:l] + os.getcwd()+'/' + el.text[l:]
            songs.append(el)

    tree.write('lcdmenu.xml',)
    init_menu()

def PlaySong(x):
    player.play(x)
    

def DoQuit():
    lcd.clear()
    lcd.message('Are you sure?\nPress Sel for Y')
    while 1:
        if lcd.is_pressed(LEFT):
            break
        if lcd.is_pressed(SELECT):
            lcd.clear()
            # #lcd.backlight(lcd.OFF)
            quit()
        sleep(0.25)


def DoShutdown():
    lcd.clear()
    lcd.message('Are you sure?\nPress Sel for Y')
    while 1:
        if lcd.is_pressed(LEFT):
            break
        if lcd.is_pressed(SELECT):
            lcd.clear()
            # lcd.backlight(lcd.OFF)
            subprocess.getoutput("sudo shutdown -h now")
            quit()
        sleep(0.25)



def DoReboot():
    lcd.clear()
    lcd.message('Are you sure?\nPress Sel for Y')
    while 1:
        if lcd.is_pressed(LEFT):
            break
        if lcd.is_pressed(SELECT):
            lcd.clear()
            # lcd.backlight(lcd.OFF)
            subprocess.getoutput("sudo reboot")
            quit()
        sleep(0.25)


def LcdOff():
    global currentLcd
    currentLcd = lcd.OFF
    lcd.set_backlight(0.0)


def LcdOn():
    global currentLcd
    currentLcd = lcd.ON
    lcd.set_backlight(1.0)


def LcdRed():
    global currentLcd
    currentLcd = lcd.set_color(1.0, 0.0, 0.0)
    # lcd.backlight(currentLcd)


def LcdGreen():
    global currentLcd
    currentLcd = lcd.set_color(0.0, 1.0, 0.0)
    # lcd.backlight(currentLcd)


def LcdBlue():
    global currentLcd
    currentLcd = lcd.set_color(0.0, 0.0, 1.0)
    # lcd.backlight(currentLcd)


def LcdYellow():
    global currentLcd
    currentLcd = lcd.set_color(1.0, 1.0, 0.0)
    # lcd.backlight(currentLcd)


def LcdTeal():
    global currentLcd
    currentLcd = lcd.set_color(0.0, 0.8, 0.8)
    # lcd.backlight(currentLcd)


def LcdViolet():
    global currentLcd
    currentLcd = lcd.set_color(0.8, 0.0, 0.8)
    # lcd.backlight(currentLcd)


def ShowDateTime():
    if DEBUG:
        print('in ShowDateTime')
    lcd.clear()
    while not (lcd.is_pressed(LEFT)):
        sleep(0.25)
        lcd.home()
        lcd.message(strftime('%a %b %d %Y\n%I:%M:%S %p', localtime()))


def ValidateDateDigit(current, curval):
    # do validation/wrapping
    if current == 0:  # Mm
        if curval < 1:
            curval = 12
        elif curval > 12:
            curval = 1
    elif current == 1:  # Dd
        if curval < 1:
            curval = 31
        elif curval > 31:
            curval = 1
    elif current == 2:  # Yy
        if curval < 1950:
            curval = 2050
        elif curval > 2050:
            curval = 1950
    elif current == 3:  # Hh
        if curval < 0:
            curval = 23
        elif curval > 23:
            curval = 0
    elif current == 4:  # Mm
        if curval < 0:
            curval = 59
        elif curval > 59:
            curval = 0
    elif current == 5:  # Ss
        if curval < 0:
            curval = 59
        elif curval > 59:
            curval = 0
    return curval


def SetDateTime():
    if DEBUG:
        print('in SetDateTime')
    # M D Y H:M:S AM/PM
    curtime = localtime()
    month = curtime.tm_mon
    day = curtime.tm_mday
    year = curtime.tm_year
    hour = curtime.tm_hour
    minute = curtime.tm_min
    second = curtime.tm_sec
    ampm = 0
    if hour > 11:
        hour -= 12
        ampm = 1
    curr = [0, 0, 0, 1, 1, 1]
    curc = [2, 5, 11, 1, 4, 7]
    curvalues = [month, day, year, hour, minute, second]
    current = 0  # start with month, 0..14

    lcd.clear()
    lcd.message(strftime("%b %d, %Y  \n%I:%M:%S %p  ", curtime))
    lcd.blink()
    lcd.setCursor(curc[current], curr[current])
    sleep(0.5)
    while 1:
        curval = curvalues[current]
        if lcd.is_pressed(UP):
            curval += 1
            curvalues[current] = ValidateDateDigit(current, curval)
            curtime = (curvalues[2], curvalues[0], curvalues[1], curvalues[3], curvalues[4], curvalues[5], 0, 0, 0)
            lcd.home()
            lcd.message(strftime("%b %d, %Y  \n%I:%M:%S %p  ", curtime))
            lcd.setCursor(curc[current], curr[current])
        if lcd.is_pressed(DOWN):
            curval -= 1
            curvalues[current] = ValidateDateDigit(current, curval)
            curtime = (curvalues[2], curvalues[0], curvalues[1], curvalues[3], curvalues[4], curvalues[5], 0, 0, 0)
            lcd.home()
            lcd.message(strftime("%b %d, %Y  \n%I:%M:%S %p  ", curtime))
            lcd.setCursor(curc[current], curr[current])
        if lcd.is_pressed(RIGHT):
            current += 1
            if current > 5:
                current = 5
            lcd.setCursor(curc[current], curr[current])
        if lcd.is_pressed(LEFT):
            current -= 1
            if current < 0:
                lcd.noBlink()
                return
            lcd.setCursor(curc[current], curr[current])
        if lcd.is_pressed(SELECT):
            # set the date time in the system
            lcd.noBlink()
            os.system(strftime('sudo date --set="%d %b %Y %H:%M:%S"', curtime))
            break
        sleep(0.25)

    lcd.noBlink()


def ShowIPAddress():
    if DEBUG:
        print('in ShowIPAddress')
    lcd.clear()
    lcd.message(subprocess.getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:])
    while 1:
        if lcd.is_pressed(LEFT):
            break
        sleep(0.25)





class CommandToRun:
    def __init__(self, myName, theCommand):
        self.text = '*'+myName

        self.commandToRun = theCommand#[:l] + os.getcwd()+'/' + theCommand[l:]

        if DEBUG:
            print(self.commandToRun)

    def Run(self):
        try:
            # self.clist = subprocess.getoutput(self.commandToRun)
            # print(self.clist)
            # self.clist = self.clist.split('\n')
            # # self.clist = split(subprocess.Popen(self.commandToRun, stdout=subprocess.PIPE), '\n')
            # if len(self.clist) > 0:
            #     lcd.clear()
            #     lcd.message(self.clist[0])
            #     for i in range(1, len(self.clist)):
            #         while 1:
            #             if lcd.is_pressed(DOWN):
            #                 break
            #             sleep(0.25)
            #         lcd.clear()
            #         lcd.message(self.clist[i - 1] + '\n' + self.clist[i])
            #         sleep(0.5)
            # while 1:
            #     if lcd.is_pressed(LEFT):
            #         break

            subprocess.Popen(self.commandToRun.split())
        except Exception as e:
            print(e.args)
            print(self.commandToRun)


class Widget:
    def __init__(self, myName, myFunction):
        self.text = '>' + myName
        self.function = myFunction


class Folder:
    def __init__(self, myName, myParent):
        self.text = '#' + myName
        self.items = []
        self.parent = myParent


def HandleSettings(node):
    global lcd
    if node.getAttribute('lcdColor').lower() == 'red':
        LcdRed()
    elif node.getAttribute('lcdColor').lower() == 'green':
        LcdGreen()
    elif node.getAttribute('lcdColor').lower() == 'blue':
        LcdBlue()
    elif node.getAttribute('lcdColor').lower() == 'yellow':
        LcdYellow()
    elif node.getAttribute('lcdColor').lower() == 'teal':
        LcdTeal()
    elif node.getAttribute('lcdColor').lower() == 'violet':
        LcdViolet()
    elif node.getAttribute('lcdColor').lower() == 'white':
        LcdOn()
    if node.getAttribute('lcdBacklight').lower() == 'on':
        LcdOn()
    elif node.getAttribute('lcdBacklight').lower() == 'off':
        LcdOff()


def ProcessNode(currentNode, currentItem):
    children = currentNode.childNodes

    for child in children:
        if isinstance(child, xml.dom.minidom.Element):
            if child.tagName == 'settings':
                HandleSettings(child)
            elif child.tagName == 'folder':
                thisFolder = Folder(child.getAttribute('text'), currentItem)
                currentItem.items.append(thisFolder)
                ProcessNode(child, thisFolder)
            elif child.tagName == 'widget':
                thisWidget = Widget(child.getAttribute('text'), child.getAttribute('function'))
                currentItem.items.append(thisWidget)
            elif child.tagName == 'run':
                thisCommand = CommandToRun(child.getAttribute('text'), child.firstChild.data)
                currentItem.items.append(thisCommand)


class Display:
    def __init__(self, folder):
        self.curFolder = folder
        self.curTopItem = 0
        self.curSelectedItem = 0

    def display(self):
        if self.curTopItem > len(self.curFolder.items) - DISPLAY_ROWS:
            self.curTopItem = len(self.curFolder.items) - DISPLAY_ROWS
        if self.curTopItem < 0:
            self.curTopItem = 0
        if DEBUG:
            print('------------------')
        message_str = ''
        for row in range(self.curTopItem, self.curTopItem + DISPLAY_ROWS):
            if row > self.curTopItem:
                message_str += '\n'
            if row < len(self.curFolder.items):
                if row == self.curSelectedItem:
                    cmd = '-' + self.curFolder.items[row].text
                    if len(cmd) < 16:
                        for row in range(len(cmd), 16):
                            cmd += ' '
                    if DEBUG:
                        print('|' + cmd + '|')
                    message_str += cmd
                else:
                    cmd = ' ' + self.curFolder.items[row].text
                    if len(cmd) < 16:
                        for row in range(len(cmd), 16):
                            cmd += ' '
                    if DEBUG:
                        print('|' + cmd + '|')
                    message_str += cmd
        if DEBUG:
            print('------------------')
        lcd.home()
        lcd.message(message_str)

    def update(self, command):
        global currentLcd
        global lcdstart
        # lcd.backlight(currentLcd)
        lcdstart = datetime.now()
        if DEBUG:
            print('do', command)
        if command == 'u':
            self.up()
        elif command == 'd':
            self.down()
        elif command == 'r':
            lcd.clear()
            self.right()
        elif command == 'l':
            self.left()
        elif command == 's':
            self.select()

    def up(self):
        if self.curSelectedItem == 0:
            return
        elif self.curSelectedItem > self.curTopItem:
            self.curSelectedItem -= 1
        else:
            self.curTopItem -= 1
            self.curSelectedItem -= 1

    def down(self):
        if self.curSelectedItem + 1 == len(self.curFolder.items):
            return
        elif self.curSelectedItem < self.curTopItem + DISPLAY_ROWS - 1:
            self.curSelectedItem += 1
        else:
            self.curTopItem += 1
            self.curSelectedItem += 1

    def left(self):
        if isinstance(self.curFolder.parent, Folder):
            # find the current in the parent
            itemno = 0
            index = 0
            for item in self.curFolder.parent.items:
                if self.curFolder == item:
                    if DEBUG:
                        print('foundit')
                    index = itemno
                else:
                    itemno += 1
            if index < len(self.curFolder.parent.items):
                self.curFolder = self.curFolder.parent
                self.curTopItem = index
                self.curSelectedItem = index
            else:
                self.curFolder = self.curFolder.parent
                self.curTopItem = 0
                self.curSelectedItem = 0

    def right(self):
        if isinstance(self.curFolder.items[self.curSelectedItem], Folder):
            self.curFolder = self.curFolder.items[self.curSelectedItem]
            self.curTopItem = 0
            self.curSelectedItem = 0
        elif isinstance(self.curFolder.items[self.curSelectedItem], Widget):
            if DEBUG:
                print('eval', self.curFolder.items[self.curSelectedItem].function)
            # eval(self.curFolder.items[self.curSelectedItem].function + '()')
            eval(self.curFolder.items[self.curSelectedItem].function)
        elif isinstance(self.curFolder.items[self.curSelectedItem], CommandToRun):
            self.curFolder.items[self.curSelectedItem].Run()

    def select(self):
        if DEBUG:
            print('check widget')
        if isinstance(self.curFolder.items[self.curSelectedItem], Widget):
            if DEBUG:
                print('eval', self.curFolder.items[self.curSelectedItem].function)
            # eval(self.curFolder.items[self.curSelectedItem].function + '()')
            eval(self.curFolder.items[self.curSelectedItem].function)




def init_menu():
    # now start things up
    global uiItems, dom, top, currentLcd, display
    uiItems = Folder('root', '')

    dom = parse(configfile)  # parse an XML file by name

    top = dom.documentElement

    currentLcd = lcd.OFF
    LcdOff()
    ProcessNode(top, uiItems)

    display = Display(uiItems)
    display.display()


init_menu()
player = Music_player()
player.play("/home/pi/RaspberryPiLcdMenu/Processing R2D2.mp3")

if DEBUG:
    print('start while')

lcdstart = datetime.now()
def main_loop():
    while 1:
        try:
            volume = player.song.volume()
        except:
            pass
        if (lcd.is_pressed(LEFT) or keyboard.is_pressed('left')):
            try:
                if player.song.is_playing():
                    player.song.seek(-5.0)
                    #sleep(0.25)
            except:# (OMXPlayerDeadError ,AttributeError) as e:
                display.update('l')
                display.display()
                #sleep(0.25)

        if (lcd.is_pressed(UP) or keyboard.is_pressed('up')):
            try:
                if player.song.is_playing():
                    player.song.set_volume(volume + 500)
            except:# (OMXPlayerDeadError ,AttributeError) as e:
                display.update('u')
                display.display()
                #sleep(0.25)

        if (lcd.is_pressed(DOWN) or keyboard.is_pressed('down')):
            try:
                if player.song.is_playing():
                    player.song.set_volume(volume - 500)
            except:# (OMXPlayerDeadError ,AttributeError):
                display.update('d')
                display.display()
                #sleep(0.25)

        if (lcd.is_pressed(RIGHT) or keyboard.is_pressed('right')):
            try:
                if player.song.is_playing():
                    player.song.seek(5.0)
                    #sleep(0.25)
            except:# (OMXPlayerDeadError ,AttributeError) as e:
                display.update('r')
                if player.playing:
                    lcd.clear()
                else:
                    display.display()
                #sleep(0.25)

        if (lcd.is_pressed(SELECT) or keyboard.is_pressed('enter')):
            try:
                if player.song.is_playing():
                    player.song.quit()
                    #sleep(0.25)
            except:# (OMXPlayerDeadError ,AttributeError) as e:
                display.update('s')
                display.display()
                #sleep(0.25)

        if AUTO_OFF_LCD:
            lcdtmp = lcdstart + timedelta(seconds=5)
            # if (datetime.now() > lcdtmp):
            #     #lcd.backlight(lcd.OFF)

        try:
            if player.song.is_playing():
                lcd.home()
                lcd.message('{}\n{}:{}  {}'.format(
                            player.song_str[34:50], 
                            strftime("%M:%S", gmtime(floor(player.song.position()))), 
                            strftime("%M:%S", gmtime(floor(player.song.duration()))),
                            floor(player.song.volume())))
        except OMXPlayerDeadError:
            if player.playing:
                player.playing = False
                player.song = ''
                display.display()
            print('finished')
        except (AttributeError, DBusException):
            pass

if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        try:
            player.song.quit()
            lcd.clear()
        except:
            
            pass
        lcd.clear()
        exit()
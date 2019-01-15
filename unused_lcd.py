# only use the following if you find useful
def Use10Network():
    "Allows you to switch to a different network for local connection"
    lcd.clear()
    lcd.message('Are you sure?\nPress Sel for Y')
    while 1:
        if lcd.is_pressed(LEFT):
            break
        if lcd.is_pressed(SELECT):
            # uncomment the following once you have a separate network defined
            # subprocess.getoutput("sudo cp /etc/network/interfaces.hub.10 /etc/network/interfaces")
            lcd.clear()
            lcd.message('Please reboot')
            sleep(1.5)
            break
        sleep(0.25)


# only use the following if you find useful
def UseDHCP():
    "Allows you to switch to a network config that uses DHCP"
    lcd.clear()
    lcd.message('Are you sure?\nPress Sel for Y')
    while 1:
        if lcd.is_pressed(LEFT):
            break
        if lcd.is_pressed(SELECT):
            # uncomment the following once you get an original copy in place
            # subprocess.getoutput("sudo cp /etc/network/interfaces.orig /etc/network/interfaces")
            lcd.clear()
            lcd.message('Please reboot')
            sleep(1.5)
            break
        sleep(0.25)


def ShowLatLon():
    if DEBUG:
        print('in ShowLatLon')


def SetLatLon():
    if DEBUG:
        print('in SetLatLon')


def SetLocation():
    if DEBUG:
        print('in SetLocation')
    global lcd
    list = []
    # coordinates usable by ephem library, lat, lon, elevation (m)
    list.append(['New York', '40.7143528', '-74.0059731', 9.775694])
    list.append(['Paris', '48.8566667', '2.3509871', 35.917042])
    selector = ListSelector(list, lcd)
    item = selector.Pick()
    # do something useful
    if (item >= 0):
        chosen = list[item]





# Get a word from the UI, a character at a time.
# Click select to complete input, or back out to the left to quit.
# Return the entered word, or None if they back out.
def GetWord():
    lcd.clear()
    lcd.blink()
    sleep(0.75)
    curword = list("A")
    curposition = 0
    while 1:
        if lcd.is_pressed(UP):
            if (ord(curword[curposition]) < 127):
                curword[curposition] = chr(ord(curword[curposition]) + 1)
            else:
                curword[curposition] = chr(32)
        if lcd.is_pressed(DOWN):
            if (ord(curword[curposition]) > 32):
                curword[curposition] = chr(ord(curword[curposition]) - 1)
            else:
                curword[curposition] = chr(127)
        if lcd.is_pressed(RIGHT):
            if curposition < DISPLAY_COLS - 1:
                curword.append('A')
                curposition += 1
                lcd.setCursor(curposition, 0)
            sleep(0.75)
        if lcd.is_pressed(LEFT):
            curposition -= 1
            if curposition < 0:
                lcd.noBlink()
                return
            lcd.setCursor(curposition, 0)
        if lcd.is_pressed(SELECT):
            # return the word
            sleep(0.75)
            return ''.join(curword)
        lcd.home()
        lcd.message(''.join(curword))
        lcd.setCursor(curposition, 0)
        sleep(0.25)

    lcd.noBlink()


# An example of how to get a word input from the UI, and then
# do something with it
def EnterWord():
    if DEBUG:
        print('in EnterWord')
    word = GetWord()
    lcd.clear()
    lcd.home()
    if word is not None:
        lcd.message('>' + word + '<')
        sleep(5)
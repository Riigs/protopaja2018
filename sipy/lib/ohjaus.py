#Tämä tiedosto sisältää funktiota, joita käytetään releiden ohjauksessa

from machine import Pin

#Laittaa releen päälle -> virta ei kulje laitteessa
def relayOn(relayPinNumber):
    p_out = Pin(relayPinNumber, mode=Pin.OUT)
    p_out.value(1)
    return

#Laittaa releen pois päältä -> virta kulkee laitteessa
def relayOff(relayPinNumber):
    p_out = Pin(relayPinNumber, mode=Pin.OUT)
    p_out.value(0)
    return

#Toteuttaa objektin mukaisen käskyn ohjaamiselle
def controlRelay(contVal, relayPinNumber):
    if contVal==1:
        relayOn(relayPinNumber)
        return 1
    elif contVal==0:
        relayOff(relayPinNumber)
        return 0

#Valitsee lopullisen ohjausarvon
#Tapaukset: 11, 00, 01, 10 -> 1, 0, 0, 0
def selControl(autCont, manCont):
    contVal = 1
    if autCont == manCont:
        contVal = autCont
    else:
        contVal = 1
    return contVal

#Suorittaa releen ohjauksen annetuilla parametreillä
def control(relayPinNumber, autoCont, manCont):
    contVal = selControl(autoCont, manCont)
    controlRelay(contVal, relayPinNumber)
    return

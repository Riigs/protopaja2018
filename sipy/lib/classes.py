from lib.mittaus import *
import os

#luokka kuormille
class load:
    def __init__(self,name,ID,commandbits,relayPin,maximumCurrent,phase,priority):
        #kuorman nimi ja ID-numero
        self.__name = name
        self.__ID = ID

        #releiden pinnit ja jännitteen luennan komentobitit
        #command bits - start, mode, chn (3), dont care (3)
        combits = []
        for letter in commandbits:
            combits.append(int(letter))
        self.__commandbits = combits
        self.__relayPin = relayPin

        #tämän tunnin kulutus, hetkellinen maksimivirta ja raja-arvo
        self.__curHourEne = 0
        self.__maximumCurrent = maximumCurrent
        self.__threshold = 0.9

        #muuttujat, jotka kertovat pitääkö releitä ohjata
        self.__autoCont = 0
        self.__manualCont = 0

        #kertoo mihin vaiheeseen kuorma kuuluu
        self.__phase = phase

        #kertoo mikä prioriteetti kuorman pudottamisella on (päättäkää suunta)
        self.__priority = priority

        #kertoo viimeisimmän virran
        self.__lastCur = 0
        #viimeisin mittaus
        self.__lastTime = 0

        #tallentaa tehoja viimeisen 10s ajalta
        self.__last10Sec = []

        #milloin 10s -lista on viimeksi resetattu
        self.__last10SecTime = 0

    def getLast10SecTime(self):
        return self.__last10SecTime

    def setLast10SecTime(self,val):
        self.__last10SecTime = val

    def getLast10Sec(self):
        return self.__last10Sec

    def resetLast10Sec(self):
        self.__last10Sec = []

    def getLastCur(self):
        return self.__lastCur

    def isActive(self):
        if self.__autoCont==1 or self.__manualCont==1:
            return False
        else:
            return True

    def getPriority(self):
        return self.__priority

    def updateLastTime(self,time):
        self.__lastTime = time

    def getLastTime(self):
        return self.__lastTime

    #määrittää tunnin kulutuksen käynnistyksessä
    def setCurHourEne(self,ene):
        self.__curHourEne = ene

    #lisää curhoureneen kulutetun energian
    def addCurHourEne(self,ene,power):
        self.__curHourEne += ene
        self.__last10Sec.append(power)

    #antaa maksimivirran
    def getMaxCur(self):
        maxCur = self.__threshold*self.__maximumCurrent
        return maxCur

    #avaa releen
    def relayAutoOpen(self):
        self.__autoCont = 1

    #sulkee releen
    def relayAutoClose(self):
        self.__autoCont = 0

    #avaa releen
    def relayManualOpen(self):
        self.__manualCont = 1

    #sulkee releen
    def relayManualClose(self):
        self.__manualCont = 0

    def getCurHourEne(self):
        return self.__curHourEne

    #antaa tämänhetkisen virran
    def getCurrent(self):
        current = adcRead(self.getCommandbits(),20)
        self.__lastCur = current
        return current

    #antaa kuorman nimen
    def getName(self):
        return self.__name

    def getID(self):
        return self.__ID

    def getCommandbits(self):
        return self.__commandbits

    def getPhase(self):
        return self.__phase

    def getRelayPin(self):
        return self.__relayPin

    #palauttaa controllimuuttujat tuplessa (muuttumaton lista)
    def getControlState(self):
        return (self.__autoCont,self.__manualCont)

    #antaa infoa kuormasta
    def info(self):
        print("Name:",self.__name)
        print("ID:",self.__ID)
        print("This load is part of the phase:",self.__phase)
        print("Pin of the relay:",self.__relayPin)
        print("This hour's consumed energy:",self.__curHourEne)
        print("Maximum current of this load:",self.__maximumCurrent)
        print("Load's dropping priority:",self.__priority)
        print("")



#luokka päävaiheille
class mainPhase:
    def __init__(self,name,ID,commandbits,maximumCurrent):
        #päävaiheen nimi ja ID-numero
        self.__name = name
        self.__ID = ID

        #lista, jossa vaiheen kuormat
        self.__loads = []

        #tämän tunnin kulutus, maksimi hetkellinen virta ja raja-arvo
        self.__curHourEne = 0
        self.__maximumCurrent = maximumCurrent
        self.__threshold = 0.9

        #command bits - start, mode, chn (3), dont care (3)
        combits = []
        for letter in commandbits:
            combits.append(int(letter))
        self.__commandbits = combits

        self.__lastCur = 0

        #tallentaa tehoja viimeisen 10s ajalta
        self.__last10Sec = []

        #milloin 10s -lista on viimeksi resetattu
        self.__last10SecTime = 0

        #viimeisin mitattu teho
        self.__lastPower = 0

    def getLastPower(self):
        return self.__lastPower

    def getLast10SecTime(self):
        return self.__last10SecTime

    def setLast10SecTime(self,val):
        self.__last10SecTime = val

    def getLast10Sec(self):
        return self.__last10Sec

    def resetLast10Sec(self):
        self.__last10Sec = []

    def getLastCur(self):
        return self.__lastCur

    def loadPrioritize(self):
        self.__loads.sort(key=lambda load: load.getPriority())

    def getCurHourEne(self):
        return self.__curHourEne

    def returnLoads(self):
        return self.__loads

    #antaa tämänhetkisen virran
    def getCurrent(self):
        current = adcRead(self.getCommandbits(),50)
        self.__lastCur = current
        return current

    #antaa maksimivirran
    def getMaxCur(self):
        maxCur = self.__threshold*self.__maximumCurrent
        return maxCur

    #antaa vaiheen nimen
    def getName(self):
        return self.__name

    def getID(self):
        return self.__ID

    def getCommandbits(self):
        return self.__commandbits

    #määrittää tunnin kulutuksen käynnistyksessä
    def setCurHourEne(self,ene):
        self.__curHourEne = ene

    def addLast10Sec(self,power):
        self.__last10Sec.append(power)

    def updateCurHourEne(self):
        self.__curHourEne = 0
        for load in self.__loads:
            self.__curHourEne += load.getCurHourEne()

    #lisää vaiheeseen kuorman
    def addLoad(self,load):
        self.__loads.append(load)

    #kutsutaan tunnin välein, resettaa tunnin kulutuksen
    def resetHour(self):
        self.__curHourEne = 0

    #antaa infoa päävaiheesta
    def info(self):
        print("Name:",self.__name)
        print("ID:",self.__ID)
        print("This hour's consumed energy:",self.__curHourEne)
        print("Maximum current of this phase:",self.__maximumCurrent)
        print("Loads:")
        if len(self.__loads) == 0:
            print("None")
        for load in self.__loads:
            print(load.getName())
        print("")

#testausta
#kuorma1 = load("Lattialämmitys",12345,1,2,10,1,0)
#kuorma1.info()
#print("")
#kuorma1.info()

#print("")

#päävaihe1 = mainPhase("Päävaihe 1",98765,3,36)
#päävaihe1.addLoad(kuorma1)
#päävaihe1.info()

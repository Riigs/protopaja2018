from lib.mittaus import *
import os

#luokka kuormille
class load:
    def __init__(self,name,ID,sensorPin,relayPin,maximumCurrent,phase,priority):
        #kuorman nimi ja ID-numero
        self.__name = name
        self.__ID = ID

        #sensorien ja releiden pinnit
        self.__sensorPin = sensorPin
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

        self.__lastTime = 0

    def updateLastTime(self,time):
        self.__lastTime = time

    def getLastTime(self):
        return self.__lastTime

    #lisää curhoureneen kulutetun energian
    def addCurHourEne(self,ene):
        self.__curHourEne += ene

    #antaa maksimivirran
    def getMaxCur(self):
        maxCur = self.__threshold*self.__maximumCurrent
        return maxCur

    #avaa releen
    def relayDisconn(self):
        self.__autoCont = 1
        #tähän joku timeri joka palauttaa releen tilan jossain vaiheessa

    #kutsutaan tunnin välein, resettaa tunnin kulutuksen
    #Lisäksi poistaa kuluneen tunnin tiedot
    def resetHour(self):
        filename = str(self.__ID)+".txt"
        path = "temp/" + filename
        #path = os.path.join("temp", filename)
        try:
            rm(path)
            return 1
        except:
            return 0

    def getCurHourEne(self):
        return self.__curHourEne

    #antaa tämänhetkisen virran
    def getCurrent(self):
        current = adc_read(self.__sensorPin)
        return current

    #antaa tämänhetkisen kulutuksen ja tallentaa sen ID tiedostoon
    def getCons(self):
        cons = adc_read(self.__sensorPin)
        adc_save(cons, self.__ID)
        return cons

    #antaa kuorman nimen
    def getName(self):
        return self.__name

    def getPhase(self):
        return self.__phase

    #antaa infoa kuormasta
    def info(self):
        print("Name:",self.__name)
        print("ID:",self.__ID)
        print("This load is part of the phase:",self.__phase)
        print("Pin of the sensor:",self.__sensorPin)
        print("Pin of the relay:",self.__relayPin)
        print("This hour's consumed energy:",self.__curHourEne)
        print("Maximum current of this load:",self.__maximumCurrent)
        print("Load's dropping priority:",self.__priority)
        print("")



#luokka päävaiheille
class mainPhase:
    def __init__(self,name,ID,sensorPin,maximumCurrent):
        #päävaiheen nimi ja ID-numero
        self.__name = name
        self.__ID = ID

        #virtasensorin pinni ja lista, jossa vaiheen kuormat
        self.__sensorPin = sensorPin
        self.__loads = []

        #tämän tunnin kulutus, maksimi hetkellinen virta ja raja-arvo
        self.__curHourEne = 0
        self.__maximumCurrent = maximumCurrent
        self.__threshold = 0.9

    def getCurHourEne(self):
        return self.__curHourEne

    #antaa tämänhetkisen virran
    def getCurrent(self):
        current = adc_read(self.__sensorPin)
        return current

    #antaa maksimivirran
    def getMaxCur(self):
        maxCur = self.__threshold*self.__maximumCurrent
        return maxCur

    #avaa releen
    def relayDisconn(self):
        self.__autoCont = 1
        #tähän joku timeri joka palauttaa releen tilan jossain vaiheessa

    #antaa vaiheen nimen
    def getName(self):
        return self.__name

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

    #antaa tämänhetkisen kulutuksen
    def getCons(self):
        return adc_read(self.__sensorPin)

    #antaa infoa päävaiheesta
    def info(self):
        print("Name:",self.__name)
        print("ID:",self.__ID)
        print("Pin of the sensor:",self.__sensorPin)
        print("This hour's consumed energy:",self.__curHourEne)
        print("Maximum current of this phase:",self.__maximumCurrent)
        print("Loads:")
        if len(self.__loads) == 0:
            print("None")
        for load in self.__loads:
            print(load.getName())
        print("")



#luokka kuukauden maksimitunnille, kertoo sekä tunnin kulutuksen, että päivämäärän
class maxHourDate:
    def __init__(self,maxHour,day,month,year):
        self.__maxHour = maxHour
        self.__month = month
        self.__year = year
        self.__date = str(day) + "." + str(self.__month) + "." +  str(self.__year)

    def info(self):
        print("The biggest consumption in an hour this month:",self.__maxHour)
        print("And it was in:",self.__date)



#testausta
#kuorma1 = load("Lattialämmitys",12345,1,2,10,1,0)
#kuorma1.info()
#print("")
#kuorma1.info()

#print("")

#päävaihe1 = mainPhase("Päävaihe 1",98765,3,36)
#päävaihe1.addLoad(kuorma1)
#päävaihe1.info()

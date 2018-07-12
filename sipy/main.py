#importataan classes-filestä kaikki classit useemalla wild cardia
from lib.classes import *
import time
import os
from machine import Timer

#funktioiden määrittely
def openLoads(loads,loadFile):
    #path = os.path.join("files", loadFile)
    path = "files/" + loadFile
    loadData = open(path,'r')
    for line in loadData:
        data = line.split(',')
        if len(data) == 7:
            newLoad = load(data[0],int(data[1]),data[2],data[3],int(data[4]),int(data[5]),int(data[6]))
            loads.append(newLoad)
    loadData.close()
    return

def sortLoads(loads,phases):
    for load in loads:
        phase = load.getPhase()
        if phase==1:
            phases[0].addLoad(load)
        elif phase==2:
            phases[1].addLoad(load)
        elif phase==3:
            phases[2].addLoad(load)
        else:
            print("Kuorma", load.getName() ,"ei kuulu mihinkään vaiheeseen.")


def openPhases(phases,phasesFile):
    #path = os.path.join("files", phasesFile)
    path = "files/" + phasesFile
    phasesData = open(path,'r')
    for line in phasesData:
        data = line.split(',')
        if len(data) == 4:
            newPhase = mainPhase(data[0],int(data[1]),data[2],int(data[3]))
            phases.append(newPhase)
    phasesData.close()
    return

def openMonthMax(maxFile):
    #path = os.path.join("files", maxFile)
    path = "files/" + maxFile
    maxData = open(path,'r')
    line = maxData.readline()
    data = line.split(',')
    val = maxHourDate(0,0,0,0)
    if len(data) == 4:
        val = maxHourDate(int(data[0]),int(data[1]),int(data[2]),int(data[3]))
    maxData.close()
    return val

#Mittaa ja tulostaa jokaisen kuorman virran
def getCurrentAll():
    for load in loads:
        v=load.getCurrent()
        print(load.getName(), v, "A")
        time.sleep(0.5)

#Mittaa ja tulostaa jokaisen kuorman hetkellisen kulutuksen
def getConsAll():
    for load in loads:
        v=load.getCons()
        print(load.getName(), v)
        time.sleep(0.5)

def resetHourAll():
    for load in loads:
        load.resetHour()

def getHourEneAll():
    for load in loads:
        load.getCurHourEne()

def printInfo(data):
    try:
        for piece in data:
            piece.info()
    except:
        data.info()



#päälooppi
def main():
    printInfo(loads)
    printInfo(phases)
    printInfo(monthMax)
    print("............\n")

    running = True
    chrono.start()
    tiimari.start()
    while running:
        #mittaus
        #getCurrentAll()
        #käynnistetään mittauslooppi jos aikaa edellisestä mittauksesta on kulunut ainakin 0.5 sekuntia
        if chrono.read() - latestTime >= 0.5:
            for load in loads:
                #mitataan virta ja lasketaan kulutus ja lisätään se kuormien omiin arvoihin
                current = load.getCurrent()
                print("Kuorman " + load.getName() + " virta: "+str(current)+"A")
                #verrataan virtaa raja-arvoon ja avataan piiri jos virta ylittää rajan
                if current >= load.getMaxCur():
                    load.relayDisconn()

                power = current * voltage
                newTime = chrono.read()
                energy = power * (newTime - load.getLastTime())
                load.updateLastTime(newTime)
                load.addCurHourEne(energy)
                print("")

            totalEne = 0
            for phase in phases:
                current = phase.getCurrent()
                print("Vaiheen " + phase.getName() + " virta: "+str(current)+"A")
                if current >= phase.getMaxCur():
                    phase.relayDisconn()
                #päivitetään nykyisen tunnin kulutus
                phase.updateCurHourEne()
                totalEne += phase.getCurHourEne()
                print("")

            print("Tunnin kokonaiskulutus tähän mennessä:",totalEne)
            print("")

        #hetkellisen kulutuksen laskeminen

        #tämän tunnin kulutuksen päivittäminen
        #print("............\n")
        #getHourEneAll()
        #resetHourAll()


        #ohjauksen tarkistaminen pilvestä
        #ohjauksen tarkistaminen automaattisesti
        #releiden tilojen muuttaminen (virran katkominen tai palauttaminen)
        if tiimari.read()>10:
            running = False
    printInfo(loads)
    printInfo(phases)

#muuttujien asettaminen ja tietojen lataaminen tiedostosta, ja hard
#koodataan joidenkin muuttujien arvoja

#luodaan timeri ajan mittaamiseen
chrono = Timer.Chrono()
tiimari = Timer.Chrono()
latestTime = 0

#oletetaan jännitteen pysyvän vakio 230-arvoisena
voltage = 230

#eri sulakkeiden maksimivirrat
phaseMaxCur = 36
loadMaxCur = 10

#maksimi tuntiteho ja tämänhetkisen tunnin kulutus ja raja-arvo
maxHour = 2000
hourThreshold = 0.9

#tiedostojen nimet
loadFile = "loads.txt"
phaseFile = "phases.txt"
monthMaxFile = "monthMax.txt"

#avataan eri kuormat tiedostosta
loads = []
openLoads(loads,loadFile)

#avataan tiedot eri vaiheista tiedostosta
phases = []
openPhases(phases,phaseFile)
sortLoads(loads,phases)

#avataan tiedot kuukauden suurimmasta tuntitehosta tiedostosta
monthMax = openMonthMax(monthMaxFile)

#käynnistää main loopin vain jos tiedosto itse käynnistetään, eikä sitä
#importata toiseen tiedostoon
if __name__ == '__main__':
    main()

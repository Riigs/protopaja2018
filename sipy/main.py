#importataan classes-filestä kaikki classit useemalla wild cardia
from lib.classes import *

#funktioiden määrittely
def openLoads(loads,loadFile):
    loadData = open(loadFile,'r')
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
    phasesData = open(phasesFile,'r')
    for line in phasesData:
        data = line.split(',')
        if len(data) == 4:
            newPhase = mainPhase(data[0],int(data[1]),data[2],int(data[3]))
            phases.append(newPhase)
    phasesData.close()
    return

def openMonthMax(maxFile):
    maxData = open(maxFile,'r')
    line = maxData.readline()
    data = line.split(',')
    val = maxHourDate(0,0,0,0)
    if len(data) == 4:
        val = maxHourDate(int(data[0]),int(data[1]),int(data[2]),int(data[3]))
    maxData.close()
    return val

def printInfo(data):
    try:
        for piece in data:
            piece.info()
    except:
        data.info()

#päälooppi
def main():
    running = True
    while running:
        #mittaus
        #hetkellisen kulutuksen laskeminen
        #tämän tunnin kulutuksen päivittäminen
        #ohjauksen tarkistaminen pilvestä
        #ohjauksen tarkistaminen automaattisesti
        #releiden tilojen muuttaminen (virran katkominen tai palauttaminen)
        printInfo(loads)
        printInfo(phases)
        printInfo(monthMax)
        running = False

#muuttujien asettaminen ja tietojen lataaminen tiedostosta, ja hard
#koodataan joidenkin muuttujien arvoja

#eri sulakkeiden maksimivirrat
phaseMaxCur = 36
loadMaxCur = 10

#maksimi tuntiteho
maxHour = 2000

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

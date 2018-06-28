#importataan classes-filestä kaikki classit useemalla wild cardia
from classes import *

#funktioiden määrittely
def openLoads(loads,loadFile):
    loadData = open(loadFile,'r')
    for line in loadData:
        data = line.split(',')
        if len(data) == 7:
            newLoad = load(data[0],data[1],data[2],data[3],data[4],data[5],data[6])
            loads.append(newLoad)
    loadData.close()
    return

def openPhases(phases,phasesFile):
    phasesData = open(phasesFile,'r')
    for line in phasesData:
        data = line.split(',')
        if len(data) == 4:
            newPhase = mainPhase(data[0],data[1],data[2],data[3])
            phases.append(newPhase)
    phasesData.close()
    return

def openMonthMax():
    val = maxHourDate(1000,1,1,2000)
    return val

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
        loads[0].info()
        phases[0].info()
        running = False

#muuttujien asettaminen ja tietojen lataaminen tiedostosta, ja hard
#koodataan joidenkin muuttujien arvoja

#eri sulakkeiden maksimivirrat
phaseMaxCur = 36
loadMaxCur = 10

#maksimi tuntiteho ja suurimman tuntitehon päivä
maxHour = 2000
monthMaxHour = maxHourDate(0,1,1,2000)

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

#avataan tiedot kuukauden suurimmasta tuntitehosta tiedostosta
monthMax = openMonthMax()

#käynnistää main loopin vain jos tiedosto itse käynnistetään, eikä sitä
#importata toiseen tiedostoon
if __name__ == '__main__':
    main()

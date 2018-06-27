#importataan classes-filestä kaikki classit useemalla wild cardia
from lib.classes import *

#funktioiden määrittely
def openLoads(loads):
    return

def openPhases(phases):
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
        print("kraak")
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
openLoads(loads)

#avataan tiedot eri vaiheista tiedostosta
phases = []
openPhases(phases)

#avataan tiedot kuukauden suurimmasta tuntitehosta tiedostosta
monthMax = openMonthMax()

#käynnistää main loopin vain jos tiedosto itse käynnistetään, eikä sitä
#importata toiseen tiedostoon
if __name__ == '__main__':
    main()

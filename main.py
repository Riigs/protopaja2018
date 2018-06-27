#importataan classes-filestä kaikki classit useemalla wild cardia
from classes import *

testLoad = load("Sähköauton latausasema",12345,1,2,10,1,0)
testLoad.info()




#muuttujien asettaminen ja tietojen lataaminen tiedostosta, ja hard
#koodataan joidenkin muuttujien arvoja

#eri sulakkeiden maksimivirrat
phaseMaxCur = 36
loadMaxCur = 10

#maksimi tuntiteho ja suurimman tuntitehon päivä
maxHour = 2000
monthMaxHour = maxHourDate(0,1,1,2000)

#avataan eri kuormat tiedostosta
#openLoads()

#avataan tiedot eri vaiheista tiedostosta
#openPhases()

#avataan tiedot kuukauden suurimmasta tuntitehosta tiedostosta
#openMonthMax()




#päälooppi
running = True
while running:
    #mittaus
    #hetkellisen kulutuksen laskeminen
    #tämän tunnin kulutuksen päivittäminen
    #ohjauksen tarkistaminen pilvestä
    #ohjauksen tarkistaminen automaattisesti
    #releiden tilojen muuttaminen (virran katkominen tai palauttaminen)
    
    running = False

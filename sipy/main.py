#importataan classes-filestä kaikki classit useemalla wild cardia
from lib.classes import *
from lib.ohjaus import *
from machine import Timer
from network import WLAN
import time
import os
import sys
import lib.urequests as urequests

#nettiin yhdistys
wlan = WLAN(mode=WLAN.STA)
nets = wlan.scan()
for net in nets:
    if net.ssid == 'aalto open':
        print('Network found!')
        wlan.connect(net.ssid, timeout=5000)
        while not wlan.isconnected():
            machine.idle() # save power while waiting
        print('WLAN connection succeeded!')
        break

#urequestin testausta
#response = urequests.get('http://jsonplaceholder.typicode.com/albums/1')
#print(response.text)
#sys.exit()

pycom.heartbeat(False)

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
    for phase in phases:
        phase.loadPrioritize()


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

def openPass(passFile):
    path = "files/" + passFile
    passData = open(path,'r')
    line = passData.readline()
    data = line.split(',')
    secret = [data[0],data[1]]
    passData.close()
    return secret

#Mittaa ja tulostaa jokaisen kuorman virran
def getCurrentAll():
    for load in loads:
        v=load.getCurrent()
        print(load.getName(), v, "A")
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
    latestTime = 0
    while running:
        #tarkistetaan onko kulunut 10s
        for load in loads:
            time = chrono.read()
            if time - load.getLast10SecTime() >= 10:
                #keskiarvon lasku
                sum = 0
                for val in load.getLast10Sec():
                    sum += val
                ave = sum/len(load.getLast10Sec())

                input = load.getName()+' power='+str(ave)
                #urequests vaatii että data on enkoodattu utf-8:ssa(funktion oletusasetus)
                url = "http://ec2-34-245-7-230.eu-west-1.compute.amazonaws.com:8086/write?db=newtest&u="+secrets[0]+"&p="+secrets[1]
                print(url)
                resp = urequests.post(url,data=input.encode())
                print(resp.status_code)

                #lataus pilveen
#https://forum.micropython.org/viewtopic.php?t=3969
#https://forum.pycom.io/topic/1061/https-post-using-urequests-py-and-guru-mediation-error
#https://techtutorialsx.com/2017/06/11/esp32-esp8266-micropython-http-get-requests/
#https://docs.python.org/2/tutorial/datastructures.html

                #tyhjennetään lista ja asetetaan uusi resettausaika
                load.setLast10SecTime(chrono.read())
                load.resetLast10Sec()

        #käynnistetään mittauslooppi jos aikaa edellisestä mittauksesta on kulunut ainakin 0.5 sekuntia
        if chrono.read() - latestTime >= 0.5:
            pycom.rgbled(0x330000) # red
            latestTime = chrono.read()
            for load in loads:
                if load.isActive():
                    #mitataan virta ja lasketaan kulutus ja lisätään se kuormien omiin arvoihin
                    current = load.getCurrent()
                    print("Kuorman " + load.getName() + " virta: "+str(current)+"A")

                    #verrataan virtaa raja-arvoon ja avataan piiri jos virta ylittää rajan
                    #tätä ei itse asiassa tarvitakaan
                    #if current >= load.getMaxCur():
                        #load.relayAutoOpen()

                    power = current * voltage
                    newTime = chrono.read()
                    #wattisekunnit wattitunneiksi
                    energy = power * (newTime - load.getLastTime()) / 3600
                    load.updateLastTime(newTime)
                    load.addCurHourEne(energy,power)
                    print("")

                #kuormien palautus päälle
                elif load.isActive() == False:
                    #getPhase palauttaa 1-3, halutaan 0-2
                    phaseNum = load.getPhase() - 1
                    phasePower = phases[phaseNum].getLastCur() * voltage
                    loadPower = load.getLastCur() * voltage
                    #tarkistetaan onko nykyinen vaiheteho ja kuorman teho yhdessä tarpeeksi pieni, suljetaan rele jos on
                    if phasePower + loadPower < maxPower * hourThreshold:
                        load.relayAutoClose()
                        break

            #tehdään mittaukset ja rajoitukset päävaiheille
            totalEne = 0
            for phase in phases:
                current = phase.getCurrent()
                power = current * voltage
                print("Vaiheen " + phase.getName() + " virta: "+str(current)+"A")

                #verrataan virtaa maksimivirtaan ja tehoa maksimitehoon, poistetaan yksi pienimmän prioriteetin kuorma jos ylittyy
                if current >= phase.getMaxCur():
                    for load in phase.returnLoads():
                        if load.isActive():
                            load.relayAutoOpen()
                            break
                if power >= maxPower:
                    for load in phase.returnLoads():
                        if load.isActive():
                            load.relayAutoOpen()
                            break

                #päivitetään nykyisen tunnin kulutus
                phase.updateCurHourEne()
                totalEne += phase.getCurHourEne()
                print("")

            print("Tunnin kokonaiskulutus tähän mennessä:",totalEne)
            print("")

            #kuormien sulku kun maksimienergia ylitetään
            #if totalEne >= hourThreshold * maxHour:
                #for phase in phases:
                    #for load in phase.returnLoads():
                        #load.relayAutoOpen()

            #releiden ohjaus muuttujien mukaan
            for load in loads:
                controlVars = load.getControlState()
                print("Name:",load.getName(),"Autocont:",controlVars[0],"Manualcont:",controlVars[1])
                relayPin = load.getRelayPin()
                autoCont = controlVars[0]
                manualCont = controlVars[1]
                control(relayPin,autoCont,manualCont)

            #pycom.rgbled(0x000000)
            print("Mittauksiin ja ohjauksiin kulunut aika:",chrono.read()-latestTime)
            pycom.rgbled(0x000000)
            print("Kulutuksia:",loads[1].getLast10Sec())
            #ohjauksen tarkistaminen pilvestä tarvitaan viel

        #if tiimari.read()>10:
            #running = False

    printInfo(loads)
    printInfo(phases)

#muuttujien asettaminen ja tietojen lataaminen tiedostosta, ja hard
#koodataan joidenkin muuttujien arvoja

#luodaan timeri ajan mittaamiseen
chrono = Timer.Chrono()
tiimari = Timer.Chrono()

#oletetaan jännitteen pysyvän vakio 230-arvoisena
voltage = 235

#eri sulakkeiden maksimivirrat
phaseMaxCur = 36
loadMaxCur = 10

#maksimi tuntiteho ja tämänhetkisen tunnin kulutus ja raja-arvo
#yksiköt watteina ja wattitunteina
maxHour = 2000
maxPower = maxHour
hourThreshold = 0.9

#tiedostojen nimet
loadFile = "loads.txt"
phaseFile = "phases.txt"
monthMaxFile = "monthMax.txt"
passFile = "pass.txt"

#avataan eri kuormat tiedostosta
loads = []
#kuormien nimet pitää olla ilman ääkkösiä
openLoads(loads,loadFile)

#avataan tiedot eri vaiheista tiedostosta
phases = []
openPhases(phases,phaseFile)
sortLoads(loads,phases)

#avataan tiedot kuukauden suurimmasta tuntitehosta tiedostosta
monthMax = openMonthMax(monthMaxFile)

#avataan salasanat ja käyttäjät tiedostosta
#tiedosto muotoa:
#username,password,mitä tahansa tekstiä
secrets = openPass(passFile)

#käynnistää main loopin vain jos tiedosto itse käynnistetään, eikä sitä
#importata toiseen tiedostoon
if __name__ == '__main__':
    main()

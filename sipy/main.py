#importataan classes-filestä kaikki classit useemalla wild cardia
from lib.classes import *
from lib.ohjaus import *
from machine import Timer
from network import WLAN
from machine import RTC
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


#rtc:n testausta
#rtc = RTC()
#rtc.ntp_sync("fi.pool.ntp.org",100)

#while rtc.synced()==False:
#    print("Waiting for sync...")
#rtc.ntp_sync(None,100)

#tim = rtc.now()
#print(tim)
#hour = tim[3]
#year = tim[0]
#print("Tunti:",hour,"Vuosi:",year)
#sys.exit()


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

def openPass(passFile):
    path = "files/" + passFile
    passData = open(path,'r')
    line = passData.readline()
    data = line.split(',')
    secret = [data[0],data[1]]
    passData.close()
    return secret

def setMeasTime(measTime,curHour):
    measTime[0] = curHour[0]
    measTime[1] = curHour[1]
    measTime[2] = curHour[2]
    measTime[3] = curHour[3]

def parseStringToTime(string):
    year = int(string[0:4])
    month = int(string[5:7])
    day = int(string[8:10])
    hour = int(string[11:13])
    return [year,month,day,hour]

#lataa pilvestä kulutukset nykyiselle tunnille ja asettaa ne
def getCloudEnes(list,rtc,secrets):
    url = "http://ec2-34-245-7-230.eu-west-1.compute.amazonaws.com:8086/query?db=newtest&u="+secrets[0]+"&p="+secrets[1]+"&pretty=true"

    for thing in list:
        time = rtc.now()
        year = time[0]
        month = time[1]
        day = time[2]
        hour = time[3]
        curTime = [year,month,day,hour]

        name = thing.getName()
        query = '&q=SELECT+last(totalEne)+FROM+"'+name+'"'
        try:
            resp = urequests.get(url+query)
            print(resp.status_code)
            jsonOut = resp.json()

            print(jsonOut)
            print("Aika:",jsonOut["results"][0]["series"][0]["values"][0][0])
            print("Arvo:",jsonOut["results"][0]["series"][0]["values"][0][1])

            lastTime = parseStringToTime(jsonOut["results"][0]["series"][0]["values"][0][0])
            if lastTime[0]==curTime[0] and lastTime[1]==curTime[1] and lastTime[2]==curTime[2] and lastTime[3]==curTime[3]:
                ene = jsonOut["results"][0]["series"][0]["values"][0][1]
                thing.setCurHourEne(ene)
                setMeasTime(measTime,curTime)

        except:
            print("Query failed.")
            pass


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
    print("............\n")

    running = True
    chrono.start()
    tiimari.start()
    latestTime = 0
    while running:

        #tarkistetaan onko tunti vaihtunut, jos on, nollataan tuntikulutukset
        time = rtc.now()
        year = time[0]
        month = time[1]
        day = time[2]
        hour = time[3]
        curTime = [year,month,day,hour]
        if (measTime[0]==curTime[0] and measTime[1]==curTime[1] and measTime[2]==curTime[2] and measTime[3]==curTime[3])==False:
            for load in loads:
                load.setCurHourEne(0)
            for phase in phases:
                phase.setCurHourEne(0)

        #tarkistetaan onko kulunut 10s ja lähetetään dataa
        for load in loads:
            time = chrono.read()
            if time - load.getLast10SecTime() >= 10:
                #keskiarvon lasku
                sum = 0
                for val in load.getLast10Sec():
                    sum += val

                #otetaan huomioon nollatapaus
                if len(load.getLast10Sec())==0:
                    ave = 0
                else:
                    ave = sum/len(load.getLast10Sec())

                input = load.getName()+' power='+str(ave)+',totalEne='+str(load.getCurHourEne())
                print(input)
                #urequests vaatii että data on enkoodattu utf-8:ssa(funktion oletusasetus)
                url = "http://ec2-34-245-7-230.eu-west-1.compute.amazonaws.com:8086/write?db=newtest&u="+secrets[0]+"&p="+secrets[1]
                print(url)
                #joskus datan lataus epäonnistuu ja ohjelma kaatuu ilman try-exceptiä
                try:
                    resp = urequests.post(url,data=input.encode())
                except:
                    pass

                #tyhjennetään lista ja asetetaan uusi resettausaika
                load.setLast10SecTime(chrono.read())
                load.resetLast10Sec()

        #tarkistetaan onko kulunut 10s ja lähetetään dataa
        for phase in phases:
            time = chrono.read()
            if time - phase.getLast10SecTime() >= 10:
                #keskiarvon lasku
                sum = 0
                for val in phase.getLast10Sec():
                    sum += val

                #otetaan huomioon nollatapaus
                if len(phase.getLast10Sec())==0:
                    ave = 0
                else:
                    ave = sum/len(phase.getLast10Sec())

                input = phase.getName()+' power='+str(ave)+',totalEne='+str(phase.getCurHourEne())
                print(input)
                #urequests vaatii että data on enkoodattu utf-8:ssa(funktion oletusasetus)
                url = "http://ec2-34-245-7-230.eu-west-1.compute.amazonaws.com:8086/write?db=newtest&u="+secrets[0]+"&p="+secrets[1]
                print(url)

                #tarvitaan try except mahdollisen kaatumisen estämiseksi
                try:
                    resp = urequests.post(url,data=input.encode())
                    print(resp.status_code)
                except:
                    pass

                #tyhjennetään lista ja asetetaan uusi resettausaika
                phase.setLast10SecTime(chrono.read())
                phase.resetLast10Sec()

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
passFile = "pass.txt"

#avataan eri kuormat tiedostosta
loads = []
#kuormien nimet pitää olla ilman ääkkösiä,ei välilyöntejä,
openLoads(loads,loadFile)

#avataan tiedot eri vaiheista tiedostosta
phases = []
openPhases(phases,phaseFile)
sortLoads(loads,phases)

#kellon päivittäminen uudelleenkäynnistyksessä internetin kautta
rtc = RTC()
rtc.ntp_sync("fi.pool.ntp.org",100)
while rtc.synced()==False:
    print("Waiting for sync...")
rtc.ntp_sync(None,100)
print("Sync complete!")

#mitä tuntia mitataan nyt
measTime = [2018,12,25,13]
time = rtc.now()
year = time[0]
month = time[1]
day = time[2]
hour = time[3]
curTime = [year,month,day,hour]
setMeasTime(measTime,curTime)

#avataan salasanat ja käyttäjät tiedostosta
#tiedosto muotoa:
#username,password,mitä tahansa tekstiä
secrets = openPass(passFile)

#ladataan nykyisen tunnin kulutukset pilvestä
getCloudEnes(loads,rtc,secrets)
getCloudEnes(phases,rtc,secrets)

#käynnistää main loopin vain jos tiedosto itse käynnistetään, eikä sitä
#importata toiseen tiedostoon
if __name__ == '__main__':
    main()

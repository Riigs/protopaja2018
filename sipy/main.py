#importataan classes-filestä kaikki classit useemalla wild cardia
from lib.classes import *
from lib.ohjaus import *
from machine import Timer
from machine import RTC
from machine import Pin
from network import WLAN
import machine
import usocket
import time
import ujson
import _thread
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

pycom.heartbeat(False)

#funktioiden määrittely
def openLoads(loads):
    #path = "files/" + loadFile
    #loadData = open(path,'r')
    #try:
    resp = urequests.get('https://salty-mountain-85076.herokuapp.com/api/loads')
    loadData = resp.json()
    for nuload in loadData:
        #data = line.split(',')
        #if len(data) == 7:
        #newLoad = load(data[0],int(data[1]),data[2],data[3],int(data[4]),int(data[5]),int(data[6]))
        newLoad = load(nuload['name'],nuload['id'],nuload['commandBits'],nuload['relayPin'],int(nuload['maxCurrent']),int(nuload['phase']),
            int(nuload['priority']))
        loads.append(newLoad)
    #loadData.close()
    #except:
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
    #path = "files/" + phasesFile
    #phasesData = open(path,'r')
    #try:
    resp = urequests.get('https://salty-mountain-85076.herokuapp.com/api/phases')
    phasesData = resp.json()
    for phase in phasesData:
        #data = line.split(',')
        #if len(data) == 4:
        newPhase = mainPhase(phase['name'],phase['id'],phase['commandBits'],int(phase['maxCurrent']))
        phases.append(newPhase)
    #phasesData.close()
    #except:
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
        timeNow = rtc.now()
        year = timeNow[0]
        month = timeNow[1]
        day = timeNow[2]
        hour = timeNow[3]
        curTime = [year,month,day,hour]

        name = thing.getName()
        query = '&q=SELECT+last(totalEne)+FROM+"Measurement"+WHERE+"id"=\''+str(thing.getID())+"\'"
        #print(query)
        try:
            resp = urequests.get(url+query)
            #print(resp.status_code)
            jsonOut = resp.json()

            #print(jsonOut)
            #print("Aika:",jsonOut["results"][0]["series"][0]["values"][0][0])
            #print("Arvo:",jsonOut["results"][0]["series"][0]["values"][0][1])

            lastTime = parseStringToTime(jsonOut["results"][0]["series"][0]["values"][0][0])
            if lastTime[0]==curTime[0] and lastTime[1]==curTime[1] and lastTime[2]==curTime[2] and lastTime[3]==curTime[3]:
                ene = jsonOut["results"][0]["series"][0]["values"][0][1]
                thing.setCurHourEne(ene)
                setMeasTime(measTime,curTime)

        except:
            print("Query failed.")
            pass

#palauttaa kuukauden viimeisen päivän
def getFinalDay(month,year):
    if month==1 or month==3 or month==5 or month==7 or month==8 or month==10 or month==12:
        return 31
    elif month==4 or month==6 or month==9 or month==11:
        return 30

    elif month==2:
        if year%4==0:
            if year%100==0:
                if year%400==0:
                    return 29
                else:
                    return 28
            else:
                return 29
        else:
            return 28

#tulostaa 12 kuukauden ajalta suurimman kulutuksen tunnin tiedot ja palauttaa kulutuksen
def getCloudMaxHourPower(secrets,thing):
    ene = 0

    try:
        url = "http://ec2-34-245-7-230.eu-west-1.compute.amazonaws.com:8086/query?db=newtest&u="+secrets[0]+"&p="+secrets[1]+"&pretty=true"
        query = '&q=SELECT+max(totalEne)+FROM+"Measurement"+WHERE+"id"=\''+str(thing.getID())+'\'+AND+time>=now()-365d'

        resp = urequests.get(url+query)
        #print(resp.status_code)
        jsonOut = resp.json()
        #print(jsonOut)

        ene = jsonOut["results"][0]["series"][0]["values"][0][1]
        newtime = parseStringToTime(jsonOut["results"][0]["series"][0]["values"][0][0])
        print("")
        #tällä hetkellä lisää 3h koska utc, mutta ei pysy samana koska kesä- ja talviaika
        print("The greatest hourly power in the last 12 months was: "+str(ene)+", and this hour was in: "+str(newtime[2])+"."+str(newtime[1])+"."+str(newtime[0])+" "+str(newtime[3]+3)+"-"+str(newtime[3]+1+3))
    except:
         pass

    print("")
    return ene

def printInfo(data):
    try:
        for piece in data:
            piece.info()
    except:
        data.info()

def getTotalEnergy(phases):
    total = 0
    for phase in phases:
        total += phase.getCurHourEne()
    return total

def cloudThread(threadLoads,threadPhases):
    global maxHour
    while True:
        #controllimuuttujien hakeminen
        try:
            url = 'http://salty-mountain-85076.herokuapp.com/api/loads'
            threadData = urequests.get(url).json()
            for threadUnit in threadData:
                for threadLoad in threadLoads:
                        if threadLoad.getID()==threadUnit['id']:
                            threadVal = int(threadUnit['contValue'])
                            if threadVal==1:
                                threadLoad.relayManualOpen()
                            elif threadVal==0:
                                threadLoad.relayManualClose()
                                break;
        except:
            print("Error getting manualCont values.")
            pass

        #maksimi tuntitehon hakeminen
        try:
            url = 'http://salty-mountain-85076.herokuapp.com/api/phases'
            threadData = urequests.get(url).json()
            for threadUnit in threadData:
                for threadPhase in threadPhases:
                        if threadPhase.getID()==threadUnit['id']:
                            threadVal = int(threadUnit['phaseMax'])
                            maxHour = threadVal
                            break;
        except:
            print("Error getting max hourpower values.")
            pass
        time.sleep(5)

#päälooppi
def main():
    printInfo(loads)
    printInfo(phases)
    print("............\n")
    running = True
    global maxHour
    global maxPower

    #tarkistetaan ohjaukset pilvestä tietyin väliajoin
    _thread.start_new_thread(cloudThread, (loads,phases))

    chrono.start()
    latestMeasTime = 0
    latestPowerTime = 0
    latestManControlTime = 0
    while running:

        #tarkistetaan onko tunti vaihtunut, jos on, nollataan tuntikulutukset
        timeNow = rtc.now()
        year = timeNow[0]
        month = timeNow[1]
        day = timeNow[2]
        hour = timeNow[3]
        minutes = timeNow[4]
        seconds = timeNow[5]
        curTime = [year,month,day,hour]
        if (measTime[0]==curTime[0] and measTime[1]==curTime[1] and measTime[2]==curTime[2] and measTime[3]==curTime[3])==False:
            for load in loads:
                load.setCurHourEne(0)
            for phase in phases:
                phase.setCurHourEne(0)
            setMeasTime(measTime,curTime)

        #lasketaan uusi maksimiteho, ottaen huomioon kulutettu energia (joka viides sekunti)
        if chrono.read()-latestPowerTime>5:
            remainingTime = 3600 - minutes*60 - seconds
            maxPower = (maxHour-getTotalEnergy(phases))/(remainingTime/3600)
            latestPowerTime = chrono.read()

        #tarkistetaan onko kulunut 10s ja lähetetään dataa
        for load in loads:
            curtime = chrono.read()
            if curtime - load.getLast10SecTime() >= 10:
                #keskiarvon lasku
                sum = 0
                for val in load.getLast10Sec():
                    sum += val

                #otetaan huomioon nollatapaus
                if len(load.getLast10Sec())==0:
                    ave = 0
                else:
                    ave = sum/len(load.getLast10Sec())

                #mittaus, tagit id ja nimi, fieldit teho ja energia
                input = 'Measurement,id='+str(load.getID())+',name='+load.getName()+' power='+str(ave)+',totalEne='+str(load.getCurHourEne())
                #print(input)
                #urequests vaatii että data on enkoodattu utf-8:ssa(funktion oletusasetus)
                url = "http://ec2-34-245-7-230.eu-west-1.compute.amazonaws.com:8086/write?db=newtest&u="+secrets[0]+"&p="+secrets[1]

                #print(url)
                #joskus datan lataus epäonnistuu ja ohjelma kaatuu ilman try-exceptiä
                try:
                    urequests.post(url,data=input.encode())
                except:
                    pass

                #tyhjennetään lista ja asetetaan uusi resettausaika
                load.setLast10SecTime(chrono.read())
                load.resetLast10Sec()

        #tarkistetaan onko kulunut 10s ja lähetetään dataa
        for phase in phases:
            curtime = chrono.read()
            if curtime - phase.getLast10SecTime() >= 10:
                #keskiarvon lasku
                sum = 0
                for val in phase.getLast10Sec():
                    sum += val

                #otetaan huomioon nollatapaus
                if len(phase.getLast10Sec())==0:
                    ave = 0
                else:
                    ave = sum/len(phase.getLast10Sec())

                input = 'Measurement,id='+str(phase.getID())+',name='+phase.getName()+' power='+str(ave)+',totalEne='+str(phase.getCurHourEne())
                #print(input)
                #urequests vaatii että data on enkoodattu utf-8:ssa(funktion oletusasetus)
                url = "http://ec2-34-245-7-230.eu-west-1.compute.amazonaws.com:8086/write?db=newtest&u="+secrets[0]+"&p="+secrets[1]
                #print(url)

                #tarvitaan try except mahdollisen kaatumisen estämiseksi
                try:
                    resp = urequests.post(url,data=input.encode())
                    #print(resp.status_code)
                except:
                    pass

                #tyhjennetään lista ja asetetaan uusi resettausaika
                phase.setLast10SecTime(chrono.read())
                phase.resetLast10Sec()

        #käynnistetään mittauslooppi jos aikaa edellisestä mittauksesta on kulunut ainakin 0.5 sekuntia
        if chrono.read() - latestMeasTime >= 0.5:
            pycom.rgbled(0x330000) # red
            latestMeasTime = chrono.read()
            for load in loads:
                if load.isActive():
                    #mitataan virta ja lasketaan kulutus ja lisätään se kuormien omiin arvoihin
                    current = load.getCurrent()
                    power = current * voltage
                    newTime = chrono.read()
                    #wattisekunnit wattitunneiksi
                    energy = power * (newTime - load.getLastTime()) / 3600
                    load.updateLastTime(newTime)
                    load.addCurHourEne(energy,power)

                #kuormien palautus päälle, jälkimmäisessä tunnin puolikkaassa
                #and minutes>=30
                elif load.isActive() == False:
                    #lasketaan kokonaisteho järjestelmässä
                    totalPower = 0
                    for phase in phases:
                        totalPower += phase.getLastPower()

                    loadPower = load.getLastCur() * voltage
                    #tarkistetaan onko nykyinen vaiheteho ja kuorman teho yhdessä tarpeeksi pieni, suljetaan rele jos on
                    if totalPower + loadPower < maxPower * hourThreshold and phases[load.getPhase()-1].getLastCur() + load.getLastTime() < phase.getMaxCur():
                        load.relayAutoClose()

            #tehdään mittaukset ja rajoitukset päävaiheille
            totalEne = 0
            totalPower = 0
            for phase in phases:
                current = phase.getCurrent()
                power = current * voltage
                phase.addLast10Sec(power)
                totalPower += power

                #verrataan virtaa maksimivirtaan ja tehoa maksimitehoon, poistetaan yksi pienimmän prioriteetin kuorma jos ylittyy
                if current >= phase.getMaxCur():
                    for load in phase.returnLoads():
                        if load.isActive():
                            load.relayAutoOpen()
                            break

                #päivitetään nykyisen tunnin kulutus
                phase.updateCurHourEne()
                totalEne += phase.getCurHourEne()
                print("")

            #jos järjestelmän kokonaisteho ylittää maksimitehon, sammutetaan kuormia, järjestetään vaiheet niiden kulutuksen mukaan, laskevasti
            phases.sort(key=lambda phase: phase.getLastPower(),reverse=True)
            if totalPower >= maxPower:
                for phase in phases:
                    for load in phase.returnLoads():
                        if load.isActive():
                            load.relayAutoOpen()
                            break

            #releiden ohjaus muuttujien mukaan
            for load in loads:
                controlVars = load.getControlState()
                print("Name:",load.getName(),"Autocont:",controlVars[0],"Manualcont:",controlVars[1])
                relayPin = load.getRelayPin()
                autoCont = controlVars[0]
                manualCont = controlVars[1]
                control(relayPin,autoCont,manualCont)

            pycom.rgbled(0x000000)
            print("Tehoja:",loads[1].getLast10Sec())
            print("CurEne:",getTotalEnergy(phases))
            print("Max power =",maxPower)
            print("Max tuntiteho =",maxHour)

    printInfo(loads)
    printInfo(phases)

#muuttujien asettaminen ja tietojen lataaminen tiedostosta, ja hard
#koodataan joidenkin muuttujien arvoja

#luodaan timeri ajan mittaamiseen
chrono = Timer.Chrono()

#oletetaan jännitteen pysyvän vakio 230-arvoisena
voltage = 235

#eri sulakkeiden maksimivirrat
phaseMaxCur = 36
loadMaxCur = 10

#tiedostojen nimet
loadFile = "loads.txt"
phaseFile = "phases.txt"
passFile = "pass.txt"

#avataan eri kuormat tiedostosta
loads = []
#kuormien nimet pitää olla ilman ääkkösiä,ei välilyöntejä,
openLoads(loads)

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
timeNow = rtc.now()
year = timeNow[0]
month = timeNow[1]
day = timeNow[2]
hour = timeNow[3]
curTime = [year,month,day,hour]
setMeasTime(measTime,curTime)

#avataan salasanat ja käyttäjät tiedostosta
#tiedosto muotoa:
#username,password,mitä tahansa tekstiä
secrets = openPass(passFile)

#ladataan nykyisen tunnin kulutukset pilvestä
getCloudEnes(loads,rtc,secrets)
getCloudEnes(phases,rtc,secrets)

monthMax = 0
for phase in phases:
    monthMax += getCloudMaxHourPower(secrets,phase)

#maksimi tuntiteho ja tämänhetkisen tunnin kulutus ja raja-arvo
#yksiköt watteina ja wattitunteina
maxHour = 2000
maxPower = maxHour
hourThreshold = 0.95

#käynnistää main loopin vain jos tiedosto itse käynnistetään, eikä sitä
#importata toiseen tiedostoon
if __name__ == '__main__':
    main()

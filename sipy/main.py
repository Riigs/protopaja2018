#importataan classes-filestä kaikki classit useemalla wild cardia
from lib.classes import *
from lib.ohjaus import *
from machine import Timer
from machine import RTC
from network import WLAN
from network import Bluetooth
from time import sleep
from micropython import mem_info
from gc import mem_free
from gc import collect
import _thread
import lib.urequests as urequests

#päälooppi
def main():
    printInfo(loads)
    printInfo(phases)
    print("............\n")
    running = True
    global maxHour
    global maxPower
    global startto
    startto = True
    chrono.start()
    latestMeasTime = 0
    latestPowerTime = 0

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
                    resp = urequests.post(url,data=input.encode())
                    resp.close()
                    #pass
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
                    resp.close()
                    #pass
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

                elif load.isActive() == False:
                    #lasketaan kokonaisteho järjestelmässä
                    load.addCurHourEne(0,0)
                    totalPower = 0
                    for phase in phases:
                        totalPower += phase.getLastPower()

                    loadPower = load.getLastCur() * voltage
                    #tarkistetaan onko nykyinen vaiheteho ja kuorman teho yhdessä tarpeeksi pieni, suljetaan rele jos on
                    if totalPower + loadPower < maxPower * hourThreshold and phases[load.getPhase()-1].getLastCur() + load.getLastCur() < phase.getMaxReturnCur():
                        load.relayAutoClose()

            #tehdään mittaukset ja rajoitukset päävaiheille
            totalEne = 0
            totalPower = 0
            for phase in phases:
                phase.loadPrioritize()
                current = phase.getCurrent()
                power = current * voltage
                phase.setLastPower(power)
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
            totalEnergy = getTotalEnergy(phases)
            infoChara.value("Nykyisen tunnin kokonaiskulutus: "+str(totalEnergy)+"kWh.")
            print("Tehoja:",loads[1].getLast10Sec())
            print("CurEne:",totalEnergy)
            print("Max power =",maxPower)
            print("Max tuntiteho =",maxHour)

    printInfo(loads)
    printInfo(phases)

def openWifiInfo():
    path = "files/wifiInfo.txt"
    wifiData = open(path,'r')
    line = wifiData.readline()
    ssid = line
    line = wifiData.readline()
    password = line
    wifiData.close()
    return [ssid,password]

def saveWifiInfo(ssid,password):
    wifiInf = open("files/wifiInfo.txt", "w+")
    wifiInf.write(ssid)
    wifiInf.write(password)
    wifiInf.close()

#funktioiden määrittely
def openLoads(loads):
    resp = urequests.get('http://salty-mountain-85076.herokuapp.com/api/loads')
    loadData = resp.json()
    for nuload in loadData:
        newLoad = load(nuload['name'],nuload['id'],nuload['commandBits'],nuload['relayPin'],int(nuload['maxCurrent']),int(nuload['phase']),
            int(nuload['priority']))
        loads.append(newLoad)
    return resp

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

def openPhases(phases):
    resp = urequests.get('http://salty-mountain-85076.herokuapp.com/api/phases')
    phasesData = resp.json()
    for phase in phasesData:
        newPhase = mainPhase(phase['name'],phase['id'],phase['commandBits'],int(phase['maxCurrent']))
        phases.append(newPhase)
    return resp

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
            resp.close()

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

#tulostaa 12 kuukauden ajalta suurimman kulutuksen tunnin tiedot ja palauttaa kulutuksen
def getCloudMaxHourPower(secrets,thing):
    ene = 0

    try:
        url = "http://ec2-34-245-7-230.eu-west-1.compute.amazonaws.com:8086/query?db=newtest&u="+secrets[0]+"&p="+secrets[1]+"&pretty=true"
        query = '&q=SELECT+max(totalEne)+FROM+"Measurement"+WHERE+"id"=\''+str(thing.getID())+'\'+AND+time>=now()-365d'

        resp = urequests.get(url+query)
        #print(resp.status_code)
        jsonOut = resp.json()
        resp.close()
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
    global startto
    while True:
        #controllimuuttujien hakeminen
        if startto:
            try:
            #if True:
                url = 'http://salty-mountain-85076.herokuapp.com/api/loads'
                resp = urequests.get(url)
                threadData = resp.json()
                resp.close()
                for threadUnit in threadData:
                    for threadLoad in threadLoads:
                            if threadLoad.getID()==threadUnit['id']:
                                threadVal = int(threadUnit['contValue'])
                                threadPrio = int(threadUnit['priority'])
                                threadLoad.setPriority(threadPrio)
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
                resp = urequests.get(url)
                threadData = resp.json()
                resp.close()
                for threadUnit in threadData:
                    for threadPhase in threadPhases:
                            if threadPhase.getID()==threadUnit['id']:
                                threadVal = int(threadUnit['phaseMax'])
                                maxHour = threadVal
                                break;
            except:
                print("Error getting max hourpower values.")
                pass
            sleep(1)

def sendInfo(chr):
    events = chr.events()
    if events & Bluetooth.CHAR_READ_EVENT:
        print("Lähetetään dataa kännykälle.")

def receiveWifiInfo(chr):
    global ssid
    global password
    global proceed
    global bluetoothTimer
    events = chr.events()
    if events & Bluetooth.CHAR_WRITE_EVENT:
        input = chr.value().decode("utf-8")
        try:
            data = input.split(" ",2)
            print('Type:',data[0])
            print("Data:",' '.join(data[1:]))
            if data[0]=='0':
                ssid = ' '.join(data[1:])
            elif data[0]=='1':
                password = data[1]
            elif data[0]=='2' and data[1]=='ok':
                proceed = True
                bluetoothTimer.reset()
                bluetoothTimer.stop()
            elif data[0]=='33':
                password = ""
            else:
                print("Väärin muotoiltu inputti")
            saveWifiInfo(ssid,password)
            #examp = "0 aalto open"
            #examp2 = "1 salispalis"
            #examp3 = "2 ok"
            #examp4 = "33", ei salasanaa
        except:
            print("Väärin muotoiltu inputti")
            pass



#alkutehtävät käynnistyksessä
bluetooth = Bluetooth()
bluetooth.set_advertisement(name='Kuormanohjausyksikkö', service_uuid=b'1234567890123456')
def conn_cb (bt_o):
    global connected
    events = bt_o.events()   # this method returns the flags and clears the internal registry
    if events & Bluetooth.CLIENT_CONNECTED:
        print("Client connected")
        connected = True
    elif events & Bluetooth.CLIENT_DISCONNECTED:
        print("Client disconnected")
        connected = False

#Create service and characteristic
wifiService = bluetooth.service(uuid='0000000000000000', isprimary=True)
wifiChara = wifiService.characteristic(uuid='0000000000000002', properties=Bluetooth.PROP_BROADCAST | Bluetooth.PROP_WRITE)

infoService = bluetooth.service(uuid='0000000000000001',isprimary=True)
infoChara = infoService.characteristic(uuid='0000000000000003',properties=Bluetooth.PROP_BROADCAST | Bluetooth.PROP_READ,value=0)

bluetooth.callback(trigger=Bluetooth.CLIENT_CONNECTED | Bluetooth.CLIENT_DISCONNECTED, handler=conn_cb)
wifiChara.callback(trigger=Bluetooth.CHAR_WRITE_EVENT, handler=receiveWifiInfo)
infoChara.callback(trigger=Bluetooth.CHAR_READ_EVENT, handler=sendInfo)

connected = False
ssid = "aalto open"
password = ""
proceed = False
[ssid,password]=openWifiInfo()

bluetooth.advertise(True)
bluetoothTimer = Timer.Chrono()
bluetoothTimer.start()

print("Waiting for bluetooth...")

#odottaa uutta bluetooth-yhteyttä enintään 20 sekuntia
while proceed==False:
    if connected==False and bluetoothTimer.read()>=20:
        print("20 seconds passed, waiting stopped, proceeding.")
        proceed=True
    pass

bluetoothTimer.stop()
bluetoothTimer.reset()
del bluetoothTimer

#nettiin yhdistys
wlan = WLAN(mode=WLAN.STA)
nets = wlan.scan()
while not wlan.isconnected():
    for net in nets:
        if net.ssid == ssid:
            print('Network found!')
            if password=="":
                wlan.connect(net.ssid, timeout=5000)
            else:
                wlan.connect(net.ssid, timeout=5000, auth=(WLAN.WPA2, password))
            sleep(5)
            if wlan.isconnected():
                print('WLAN connection succeeded!')
                break
    if not wlan.isconnected():
        print("Trying again for connection.")
        sleep(1)

del ssid,password,proceed

pycom.heartbeat(False)

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
#loadFile = "loads.txt"
#phaseFile = "phases.txt"
passFile = "pass.txt"
#avataan eri kuormat tiedostosta
loads = []
#kuormien nimet pitää olla ilman ääkkösiä,ei välilyöntejä,
resp1 = openLoads(loads)

#avataan tiedot eri vaiheista tiedostosta
phases = []
resp2 = openPhases(phases)
sortLoads(loads,phases)

startto = False
#tarkistetaan ohjaukset pilvestä tietyin väliajoin, käynnistetään startto-muuttujalla myöhemmässä ohjelman vaiheessa
while True:
    try:
        _thread.start_new_thread(cloudThread, (loads,phases))
        break
    except:
        print("Try again")
        print(mem_info())
        print(mem_free())
        pycom.rgbled(0x000000)
        sleep(1)
        pycom.rgbled(0x007f00)

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
del timeNow,year,month,day,hour,curTime
resp1.close()
resp2.close()

#avataan salasanat ja käyttäjät tiedostosta
#tiedosto muotoa:
#username,password,mitä tahansa tekstiä
secrets = openPass(passFile)

#ladataan nykyisen tunnin kulutukset pilvestä
getCloudEnes(loads,rtc,secrets)
getCloudEnes(phases,rtc,secrets)

#maksimi tuntiteho ja tämänhetkisen tunnin kulutus ja raja-arvo
#yksiköt watteina ja wattitunteina
maxHour = 2000
maxPower = maxHour
hourThreshold = 0.95

#käynnistää main loopin vain jos tiedosto itse käynnistetään, eikä sitä
#importata toiseen tiedostoon
if __name__ == '__main__':
    main()

import time
import os

try:
    import pycom
    import machine

    adc = machine.ADC()
    #adc.vref(1166)

    #input voltagen laittaminen p22 pinniin
    #dac = machine.DAC('P21')        # create a DAC object
    #dac.write(0.1)

    #perusjännitteen mittaus
    #from machine import ADC
    #adc = ADC()
    #adc.vref_to_pin('P21')

except ImportError:
    print("Sipy disconnected")
    pass

#Palauttaa jännitteen lukeman
def adc_read(sensorPin):
    try:
        i = 0
        val = 0
        apin = adc.channel(pin=sensorPin)
        for i in range(100):
            val += apin.voltage()
        #jaetaan tuhannella jotta saadaan voltteja mikrovolttien sijaan
        val = val/100/1000
        val = round(val,4)
        #print("Value:",val)
        #print("Voltage:",val)
        current = valToCurrent(val)
        return current
    except:
        print("No reading from pin", sensorPin)
        return 0

def valToCurrent(val):
    #oletusarvona 12-bittinen mittaus
    bits = 12
    #virran, jännitteiden ja saadun arvon välisistä suhteista johdettu kaava
    current = 50.0*val/(1.1)
    return round(current,4)

#Tallentaa lukeman kansioon temp/ID.txt
def adc_save(val, ID):
    filename = str(ID)+".txt"
    #path = os.path.join("temp", filename)
    path = "temp/" + filename
    print(path)
    #f = open(path,'a+')
    #f.write(str(val)+"\n")
    #f.close()
    with open(path, "a+") as f:
        f.write(str(val)+"\n")

def adcFileRead():
    file = open("temp/12345.txt", 'r')
    data = file.read()
    print(data)
    file.close()

def rm(filename):
    os.remove(filename)

def val_to_volt(val):
    max = 4095
    u = (val/max)*1.1
    return round(u,4)

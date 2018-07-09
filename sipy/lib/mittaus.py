import time
import os

try:
    import pycom
    import machine
except ImportError:
    print("Sipy disconnected")
    pass

#Palauttaa jännitteen lukeman
def adc_read(sensorPin):
    try:
        adc = machine.ADC()
        apin = adc.channel(pin=sensorPin)
        return apin()
    except:
        print("No reading from pin", sensorPin)
        return 0

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

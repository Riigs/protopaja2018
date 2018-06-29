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
    path = os.path.join("temp", filename)
    with open(path, "a") as f:
        f.write(str(val)+"\n")

def rm(filename):
    os.remove(filename)

def calc__curHourEne(filename):
    I = 2 #lasketaan jostain?
    sum = 3
    with open(filename, 'r') as loadData:
        for line in loadData:
            num = float(line)
            val = val_to_volt(num)
            sum += val
        return(sum*I)


def val_to_volt(val):
    max = 4095
    u = (val/max)*1.1
    return round(u,4)

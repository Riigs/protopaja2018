#Poista kommentit pycom ja machine kun ajat sipyllä
import pycom
import machine
import time

#Palauttaa jännitteen lukeman
def adc_read(sensorPin):
    try:
        adc = machine.ADC()
        apin = adc.channel(pin=sensorPin)
        return apin()
    except:
        print("Ei lukemaa")
        return 0

#Tallentaa lukeman kansioon ID
def adc_save(val, ID):
    with open(str(ID)+".txt", "a") as f:
        f.write(str(val)+"\n")

def val_to_volt(val):
    max = 4095
    u = (val/max)*1.1
    return u

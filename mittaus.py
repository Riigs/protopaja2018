#Poista kommentit pycom ja machine kun ajat sipyllä
import pycom
import machine 
import time

#lukee jännitettä.
def adc_read(sensorPin):
    adc = machine.ADC()
    apin = adc.channel(pin=sensorPin)
    val = apin()
    time.sleep(2)
    return val

def val_to_volt(val):
    max = 4095
    u = (val/max)*1.1
    return u

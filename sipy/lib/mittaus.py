#Poista kommentit pycom ja machine kun ajat sipyllä
import pycom
import machine #rajoita tilan säästämiseksi?
import time

#lukee jännitettä.
#Kun ajat ohjelmaa Sipyllä, merkkaa "#POIS" merkityt rivit kommenteiksi,
def adc_read(sensorPin):
    #''' #POIS
    adc = machine.ADC()
    apin = adc.channel(pin=sensorPin)
    val = apin()
    time.sleep(2)
    return val
    #''' #POIS
    #time.sleep(2) #POIS
    #return 1  #POIS

def val_to_volt(val):
    max = 4095
    u = (val/max)*1.1
    return u

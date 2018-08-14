import time
import os
from math import *

try:
    import pycom
    from machine import Pin

    #määritellään pinnit spi-kommunikaatiolle
    chipPin = Pin('P12', mode=Pin.OUT)
    mosi = Pin('P11',mode=Pin.OUT)
    miso = Pin('P10',mode=Pin.IN)
    clock = Pin('P9',mode=Pin.OUT)
    #disable device to start with
    chipPin(1)
    mosi(1)
    clock(0)

except ImportError:
    print("Sipy disconnected")
    pass

vref = 5.062

#lukee yhden arvon
def getReading(commandbits,ave):
    adcvalue = 0

    chipPin(0) #Select adc
    # setup bits to be written
    i = 0
    while i < 5:
        mosi(commandbits[i])
        #cycle clock
        clock(1)
        clock(0)
        i+=1

    clock(1)    #ignores 2 null bits
    clock(0)
    clock(1)
    clock(0)

    #read bits from adc
    i = 11
    while i >=0:
        adcvalue += miso()*pow(2,i)
        #cycle clock
        clock(1)
        clock(0)
        i -= 1

    chipPin(1) #turn off device
    if ave==0:
        ave = adcvalue/4095*vref
    else:
        ave = (ave*9+adcvalue/4095*vref)/10
    return ave

#Palauttaa jännitteen lukeman
def adcRead(commandbits,maxCur):
    value = 0
    i = 0
    while i<10:
        value=getReading(commandbits,value)
        i+=1
    current = value/vref * maxCur
    return current

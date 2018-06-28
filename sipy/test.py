#Aja konsolissa: py -m unittest test.py
import unittest

from lib.mittaus import *
from lib.classes import load
from main import *
#Testaa funktiot pääohjelmasta
class TestMain(unittest.TestCase):

    def test_openLoads(self):
        #Testi tähän
        pass

    def test_openPhases(self):
        #Testi tähön
        pass

    def test_openMonthMax(self):
        result=openMonthMax()
        val=(result._maxHourDate__maxHour)
        date=(result._maxHourDate__date)
        self.assertEqual(val, 1000)
        self.assertEqual(date, "1.1.2000")

#Testaa paketin "mittaus" funktiot
class TestMittaus(unittest.TestCase):

    def test_val_to_volt(self):
        result_1 = val_to_volt(4095)
        result_2 = val_to_volt(300)
        result_3 = val_to_volt(2000)
        self.assertEqual(result_1, 1.1)
        self.assertEqual(result_2, 0.0806)
        self.assertEqual(result_3, 0.5372)

    def test_adc_read(self):
        sensorPin='P14'
        result = adc_read(sensorPin)
        self.assertGreaterEqual(result, 0)

    def test_adc_save(self):
        #Testi tähän
        pass

#Testaa luokan "load" metodit
class Testload(unittest.TestCase):
    def setUp(self):
        self.kuorma_1=load(name="Lattialämmitys", ID=12345, sensorPin="P11", relayPin=2, maximumCurrent=10, phase=1, priority=0)
        self.kuorma_2=load("Kiuas",12346,"P12",2,10,1,0)

    def tearDown(self):
        #Testi tähän
        pass

    def test_changeRelayPin(self):
        #Testi tähän
        pass


    def test_resetHour(self):
        #Parempi testi tähän
        result_1 = self.kuorma_1.resetHour()
        result_2 = self.kuorma_2.resetHour()
        self.assertEqual(result_1, 1)
        self.assertEqual(result_2, 1)

    def test_getName(self):
        result_1 = self.kuorma_1.getName()
        result_2 = self.kuorma_2.getName()
        self.assertEqual(result_1, self.kuorma_1._load__name)
        self.assertEqual(result_2, self.kuorma_2._load__name)

    def test_getCons(self):
        #Parempi testi tähän
        result_1 = self.kuorma_1.getCons()
        result_2 = self.kuorma_2.getCons()
        self.assertGreaterEqual(result_1, 0)
        self.assertGreaterEqual(result_2, 0)

    def test_info(self):
        #Testi tähän
        pass

if __name__ == "__main__":
    unittest.main()

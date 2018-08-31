# protopaja2018
Protopaja 2018, Aalto-yliopisto 


Sipy-kansio, jonka sisältö ladataan SiPylle. Files-kansio, jossa on paikallisia tekstitiedostoja(tällä hetkellä tietokannan tunnukset ja yhdistettävän wifin tiedot), sekä vanhoja tekstitiedostoja, joita ei enää käytetä. Lib-kansiossa ovat koodimoduulit classes.py, mittaus.py, ohjaus.py ja urequests.py. Main.py on pääkooditiedosto.


Mittaus.py:
Tässä koodimoduulissa on funktio ja sen apufunktio, jonka avulla AD-muuntimesta luetaan arvoja.

(Rivit 1-23)Tiedoston alussa tuodaan tarvittavia kirjastoja ja määritellään pinnit joilla suoritetaan SPI-kommunikaatiota. Meillä oli ongelmia saada SiPyn oma SPI-kommunikaatio kirjasto toimimaan, joten toteutimme sen itse pinnien avulla.

ChipPin on pinni, joka täytyy sammuttaa ennen kuin AD-muuntimen kanssa aletaan juttelemaan ja aktivoida, kun kommunikointi loppuu.

MOSI on Master-Out-Slave-In-pinni, eli se on mikrokontrollerin ulossyöttö, joka menee AD-muuntimeen. Mikrokontrolleri on siis Master ja AD-muunnin Slave.

MISO on Master-In-Slave-Out-pinni, eli sen avulla AD-muunnin siirtää dataa mikrokontrollerille.

Clock on pinni, joka lähettää AD-muuntimelle kellosignaalin. Aina kun Slave vastaanottaa uuden kellosignaalin, se ottaa vastaan uuden arvon MOSI-pinnistä tai(/ja) lähettää arvon MISO-pinniin.

Lisäksi asetetaan vref-muuttuja, joka on referenssijännite, jonka mittasimme SiPyn virtalähteestä. Mitattuja jännitteitä verrataan tähän.


(Rivit 61-69)Funktio adcRead on pääfunktio, jota kutsutaan pääohjelmasta. Se ottaa kaksi parametria; commandbits ja maxCur.

Commandbits on lista numeroita(nollia ja ykkösiä), jotka vastaavat haluttua AD-muuntimen kanavaa(mikä numerorivi vastaa mitäkin kanavaa voi nähdä AD-muuntimen dokumentaatiosta, AD-muuntimen nimi on MCP3208).

MaxCur kertoo mikä on kyseisen sensorin maksimivirta. Esimerkiksi päävaiheen sensorin alue on 0-50A, eli funktiota pitää vaiheen virtaa mitattaessa kutsua arvolla 50.

Itse funktiossa asetetaan value- ja i-muuttuja nollaan. Value-muuttujaan tallennetaan AD-muuntimen mittaustulos, joka kertoo sensorin ulostulojännitteen. While-loopin avulla otetaan kymmenestä arvosta pseudo-keskiarvo getReading-funktion avulla. Vertaamalla mitattua jännitettä referenssijännitteeseen ja kertomalla maksimivirralla, saamme varsinaisen virran, joka palautetaan.

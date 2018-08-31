# protopaja2018
Protopaja 2018, Aalto-yliopisto 


Koodin rakenne

Sipy-kansio, jonka sisältö ladataan SiPylle. Files-kansio, jossa on paikallisia tekstitiedostoja(tällä hetkellä tietokannan tunnukset ja yhdistettävän wifin tiedot), sekä vanhoja tekstitiedostoja, joita ei enää käytetä. Lib-kansiossa ovat koodimoduulit classes.py, mittaus.py, ohjaus.py ja urequests.py. Main.py on pääkooditiedosto.

Mittaus.py

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

(Rivit 23-59)Funktio getReading varsinaisesti kommunikoi AD-muuntimen kanssa. Se ottaa parametreikseen jälleen commandbits-muuttujan, mutta nyt myös ave-muuttujan. Ave on tähän mennessä laskettu pseudo-keskiarvo tehdyille mittauksille.

Aluksi asetetaan adcvalue-muuttuja nollaan. Tähän muuttujan tallennetaan AD-muuntimen ulostulo. ChipPin lasketaan alas, jotta kommunikaatio voi alkaa. Tämän jälkeen AD-muuntimelle lähetetään commandbits-lista yksi bitti kerrallaan. Tämä toimii joko laskemalla tai nostamalla MOSI-pinni. Tämän jälkeen lähetetään kellosignaali, eli kellopinni nostetaan ja lasketaan. Näin AD-muunnin tietää että sen pitää vastaanottaa yksi bitti. Lopuksi kahden viimeisen bitin, jota ei käytetä, yli hypätään kahdella kellosignaalilla.

Seuraavaksi AD-muunnin lähettää arvoja, jotka luetaan. AD-muunnin lähettää arvoja merkitsevimmästä bitistä(eli suurimman arvon) aloittaen ja se lähettää niitä 12. AD-muuntimen tarkkuus on siis 12-bittinen. Adcvalue-muuttujaan tallennetaan bittien arvot desimaalimuodossa. Bitin arvohan desimaaleina on bitinArvo*2^bitinSijaintiOikealta. Kun yksi arvo on luettu, lähetetään taas kellosignaali, joka kertoo AD-muuntimelle, että olemme valmis vastaanottamaan uuden arvon.

Lopulta lopetamme kommunikoinnin AD-muuntimen kanssa nostamalla ChipPinnin ylös. Sitten laskemme uuden pseudo-keskiarvon käyttämällä annettua arvoa ja mitattua arvoa. Mitattu arvo lasketaan adcvalue muuttujan avulla joka on väliltä 0-4095(2¹²-1, eli AD-muuntimen tarkkuus). Tämä jaetaan maksimiarvolla 4095 ja kerrotaan referenssijännitteellä. Sitten uusi jännite palautetaan.

Ohjaus.py

Tässä tiedostossa on funktioita, joita käytetään releiden ohjaamiseen.

(Rivi 3)Koodin alussa taas tuodaan tarvittavia moduuleja. Funktio control on varsinainen funktio, jota kutsutaan koodin ulkopuolelta ja funktiot relayOn, relayOff, controlRelay ja selControl ovat apufunktiota.

(Rivit 5-15)Funktio relayOn nostaa annetun releen pinnin, aktivoiden releen. Funktio relayOff sammuttaa annetun releen.

(Rivit 17-24)Funktio controlRelay kutsuu edellisiä funktiota annetun contVal-arvon mukaan.

(Rivit 26-34)Funktio selControl ottaa kaksi parametria, autCont ja manCont. AutCont kertoo onko automaattinen ohjaus aktivoinut ja haluaa sulkea tämän kuorman. ManCont kertoo haluaako manuaalinen ohjaus sulkea tämän kuorman.

Näiden avulla päätellään pitääkö rele sulkea, tieto joka palautetaan. Jos molemmat ovat nolla tai yksi, asetetaan arvo vastaavaksi. Jos taas vain toinen on yksi, asetetaan arvoksi silti yksi. Toisin sanoen jos jompikumpi tai molemmat haluavat sammuttaa kuorma, kuorma sammutetaan.

(Rivit 36-40)Funktio control on pääfunktio, jota kutsutaan tiedoston ulkopuolelta. Se ottaa parametreikseen relayPinNumber, eli ohjattavan releen pinnin numeron, autoCont:in, eli automaattisen ohjauksen arvon ja manCont, joka kertoo manuaalisen ohjauksen arvon. Jos nämä ovat nolla, niin rele on pois päältä, eli kuormassa kulkee virta. Jos ne saavat arvon yksi, niin rele aktivoituu ja sulkee kuorman.

Aluksi lopullinen ohjausarvo selvitetään selControl-funktion avulla, jonka jälkeen ohjaus tehdään controlRelay-funktion avulla.

Classes.py

Tässä tiedostossa määritellään luokat, joita pääohjelmassa käytetään. Luokat ovat load ja mainPhase. Tiedoston alussa tuodaan mittaus.py.

Käsitellään aluksi luokkaa load. Load on siis luokka, jonka oliot edustavat järjestelmään kytkettyjä ohjattavia kuormia.

(Rivit 6-43)Funktiota init kutsutaan Pythonissa aina kun initialisoidaan uusi olio luokasta. Sen aikana voidaan määrittää olion muuttujia ja kutsua funktioita. Load-luokalla luodaan ja asetetaan tässä funktiossa useita muuttujia, joista osa on annettu oliota luodessa parametreina.

Nämä parametrit ovat name, ID, commandbits, relayPin, maximumCurrent, phase, priority. Name on kuorman nimi, ID on uniikki numerokirjainyhdistelmä, commandbits kertoo bitit, jotka vastaavat tämän kuorman kanavaa AD-muuntimella, nämä pitää muuttaa numeroiksi alkuperäisestä stringistä; relayPin on kuorman releen pinni mikrokontrollerissa, maximumCurrent kertoo kuorman sulakkeen maksimivirran, phase kertoo missä vaiheessa kuorma on ja priority kertoo kuorman prioriteetin.

Tällä hetkellä maximumCurrent-muuttujaa ei käytetä mihinkään, sitä voitaisiin käyttää yksittäisten kuormien sulakkeiden laukeamisen estämiseen, mutta kuormien automaattinen palauttaminen on ongelma, koska ohjelma tallentaa viimeisimmän virran ja estää kuorman palauttamisen. Yksi tapa ratkaista ongelma olisi antaa ohjelman “kokeilla” kuorman palauttamista jollakin väliajalla. Lisäksi tällaisesta ongelmatilanteesta voitaisiin ilmoittaa kuluttajalle ja/tai operaattorille.

Lisäksi funktiossa määritellään muuttuja nykyisen tunnin kulutukselle, curHourEne, ja muuttujat autoCont ja manualCont, joiden avulla kuormaa ohjataan. Määritellään myös lastCur-muuttuja, johon tallennetaan viimeisin kuorman virta. Muuttujaan lastTime tallennetaan viimeisimmän mittauksen aika. Muuttujaan last10Sec tallennetaan lista, johon tallennetaan mittausten arvoja 10 sekunnin ajalta ja muuttuja last10SecTime kertoo ajan jolloin edellinen lista on viimeksi nollattu.

Olioon kuuluu myös useita funktioita, joiden avulla muuttujien arvoa pystytään muuttamaan, ja joilla niiden arvot pystytään palauttamaan kysyttäessä. Esimerkkinä funktiot updateLastTime ja getLastTime(Rivit 51-55).

(Rivit 63-67)Funktio isActive palauttaa totuusarvon riippuen siitä, onko kuorma ohjattu pois päältä vai onko se vielä aktiivinen. Palauttaa tosi jos on aktiivinen.

(Rivit 83-85)Funktio addCurHourEne lisää nykyisen tunnin kulutukseen parametrina annetun energian ja samalla lisää vastaavan tehon viimeisen 10 sekunnin tehojen listaan.

(Rivit 111-115)Funktio getCurrent kutsuu adcRead-funktiota mittaus.py:stä, tallentaa virran muuttujaan ja palauttaa virran.

(Rivit 133-135)Funktio getControlState palauttaa ohjausmuuttujien arvot tuplena(muuttumaton lista). Näin niiden arvot saadaan tallennettua yhteen muuttujaan. Ensimmäisenä tuplessa on autoCont, sitten manualCont.

(Rivit 138-146)Funktio info tulostaa konsoliin tietoa kuormasta, lähinnä debuggausta varten.

Tiedoston toinen luokka on mainPhase. Se kuvaa siis järjestelmän päävaiheita. Se on hyvin samankaltainen kuin load-luokka, mutta siitä puuttuu osa load-luokasta ja siihen on myös lisätty omia osiaan.

(Rivit 152-181)Funktiossa init alustetaan jälleen muuttujat uudelle oliolle. Parametreilla ja muuttujilla name, ID, commandbits ja maximumCurrent on sama käyttötarkoitus kuin load-oliossa. Lisäksi määritellään raja-arvomuuttujat threshold ja returnThreshold, jotka prosentteina ilmoittavat kuinka lähelle maksimiarvoja saadaan mennä ennen kuin kuormia katkaistaan ja milloin ollaan tarpeeksi kaukana maksimiarvosta, jotta kuormia voidaan palauttaa. Muuttuja lastPower kertoo vaiheen viimeisimmän tehon.

Jälleen luokassa on funktiot muuttujien arvojen vaihtamiselle ja niiden palauttamiselle.

(Rivit 204-205)Funktio loadPrioritize järjestää kuormat prioriteetin mukaiseen järjestykseen, pienimmästä suurimpaan. Tähän käytetään Pythonin sort-funktiota listoille. Annamme sort-funktiolle key-parametrin arvon käyttämällä lambda-avainsanaa. Kutsumme siis listan jokaista alkiota “load”:iksi ja järjestämme ne niiden getPriority-funktion palauttaman arvon mukaan.

(Rivit 210-211)Funktio returnLoads palauttaa tämän vaiheen kaikki kuormat listana.

(Rivit 219-227)Funktiot getMaxCur ja getMaxReturnCur palauttavat vaiheen maksimivirrat, ensimmäinen maksimin, jonka ylittyessä kuormia rajoitetaan ja toinen maksimin, jonka alittuessa kuormia voidaan palauttaa.

(Rivit 246-249)Funktio updateCurHourEne päivittää vaiheen tunnin aikaisen kulutuksen. Tämä tehdään käymällä läpi vaiheen kuormat ja laskemalla niiden kulutukset yhteen.

(Rivit 252-253)Funktio addLoad lisää vaiheen loads-listaan parametrina annetun kuorman.

(Rivit 256-257)Funktio resetHour nollaa tunnin kulutuksen tunnin vaihtuessa.

uRequests.py

Moduuli, jonka avulla mikrokontrollerimme keskustelee tietokantojen avulla. Moduuli on osa MicroPython-projektia GitHub:issa, josta sen pystyy myös lataamaan. Moduuli ei kuitenkaan oletuksena ollut SiPy:ssä.

https://github.com/micropython/micropython-lib/tree/master/urequests

Jouduimme muuttamaan ladattua koodia hieman, koska SiPy:mme MicroPython on ilmeisesti eri versiota kuin lataamamme koodi. Muutimme koodista riviä 53, getaddrinfo toimii eri tavalla ja vaatii vain kaksi parametria meidän koodissamme.

ai = usocket.getaddrinfo(host, port, 0, usocket.SOCK_STREAM) -> ai = usocket.getaddrinfo(host, port)

Main.py

Tässä tiedostossa on ohjelman varsinainen koodi ja lisäksi paljon funktiota. Periaatteessa nämä funktiot olisi voinut siisteyden vuoksi siirtää vielä omaan tiedostoonsa.

Tiedoston alussa tuodaan kaikki tarvittavat moduulit, sekä itse kokoamamme, että valmiit. Heti näiden jälkeen määritellään main-loop, mutta käsitellään se vasta myöhemmin. Käydään aluksi läpi miten ohjelma alkaa.

Alkuvalmistelut

Rivillä 426 alkaa ohjelman suoritus. Aluksi luodaan uusi bluetooth-olio, jolla alamme “mainostamaan” SiPyä bluetoothin kautta nimellä Kuormanohjausyksikkö. Tällöin muut laitteet pystyvät näkemään SiPyn ja yrittää muodostaa yhteyden siihen. Kyseessä ei ole kuitenkaan laitteiden pair:aus; puhelimeen tarvitaan erillinen applikaatio, joka yhdistää SiPyyn.

(Rivit 439-444)Luodaan bluetooth-palvelut ja niille characteristic:sit. Yhdistyneet laitteet pystyvät näkemään nämä palvelut. Se, että ne ovat primaarisia, tarkoittaa, että muut laitteet pystyvät näkemään ne. Sekundaariset palvelut ovat saatavilla vain laitteelle itselleen ja sen palveluille. Characteristic:siin pystytään tallentamaan yksi arvo. Niiden luonnissa pystytään määrittelemään mitä ominaisuuksia niillä on, esimerkiksi wifiChara-characteristic:silla on ominaisuus WRITE, eli characteristic:siin pystytään lähettämään dataa.

(Rivit 446-448)Seuraavaksi määritellään eri characteristic:sien callbackit. Toisin sanoen funktiot, joita kutsutaan kun jotakin tiettyä tapahtuu. Esimerkiksi kun bluetooth-characteristic:sissa tapahtuu joko tapahtuma CLIENT_CONNECTED tai CLIENT_DISCONNECTED, niin kutsutaan funktiota conn_cb. InfoCharan rekisteröidessä arvon lukemisen, kutsutaan sendInfo-funktiota, mutta emme tehneet tätä osaa ohjelmasta loppuun. Jos meillä olisi oma bluetooth-applikaatio puhelimessamme, voisimme lähettää tällä dataa puhelimeen SiPystä.

(Rivit 450-454,457)Connected-muuttuja kertoo onko meillä yhteys johonkin laitteeseen. Proceed-muuttuja kertoo haluammeko siirtyä ohjelmassa eteenpäin, vai odottaa laitteen yhdistämistä. BluetoothTimer on ajastin, joka mittaa kulunutta aikaa. Ssid ja password ovat muuttujia, joihin tallennetaan haluamamme wifi-yhteyden nimi ja salasana. Aluksi avaamme ne paikallisesta tiedostosta openWifiInfo-funktiolla.

(Rivit 456,458)Aloitamme SiPymme “mainostamisen” bluetoothissa ja aloitamme ajastimen ajanlaskun.

(Rivit 462-467)Loopataan, odottaen, että jokin laite yrittäisi ottaa yhteyttä SiPyyn. Mikäli yli kaksikymmentä sekuntia on kulunut, eikä yhteyttä ole luotu, etenee ohjelma.

(Rivit 429-437)Funktio conn_cb aktivoituu kun SiPy huomaa laitteen ottaneen yhteyden tai katkaisseen sen. Connected-muuttujan arvo muutetaan vastaamaan tätä tilannetta, jolloin ohjelma tietää odottaa lisää käskyjä bluetoothin kautta.

(Rivit 391-422)Funktiota receiveWifiInfo kutsutaan kun dataa vastaanotetaan puhelimesta Bluetoothin kautta. Globaalit muuttujat ssid, password, proceed ja bluetoothTimer julistetaan funktion aluksi. Muuttujiin ssid ja password tallennetaan vastaanotettu SSID ja salasana. Parametrina saadaan jonkin bluetooth-palvelun characteristic, josta saamme bluetooth-tapahtumat events()-funktiolla. Jos events-muuttuja ei ole tyhjä ja on tapahtunut bluetooth-kirjoitustapahtuma(SiPyä kohti) edetään koodissa.

Ohjelma pystyy vastaanottamaan neljä eri komentoa: “0 —”, joka vaihtaa ssid-muuttujan arvon kolmen viivan kohdalla olevaksi merkkijonoksi; “1 —”, joka vaihtaa password-muuttujan arvon; “2 ok”, joka kertoo ohjelmalle, että sen pitää lopettaa komentojen odottaminen bluetoothissa ja edetä suorituksessaan; sekä “33”, joka kertoo ohjelmalle, että halutulla SSID:llä ei ole salasanaa.

Aluksi syöttö muutetaan merkkijonoksi ottamalla aluksi characteristic:in arvo value-funktiolla ja sitten dekoodaamalla saatu tulos decode-funktiolla, syötteenä utf-8. Tämän jälkeen syöte jaetaan listaan osiin välilyöntien mukaan. Näitä arvoja verrataan olemassa oleviin komentoihin ja mikäli ne vastaavat, suoritetaan koodia. Kahdessa ensimmäisessä tapauksessa merkkijonot vain kopioidaan muuttujiin. Jos syöte on “2 ok”, proceed-muuttujan arvoksi asetetaan True, jotta ohjelma etenisi ja bluetoothTimer resetoidaan ja pysäytetään. Jos syöte on “33”, niin muuttujaan password tallennetaan tyhjä merkkijono.

Lopuksi ohjelma tallentaa uudet(tai vanhat) arvot paikallisesti saveWifiInfo-funktion avulla.

(Rivit 469-471)Seuraavaksi bluetoothTimer pysäytetään ja poistetaan muistin säästämiseksi.

(Rivit 473-490)Nyt kun tiedämme mihin wifiin haluamme yhdistää, otetaan yhteys siihen. Luodaan uusi wlan-olio, jonka asetuksena on STA, eli station, eli asema. Nets-listaan haetaan kaikki wlan:it, jotka SiPy löytää.

Seuraavaksi käymme niitä läpi ja tutkimme onko joku niistä samanniminen kuin haluamamme verkko. Mikäli on, yritetään yhdistystä connect-funktiolla, joko salasanalla tai ilman. Odotetaan kunnes yhteys onnistuu, tai kuluu 5 sekuntia, jonka jälkeen yritetään uudestaan. Jos yhteys onnistuu pystyy koodi taas etenemään. Rivillä 494 sammutetaan SiPyn automaattinen ledin vilkutus, koska käytämme lediä myöhemmin koodin etenemisen visualisoimiseen.

Rivillä 500 luodaan ajastin, jota käytetään mittausten välisen ajan mittaamiseen. Se pyörii jatkuvasti ja nykyistä arvoa verrataan edelliseen. Lisäksi asetamme voltage-muuttujan arvoksi 235. Oletamme siis, että jännite pysyy vakiona, vaikka se voikin todellisuudessa vaihdella.

(Rivit 509-521)Seuraavaksi määritellään tiedosto, jossa on tiedot pilven tietokannan käyttäjätunnuksista ja salasanoista. Lisäksi määritellään listat kuormille ja vaiheille, johon ne tallennetaan openLoads- ja openPhases-funktioiden avulla. Lopuksi kuormat lajitellaan oikeisiin vaiheisiin sortLoads-funktion avulla.

(Rivit 523-535)Nyt voimme luoda ohjausmuuttujien tarkistusta varten oman threadin pääohjelman rinnalle. Asetetaan startto-muuttuja epätodeksi, jottei threadi ala tekemään vielä mitään. Aktivoimme sen myöhemmin. Threadin luominen vie paljon muistia ja se ei aina onnistu. Tällöin SiPy yrittää uudelleen ja vilkuttaa vihreää valoa.

Muistia voi olla liian vähän, mutta meidän projektissamme ainakin ongelmana oli että se oli liian hajanaista. Threadi vaatii pitkän pätkän vapaata muistia, mutta ohjelmassamme oli yksittäisiä arvoja pitkien tyhjien alueiden välissä, jotka estivät threadin luomisen. Siirsimme siksi threadin luomisen aikaisempaan osaan ohjelmaa, jossa muuttujia ei ole määritelty vielä yhtä paljon. Luonti ei silti onnistu aina, joten sen voisi siirtää aivan ohjelman alkuun, tosin silloin pitäisi threadin käyttämät parametrit ja globaalit muuttujatkin määritellä ainakin alustavasti aikaisemmin ohjelman osassa.

(Rivit 537-543)Seuraavaksi initialisoimme SiPylle RTC:n (real-time clock), jonka avulla pystymme seuraamaan kuluvaa aikaa. Synkronoimme kellon vastaamaan nykyistä aikaa erään ntp-serverin avulla. Kun tämä on tehty, lopetamme yhteyden.

(Rivit 545-556)Seuraavaksi määrittelemme muuttujiin mitä tuntia mittaamme juuri tällä hetkellä. Käytämme tähän vuotta, kuukautta, päivää ja tuntia. Kun SiPy huomaa RTC:n tunnin olevan eri kuin nykyinen mitattava tunti, tietää se tunnin vaihtuneen. Lopuksi suljemme openLoads- ja openPhases-funktioiden palauttamat socketit, muistin vapauttamiseksi.

(Rivi 561)Avaamme openPass-funktiolla tiedostosta InfluxDB-tietokannan käyttäjätunnuksen ja salasanan.

(Rivit 563-565)Seuraavaksi haemme mahdolliset nykyisen kuluvan tunnin kulutukset pilven tietokannasta getCloudEnes-funktion avulla. Toisin sanoen jos SiPy sammuu kesken tunnin, kulutukset eivät resetoidu nollaan.

(Rivit 567-571)Määritellään tunnin aikana kulutettava maksimienergia wattitunteina ja siihen liittyvä maksimiteho. Näiden muuttujien arvot tulevat muuttumaan ohjelman aikana. Lisäksi määritellään hourThreshold-muuttuja, jonka avulla voidaan rajoittaa millä raja-arvolla maksimitehosta kuormia voidaan kytkeä takaisin päälle.

(Rivit 573-576)Lopuksi käynnistämme pääloopin. Tarkistamme, että tiedosto joka pyörittää koodia nyt on varmasti main-niminen, sen varalta että päälooppia ei käynnistetä jos tämä tiedosto tuotaisiin osaksi jotakin toista koodia, jolla on oma päälooppinsa.

Apufunktiot

(Rivit 199-213)Funktio openWifiInfo nimensä mukaisesti avaa tiedot paikallisesti tallennetusta wifi-yhteydestä. SiPy käyttää tätä yhteyttä oletuksena, jos se ei vastaanota uutta yhteyttä. SSID ja salasana luetaan files-kansion wifiInfo-tekstitiedostosta, jossa molemmat on tallennettu omalle rivilleen. Lopuksi arvot palautetaan.

(Rivit 209-213)Funktio saveWifiInfo tallentaa parametreina saadut SSID:n ja salasanan samaan tekstitiedostoon wifiInfo.txt. Molemmat tallennetaan omalle rivilleen, helpompaa lukua varten.

(Rivit 215-223)Funktio openLoads lataa palvelimen tietokannasta järjestelmän kuormien tiedot, luo niiden avulla uudet kuorma-oliot ja tallentaa ne osaksi loads-listaa. Aluksi haetaan data urequests-moduulin get-komennolla halutusta osoitteesta.

LoadData-muuttujaan tallennetaan JSON versio ladatusta datasta. Datan täytyy olla muotoiltu niin, että tämä JSON on lista eri kuormista, jotka ovat Python-sanakirjoja. Listan läpi voidaan käydä ja sanakirjasta voidaan hakea arvot käyttämällä avaimia, kuten “name” tai “id”.

Lopuksi palautetaan vastaus itse, jotta socketin viemä muisti voidaan palauttaa halutussa kohdassa koodia.

(Rivit 239-245)Funktio openPhases tekee saman kuin openLoads, mutta vaiheille.

(Rivit 225-237)Funktio sortLoads lisää kaikki järjestelmän kuormat niiden vastaavien vaiheiden listoihin addLoad-funktiota käyttäen. Lopuksi kuormat asetetaan vaiheiden listoissa prioriteettijärjestykseen.

(Rivit 247-254)Funktio openPass avaa files-kansiosta parametrina annetun tiedoston. Tässä tiedostossa on samalla rivillä, pilkulla erotettuna käytettävän InfluxDB-tietokannan käyttäjänimi ja salasana. Nämä palautetaan listana käyttöä varten.

(Rivit 256-260)Funktio setMeasTime on apufunktio, joka asettaa ensimmäisenä parametrina annetun listan alkiot vastaamaan toisena parametrina annetun listan alkioita.

(Rivit 262-267)Funktio parseStringToTime tulkitsee InfluxDB-tietokannan aikaleima-merkkijonon numeroiksi ja palauttaa ne listana.

(Rivit 270-302)Funktiota getCloudEnes kutsutaan vain kerran käynnistyksessä. Se lataa InfluxDB-tietokannasta tämänhetkisen tunnin kulutukset eri kuormille ja vaiheille, mikäli SiPy sammuu kesken tunnin. Aluksi määritellään url, josta tietokanta löytyy, johon myös sisällytetään esimerkiksi tietokannan käyttäjätunnus ja salasana InfluxDB:n url-enkoodauksen mukaan. Pretty-arvo määrittää palauttaako tietokanta tiedon “nätisti” muotoiltuna, mitä haluamme, eli asetamme arvoksi true.

Seuraavaksi käymme listan kuormia/vaiheita läpi yksi kerrallaan. Aluksi tarkistamme nykyisen ajan SiPyn RTC:stä (real-time clock). Vertaamme sitä myöhemmin haettuun dataan. Queryn arvoa merkitään q:lla. Kerromme InfluxDB:lle, että haluamme viimeisimmän kulutetun energian mittauksen (last(totalEne)) tiedot getID:n palauttamasta ID:stä.

Seuraavaksi lähetetään get-pyyntö tietokannalle ja jälleen muutetaan vastaanotettu data JSON-muotoon. Luetaan datan aikaleima ajaksi, jota vertaamme nykyiseen aikaan. Jos niiden vuodet, kuukaudet, päivät ja tunnit täsmäävät, on edellisessä mittauksessa kyseessä sama tunti kuin nyt on meneillään. Tällöin luetaan vastauksesta energian arvo ja asetetaan se. Lisäksi päivitetään nykyinen mittausaika.

Jos arvot eivät täsmää, mitään ei tehdä.

(Rivit 304-327)Funktio getCloudMaxHourPower hakee InfluxDB-tietokannasta viimeisimmän 12 kuukauden ajalta suurimman tuntitehon. Funktio tulostaa sen ja palauttaa myös sen arvon. Tällä hetkellä funktiota ei käytetä ohjelmassa mihinkään.

Jälleen get-komennolle annetaan tietokannan osoite, tiedot ja query yhtenä merkkijonona. Nyt käytetään InfluxDB:n query languagen max-käskyä hakemaan suurin arvo, kuitenkin, että päiviä on enintään 365 nykyisestä taaksepäin. Data muutetaan taas JSON-muotoon ja energia luetaan siitä. JSON-muodossa datassa on sisäkkäin sekä sanakirjoja ja listoja ja siksi rivi (ene = jsonOut[“results”][0][“series”][0][“values”][0][1]) näyttää hieman epäselvältä. Otetaan myös kyseisen kulutuksen ajankohta ja lopuksi tulostetaan molemmat. Funktion päätteeksi palautetaan kulutuksen arvo.

(Rivit 329-334)Debuggaus funktio printInfo, joka tulosti kuormien ja vaiheiden infoja.

(Rivit 336-340)Funktio getTotalEnergy palauttaa koko järjestelmän kuluttaman energian. Tämä lasketaan parametrina annettujen vaihelistan vaiheiden kuluttamista energioista.

(Rivit 342-384)Funktio cloudThread vastaa ohjausmuuttujien arvojen päivittämisestä palvelimelta. Sitä pyöritetään rinnakkain muun ohjelman kanssa omassa threadissaan. Sitä ei kuitenkaan käynnistetä ennen kuin internet-yhteys on luotu ja muut valmistelut tehty. Tätä varten tarkistetaan startto-muuttujan arvoa, joka päivitetään true:ksi kun kaikki on valmista threadin koodin käynnistämiselle. Parametreina annetaan threadLoads, joka on siis vain aikaisemmin määritelty lista kuormista ja threadPhases, joka on lista vaiheista. Globaalien muuttujien(maxHour, startto) arvot pystyvät muuttumaan funktion ulkopuolella ja funktio saa niiden arvot heti käsiinsä ja pystyy myös itse globaalisti muuttamaan niitä.

Jälleen määritellään url-muuttujaan osoite, josta pystymme get:taamaan tarvittavat tiedot. Saatu data muutetaan jälleen JSON-muotoon ja käydään läpi. Datassa ovat kaikki kuormat ja niiden tiedot. Verrataan näiden kuormien ID:eitä paikalliseen listaan ja jos täsmäys löytyy, niin otetaan kyseisen datakuorman ohjausarvo ja prioriteetti talteen, sekä asetetaan paikallisen kuorman arvot vastaaviksi.

Seuraavaksi haetaan maksimituntiteho. Määritellään jälleen url ja muutetaan data JSON:iksi. Jälleen verrataan ID:eitä ja asetetaan globaali maxHour-muuttuja datan mukaiseksi, mikäli ID:t vastaavat. Tässä versiossa ohjelmaa maksimituntiteho on tallennettu samaan tietokantaan kuin yksittäiset vaiheet, vaikka oikeasti se onkin koko järjestelmän ominaisuus.

(Rivit 386-389)Funktiota sendInfo kutsuttaisiin, kun SiPy lähettäisi dataa Bluetoothin kautta. Emme kuitenkaan lopulta tehneet tätä toiminnallisuutta.

Main()

Käydään seuraavaksi läpi itse pääfunktio. Jälkikäteen ajateltuna useita kohtia pääfunktiosta olisi voinut toteuttaa omina funktioinaan, jotka olisivat tehneet pääfunktiosta helpommin luettavan ja lyhyemmän.

(Rivit 15-28)Vielä pääfunktion alkuvalmisteluja, jotka eivät kuulu itse päälooppiin. Aluksi tulostetaan debuggausmielessä tiedot kuormista ja vaiheista. Asetetaan running-muuttuja todeksi. Se vastaa pääloopin toistumisesta, tässä versiossa ohjelmaa sitä ei aseteta missään vaiheessa False:ksi. Haetaan globaalit muuttujat maxHour, maxPower ja startto pääfunktion käyttöön. Asetetaan startto True:ksi, jotta aikaisemmin aloittamamme threadi käynnistää varsinaisen toimintansa.

Käynnistämme myös chrono-ajastimen ajanlaskun ja asetamme kaksi aikamuuttujaa, latestMeasTime, johon tallennetaan ajastimen aika viimeisestä mittauksesta; ja latestPowerTime, joka kertoo milloin uusin maksimiteho on laskettu.

Seuraavaksi alkaa päälooppi, jota toistetaan jatkuvasti. Se alkaa riviltä 29 ja jatkuu riville 194.

(Rivit 31-45)Loopin alussa tarkistetaan onko tunti vaihtunut. Tämä tehdään vertaamalla RTC:stä saatuja arvoja measTime-listan arvoihin. Tallennamme myös myös minuutit ja sekunnit muuttujiin minutes ja seconds myöhempää käyttöä varten. Mikäli tunti on vaihtunut, nollataan kuormien ja vaiheiden tuntikulutukset ja asetetaan measTime:n arvot vastaamaan nykyistä tuntia.

(Rivit 47-51)Seuraavaksi lasketaan uusi maksimiteho, jota ohjattu järjestelmä pystyy keskimäärin käyttämään ylittämättä suurinta sallittua tunnin kulutusta. Tämä tehdään viiden sekunnin välein tässä versiossa ohjelmaa. Aluksi laskemme tunnin jäljellä olevan ajan käyttämällä RTC:stä saamiamme minuutteja ja sekunteja.

Jäljellä oleva aika sekunneissa on tunnin sekunnit 3600 – minuutit*60 – sekunnit. Suurin sallittu keskimääräinen teho on jäljellä oleva energia, joka saadaan tunnin maksimista ja tämänhetkisestä kokonaiskulutuksesta, jaettuna jäljellä olevana aikana(muutettuna tunneiksi, koska maksimienergia on annettu wattitunneissa). Lopuksi asetetaan aika siitä, milloin tämä on viimeksi tehty.

(Rivit 53-85) Seuraavassa osassa koodia tarkastetaan kuormista milloin niistä on viimeksi lähetetty kulutustietoja tietokantaan. Mikäli 10 sekuntia on kulunut, lasketaan aluksi keskiarvo tälle ajalle. Tähän käytetään funktiota getLast10Sec, joka palauttaa listan kuorman viimeisistä 10 sekunnin mittauksista. Jos jostain syystä listan pituus on nolla, asetetaan keskiarvoksi nolla, jotta vältetään nollalla jakaminen.

Määritämme input-muuttujaan mitä haluamme lähettää tietokantaan. Kyseessä on merkkijono. Siinä näkyy myös tietokannan rakenne. Ensimmäisenä on määritelty mittauksen nimi “Measurement” ja pilkku, jonka jälkeen määritellään tagit, joilla InfluxDB:ssä määritellään tiedot mittauksesta, kuten ID ja nimi. Tagien jälkeen syötteessä pitää olla välilyönti, jonka jälkeen määritellään varsinaiset field:it ja arvot. Meillä on kaksi field:iä, power ja totalEne, joille annetaan arvot kuorman tehon ja kulutuksen mukaan.

Määrittelemme myös url-muuttujaan jälleen tietokannaosoitteen ja kirjautumistiedot. Toisin kuin aikaisemmin, käytämme nyt write api end point:ia, emmekä query:a. Tämä siksi, että lähetämme nyt dataa InfluxDB:hen.

Seuraavaksi lähetämme datan post-requestin avulla, datana input-muuttuja, joka on vielä enkoodattu utf-8-muotoon(encode-funktion oletusarvo).

Lopuksi tyhjennämme kymmenen sekunnin kulutuksen listan kuormalta ja asetamme nykyisen ajan siksi, milloin lähetys on viimeksi suoritettu.

(Rivit 87-118)Tehdään sama asia kuin äsken, mutta nyt vaiheille. Koska syötteet ovat täysin samanmuotoiset, tätä varten olisi voitu luoda yksi funktio, johon annetaan parametrina joko kuormat tai vaiheet.

(Rivit 120-186)Seuraava pitkä osa koodia on tarkoitettu mittausten ja rajoitusten tekemiselle. Tämä suoritetaan puolen sekunnin välein ja huomioon otetaan itse mittauksissa ja ohjauksissa kulunut aika.

Valitsimme alunperin puolen sekunnin väliajan, koska SiPy:n oman AD-muuntimen epätarkkuuden johdosta jouduimme ottamaan erittäin paljon mittaustuloksia vakaan keskiarvon saamiseksi, joka hidasti ohjelmaa. Ulkoinen AD-muunnin ei kuitenkaan vaadi tätä, joten tätä aikaa voisi todennäköisesti pienentää helpostikin. Mittausten alussa SiPyn ledi asetetaan punaiseksi, jotta tiedetään että mittaus on käynnissä. Kun mittaus on tehty, ledi sammutetaan.

(Rivit 124-145)Nyt käydään kuormat yksi kerrallaan läpi. Jos kuorma on aktiivinen, eli virrankulkua siihen ei ole estetty, tehdään mittaus sen getCurrent-funktiolla. Seuraavaksi laskemme tehon vakioksi asettamallamme ja olettamallamme voltage-muuttujan avulla. Tehohan on virta kertaa jännite.

Seuraavaksi laskemme kulutetun energian. Tämä tehdään kertomalla teho kuluneella ajalla viime mittauksesta, jonka saamme erotuksena viime mittauksen ajasta(funktio getLastTime) ja nykyisestä ajasta, newTime-muuttuja. Oletamme, että teho on pysynyt vakiona tuon ajan. Lisäksi muutamme energian wattitunneiksi, koska se on energialle käyttämämme yksikkö.

Lopuksi päivitämme kuormaan tiedon tämän mittauksen ajasta ja kutsumme funktiota addCurHourEne, joka sekä lisää kuorman nykyiseen kulutukseen mitatun energian, mutta myös lisää mitatun tehon kuorman teholistaan.

Jos kuorma ei ole aktiivinen, merkitään sen teholistaan nollia ja seuraavaksi tarkistetaan mikä on kokonaisteho järjestelmässä. Tämä tiedetään laskemalla yhteen vaiheiden tehot, jotka saadaan funktiolla getLastPower. Voimme myös laskea katkaistun kuorman ennustetun kulutuksen, mikäli se kytkettäisiin takaisin päälle. Tämä saadaan kertomalla viimeinen mitattu virta(getLastCur) jännitteellä.

Mikäli kokonaisteho ja kuorman teho yhdessä alittavat suurimman sallitun tehon, voidaan kuorma kytkeä takaisin tehonrajoituksen puolesta. Täytyy myös tarkistaa, ettei vaiheen virta ylitä sallittua rajaa, joka tehdään vertaamalla vaiheen ja kuorman virtojen summaa maksimivirtaan.

Mikäli molemmat arvot alittuvat, voidaan kuorma automaattiohjauksen puolesta kytkeä takaisin päälle. Tämä tehdään kuorman funktiolla relayAutoClose.

(Rivit 147-168)Seuraavassa osassa koodia teemme mittaukset päävaiheille ja tarkistamme samalla, että niissä ei kulje liian suurta virtaa verrattuna niiden sulakkeisiin. Aluksi asetamme totalEne- ja totalPower-muuttujat nolliksi, joihin tulemme laskemaan vaiheiden arvojen summat. Näitä käytetään myöhemmin.

Käymme vaiheet yksitellen läpi ja asetamme kuormat prioriteettijärjestykseen, sen varalta että nämä olisivat vaihtuneet palvelimella. Otamme vaiheesta virran getCurrent-funktiolla ja jälleen laskemme tehot ja energiat, kuten kuormien yhteydessä. Lisäämme vaiheolioon kulutetun energian ja viimeisimmän tehon, sekä uuden tehon 10 sekunnin listaan. Lisäksi lisäämme totalEne- ja totalPower-muuttujiin vaiheen mittaustiedot.

Vertaamme myös vaiheesta mitattua virtaa sen sallittuun maksimivirtaan, joka saadaan funktiosta getMaxCur. Jos virta ylittyy, pudotamme yhden pienimmän prioriteetin kuorman, joka on aktiivinen. Tähän voitaisiin lisätä älyä sillä, että verrattaisiin virran ylitystä kuorman virtaan ja tällä löydettäisiin optimaalinen kuorma pudotukselle, mutta tämä myös hieman lisäisi kohdassa kuluvaa aikaa, varsinkin mitä enemmän kuormia olisi.

(Rivit 170-177)Seuraavaksi järjestämme vaiheet niiden listassa tehon mukaan, suurin teho ensimmäiseksi. Käytämme taas sort-funktiota, jonka key-parametrina käytämme lambda-avainsanaa ja funktiota getLastPower. Reverse-parametri kääntää listan suurimmasta pienimpään. Jos kokonaisteho on suurempaa kuin määritelty maksimi, pudotetaan vaiheista kuormia prioriteettijärjestyksessä. Vaiheet kuitenkin käydään läpi niiden tehojen mukaan, mikä on hyvä ottaa huomioon.

(Rivit 179-186)Aikaisemmin, kun on puhuttu releiden ohjauksesta, on varsinaisesti tarkoitettu vain ohjausmuuttujien asettamista. Nyt näitä kuormien ohjausmuuttujia käytetään ohjaamaan kuormien releitä. Käydään kuormat taas yksitellen läpi.

Otetaan ohjausmuuttujat getControlState-funktiolla, joka palauttaa ne kahden arvon tuplena(muuttumaton lista). Tallennetaan niiden arvot muuttujiin autoCont ja manualCont ja tallennetaan myös kuorman releen pinni muuttujaan relayPin. Lopuksi kutsutaan control-funktiota, joka suorittaa releiden ohjauksen sille annettujen parametrien mukaan.

(Rivit 188-194)Lopuksi sammutamme ledin, näyttääksemme että mittaus ja ohjaus on loppunut ja tulostamme muutamia arvoja debuggaustarkoituksessa. Lisäksi päivitämme erään bluetooth-characteristic:sin arvon, vastaamaan merkkijonoa, joka kertoo nykyisen tunnin kokonaiskulutuksen.

Näin pitkän merkkijonon lähettäminen ei kuitenkaan toiminut oikein, joten jätimme tämän ominaisuuden kehittämisen kesken. Ilmeisesti lähetettävän tiedon pituutta pystyy kuitenkin muuttamaan characteristic:sista. Lisäksi todellisessa tapauksessa lähetettäisiin todennäköisesti pelkkä numeerinen arvo. Kuitenkin, characteristic:sien arvoja vaihtamalla on mahdollista lähettää tietoa bluetoothin kautta älypuhelimelle tai muille laitteille.

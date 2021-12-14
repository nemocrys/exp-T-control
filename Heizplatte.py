''' Notizen:
Bedienungsanleitung: https://www.ika.com/de/Produkte-Lab-Eq/Magnetruehrer-Heizruehrer-Laborruehrer-Ruehrer-csp-188/C-MAG-HS-7-control-Downloads-cpdl-20002694/

Sicherheitstemperatur einstellen:
    - links neben dem Ein-Aus-Schalter
    - Benötigt wird ein Schraubenzieher (oder ähnliches)
    - Bereich:  100 °C ... 650 °C
        -> Solltemperatur hat bei bestimmten Sicherheitstemperaturen eine maximale Größe (z.B. bei 100 °C lässt das Gerät nur 50 °C zu egal was man dem Gerät sendet!!)
        -> Siehe dafür auf das Display des Gerätes, was maximal möglich ist!!

Regler einstellen:
    - Vor starten des Programms !!
    - auf das Symbol mit dem Schraubenschlüssel drücken
        -> dann den rechten Drehknopf drehen bis der PID oder 2P auf dem Hardware Bildschirm blickt
        -> Drehknopf zur Bestätigung einmal drücken
        -> wenn die Anzeige blinkt, Drehknopf drehen bis der gewünschte Regler auf dem Display erscheint
        -> Zur Eingabe erneut den Drehknopf drücken und as Symbol mit dem Schraubenschlüssel zum Verlassen drücken

Vorhandene Funktionen:
    Werte Erfragen:
    - Gerätenamen                       -->     IN_NAME\r\n
    - Isttemperatur (Externer Fühler)   -->     IN_PV_1\r\n 
    - Isttemperatur (Heizplatte)        -->     IN_PV_2\r\n
    - Solltemperatur                    -->     IN_SP_1\r\n 
    - Sicherheitstemperatur             -->     IN_SP_3\r\n

    Werte Übergeben:
    - Solltemperatur                    -->     OUT_SP_1 x\r\n                      Intiger --> Bereich: x = 0 ... 500 °C       (Eingabe ohne Einheit)
    - Stoppe die Heizung                -->     STOP_1\r\n
    - Starte die Heizung                -->     START_1\r\n

    ############################################################################################################################################################################
    Weitere mögliche Funktionen der Heizplatte - hier erstmal nicht gebrauchte - Nicht im Programm:
    Erfragen:
    - Drehzahl Istwert                  -->     IN_PV_4\r\n
    - Viskositätstrend                  -->     IN_PV_5\r\n
    - Drehzahl Sollwert                 -->     IN_SP_4\r\n

    Werte Übergeben:
    - Drehzahl Sollwert                 -->     OUT_SP_4 x\r\n                      Intiger --> Bereich: x = 0 ... 1500 rpm     (Eingabe ohne Einheit)
    - Start Motor                       -->     START_4\r\n
    - Stoppe motor                      -->     STOP_4\r\n
    - Normalbetrieb umschalten          -->     RESET\r\n
    - Betriebsart einstellen            -->     SET_MODE_n\r\n                      n = A, B or D   --> Siehe Betriebsanleitung um zu sehen was es bedeutet!
    ############################################################################################################################################################################ 
'''

# Bibliotheken:
import serial
import random

# Variablen:
global ser_py, debug_heizplat, test_heizplat

# Funktionen:
###########################################################################
def Init_Heizplatte(com, rate, bits, stop, parity, dbg, test):            # Initialisiert die Heizplatte, z.B. wird der Steckplatz hinzugeordnet
###########################################################################
    global ser_py, debug_heizplat, test_heizplat

    debug_heizplat = dbg
    test_heizplat = test
    
    portName = com                                                        # 'COM'+str(com)
    try:
        serial.Serial(port=portName)
    except serial.SerialException:
        print ('Port ' + portName + ' not present')
        if not test_heizplat:
            quit()                              # Sollte kein Test laufen und keine COM Stelle angesprochen werden, so wird das Programm unterbrochen
    
    if test_heizplat == False:                  # identisch mit --> if not test_heizplat:   
        ser_py = serial.Serial(
            port = portName,
            baudrate = int(rate),
            parity = parity,
            stopbits = int(stop),
            bytesize = int(bits),
            timeout = 2.0)
        print('Heizplatte Initialiesiert!')
        print(f'Heizplatte: {get_Name()} bereit!')       
        if debug_heizplat == True:
            print(repr(ser_py) )	            # Für Debug
    else:
        print('Ein Test läuft gerade!')         # sagt das man im Test-Modus ist!

###########################################################################
def get_Name():                                                           # Befehl zur Namens Ausgabe der Heizplatte übergeben (Erfragt den Namen)
###########################################################################
    if test_heizplat == False:
            if debug_heizplat:
                print ('Sending to ' + ser_py.port + ' den Befehl IN_NAME\\r\\n')
            ser_py.write(('IN_NAME' +'\r\n').encode())                    # Sendet Befehl an Heizplatte, \r\n == CR LF
    name = Read_Ausgabe()
    
    #if debug_heizplat == True:
    #    print(repr(name))       # Für Debug
    return name

###########################################################################
def get_TempPt1000():                                                     # Befehl zur Temperatur Ausgabe des Temperaturfühlers übergeben (Erfragt die Temperatur des externen Messfühlers)
###########################################################################
    if test_heizplat == False:
        if debug_heizplat:
            print ('Sending to ' + ser_py.port + ' den Befehl IN_PV_1\\r\\n')
        ser_py.write(('IN_PV_1' +'\r\n').encode())
        tempF = Read_Ausgabe().split(' ')[0]
        if tempF == '':                                          # wenn ein leerer String kommt, so wird er übergeben, aber im Hauptprogramm dann aussortiert (ich mache das so, damit die Funktion etwas zurückgibt in dem Fall)
            return tempF
    else:
        tempF = random.uniform(0,100)                            # im Test Modus wird eine Zufällige zahl übergeben
    return float(tempF)                                          # gibt nur die Temperatur aus, egal wie lang die zahl wird

###########################################################################
def get_TempHeizplat():                                                   # Befehl zur Temperatur Ausgabe der Heizplatte übergeben (Erfragt Temperatur der Heizplatte)
###########################################################################
    if test_heizplat == False:
        if debug_heizplat:
            print ('Sending to ' + ser_py.port + ' den Befehl IN_PV_2\\r\\n')
        ser_py.write(('IN_PV_2' +'\r\n').encode())
        tempP = Read_Ausgabe().split(' ')[0]
        if tempP == '':                                                   # wenn ein leerer String kommt, so wird er übergeben, aber im Hauptprogramm dann aussortiert (ich mache das so, damit die Funktion etwas zurückgibt in dem Fall)
            return tempP
    else:
        tempP = random.uniform(0,100)                                     # im Test Modus wird eine Zufällige zahl übergeben
    return float(tempP)

"""
Unter https://www.ika.com/de/Produkte-Lab-Eq/Magnetruehrer-Heizruehrer-Laborruehrer-Ruehrer-csp-188/C-MAG-HS-7-control-Downloads-cpdl-20002694/ 
- Betriebsanleitung C-MAG HS 7 control DE wird auf Seite 7 gezeigt was die 1 (PT1000) und die 2 (Kontakt Thermometer ETS-D5 / ETS-D6) bedeuten!
--> werden in get_TempHeizplat() und get_TempPt1000() mit zurückgegeben (bei return werden die abgeschnitten durch split(' '))
"""

###########################################################################
def Read_Ausgabe():                                                       # Mit der Funktion kann man sich die Antwort anzeigen lassen!!
###########################################################################
    if test_heizplat == True:
        print ('Testmodus aktiv!')
        quit()
    else:
        st = ''
        back = ser_py.readline().decode()                                 # bekomme zurück diese Zeile vom Gerät 
        if debug_heizplat == True:    
            print('Reading From ' + ser_py.port + ': ' + repr(back))                                             # Für Test/ debug
        st = back.replace('\r\n', '')
        #print(f"Ausgang wurde gelesen - {st}")                           # Für Test
        return st                                                               

###########################################################################
def change_SollTemp(Solltemp):                                            # Befehl zum ändern der Solltemperatur wird der Heizplatte übergeben (auf Display der Hp kann man das sehen)
###########################################################################
    if test_heizplat == False:
            ser_py.write(('OUT_SP_1 ' + Solltemp +'\r\n').encode())
            if debug_heizplat:
                print ('Sending to ' + ser_py.port + f' den Befehl OUT_SP_1 {Solltemp}\\r\\n')
                get_SollTemp()
                get_SaveTemp()
    #print(f'Solltemperatur wird geändert auf {Solltemp}')                # Für Test
    
    # Notiz:
    # Eine Falsch Eingabe, also sollten Buchstaben übergeben werden, dann setzt die Platte die Temperatur auf 0 °C!
    # Zahlen mit Komma ignoriert es -> Die Platte nimmt nur die Zahlen vor dem Komma bzw. Punkt!

###########################################################################
def get_SollTemp():                                                       # Befehl Erfragen der Solltemperatur
###########################################################################
    if test_heizplat == False:
            if debug_heizplat:
                print ('Sending to ' + ser_py.port + ' den Befehl IN_SP_1\\r\\n')
            ser_py.write(('IN_SP_1' + '\r\n').encode())
    tempSoll = Read_Ausgabe().split(' ')[0] 
    print (f'Die Solltemperatur ist gerade {tempSoll} °C groß.')
    return tempSoll

###########################################################################
def get_SaveTemp():                                                       # Befehl Erfragen der Sicherheitstemperatur
###########################################################################
    if test_heizplat == False:
            if debug_heizplat:
                print ('Sending to ' + ser_py.port + ' den Befehl IN_SP_3\\r\\n')
            ser_py.write(('IN_SP_3 ' + '\r\n').encode())
    SaveTemp = Read_Ausgabe().split(' ')[0] 
    print(f'Die Sicherheitstemperatur ist gerade {SaveTemp} °C groß.')
    return SaveTemp

###########################################################################
def Start_Heizung():                                                      # Befehl zum Starten der Heizplatte wird übergeben + Der Plot wird erzeugt
###########################################################################
    if test_heizplat == False:
            if debug_heizplat:
                print ('Sending to ' + ser_py.port + ' den Befehl START_1\\r\\n')
            ser_py.write(('START_1' + '\r\n').encode())
            print('Heizvorgang Startet, Heizung An!')
            
###########################################################################
def Stop_Heizung():                                                       # Befehl zum Stoppen der Heizplatte wird übergeben
###########################################################################
    if test_heizplat == False:
        if debug_heizplat:
            print ('Sending to ' + ser_py.port + ' den Befehl STOP_1\\r\\n')
        ser_py.write(('STOP_1' + '\r\n').encode())
        print('Heizvorgang Zuende, Heizung Aus!')    


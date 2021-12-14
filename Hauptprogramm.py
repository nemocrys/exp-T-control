"""
Notizen:
Kürzel:     Pt  - Pt1000
            Hp  - Heizplatte
            Py  - Pyrometer
            HP  - Heizplatte und Pt1000

            Kw      - Pyrometer mit kurzen Wellen
            Lw1/Lw  - Pyrometer mit langen Wellen                           - Aspektverhältnis 20:1    (Distanzverhältnis)
            Lw2     - Pyrometer mit langen Wellen aber andere Seriennummer  - Aspektverhältnis 10:1    (Distanzverhältnis)

            AD1 - AD3   - Adafruits mit Pt100 oder Pt1000
"""

# Bibliotheken:
from Heizplatte import *                        # Hardware Funktionen der IKA C-MAG HS 7 control Heizplatte mit externen Temperaturmesssensor (hier Pt1000)
from Pyrometer import *                         # Hardware Funktionen des Pyrometers (kurzwellig)
from Pyrometer_Array import *                   # Hardware Funktionen des Pyrometers (Langwellig)
from Adafruit_PT100 import *                    # Hardware Funktionen des Adafruit PT100 

import time
import datetime                                 # Holt die Tageszeit + Datum
import random                                   # Bibliothek zum erzeugen von Zufallszahlen
import os                                       # Bibliothek für Dateipfade
from tkinter import *                           # Bibliothek zum erstellen von Fenstern
from tkinter import ttk
import numpy as np                              # Bibliothek für das Arbeiten mit Vektoren usw.
import matplotlib.pyplot as plt                 # Bibliothek für die Ausgabe von Graphen
import argparse 
import configparser
import logging                                  # https://docs.python.org/3/howto/logging.html
import subprocess                               # Bibliothek zum Ausführen von Unterprozessen

# Globale Variablen:
global FileOutName, FileOutNameE, FileOutNameEEnd, nStart, listTiRe, listTempHp, listTempPt, listTempPyKw, listTempPyKw2, listTempPyLw, AutoStop_Pt, AutoStop_Hp, AutoStop_Py, time_start, figure, figure1, figure2, line1, line2, line3, line4, line6, line7, line8, line9, lineE1, lineE2, lineE3, ax1, ax2, ax3, ax4, sampling_Time, Laser, xVonPt, xBestPt, yVonPt, yBestPt, xVonHp, xBestHp, yVonHp, yBestHp, xVonPy, xBestPy, yVonPy, yBestPy, py1_In, py2_In, py3_In, py4_In, AD1_In, AD2_In, AD3_In, PyroKw_Init, PyroKw2_Init, PyroLw_Init, PyroLw_Config, PyroLw2_Config, AD1_Init, AD2_Init, AD3_Init, anzFehler, listPy, TempTrep, TempArea, TempTime, Config, loop, StartConfig, starttimeConfig, nextTempIn, comHp, comLw, comKw, comKw2, Folder, sAD1, sAD2, sAD3, sPyroKw, sPyroKw2, sPyroLw, sPyroLw2, e_Drauf1, e_Drauf2, e_Drauf3, e_py1, e_py2, e_py3, nEMess, Stop_Graph, listEmisPyKw, listEmisPyLw, listEmisPyLw2, Vergleich_Ort, tempVergleich

# Initialisiere die Koordinatenvariablen:
xVonPt = xBestPt=  yVonPt = yBestPt = xVonHp = xBestHp = yVonHp = yBestHp = xVonPy = xBestPy = yVonPy = yBestPy = 0 

# Bezeichnungen, Werte für die Geräte auslesen:
Config_Value = configparser.ConfigParser()
Config_Value.read('Configurationen.txt', encoding="utf-8")
for section_name in Config_Value.sections():
    if section_name == 'Name Legend':
        for name, comDevice in Config_Value.items(section_name):
            if name == 'ad1':                                       # müssen im Programm klein geschrieben werden!!!!! programm macht beim Auslesen jeden Buchstaben KLEIN!!
                sAD1 = comDevice
            if name == 'ad2':
                sAD2 = comDevice
            if name == 'ad3':
                sAD3 = comDevice
            if name == 'pyrokw':                                    # noch nicht eingebaut, da Daten_Einlesen.py nicht mehr funktionieren wird!
                sPyroKw = comDevice                                 # Eventuell Im File nur Pyrometer 1 - 4 und wie bei Adafruit zu Beginn dann was was ist!!
            if name == 'pyrokw2':                                   #
                sPyroKw2 = comDevice                                #
            if name == 'pyrolw':                                    #
                sPyroLw = comDevice                                 #
            if name == 'pyrolw2':                                   #
                sPyroLw2 = comDevice                                #
    if section_name == 'Vergleich':                                 # Als Vergleich dienen Erstmal nur die Pt100 am Adafruit - Auswahl Vergleichsgerät für die Emissionsgrad-Anpassung
        for name, comDevice in Config_Value.items(section_name):
            if comDevice == 'AD1':
                Vergleich_Ort = sAD1
            if comDevice == 'AD2':
                Vergleich_Ort = sAD2
            if comDevice == 'AD3':
                Vergleich_Ort = sAD3   

# Funktionen für File und Grafik:
###########################################################################    
def Init_File():                                                          # Variablen für den Start und die Messwert-Datei werden hier initialisiert
###########################################################################   
    # Automatische Erzeugung von eindeutigen Filenamen, ohne das eine alte Datei überschrieben wird!
    global FileOutName, FileOutNameE, FileOutNameEEnd, nStart, listTiRe, listTempHp, listTempPt, listTempPyKw, listTempPyKw2, listTempPyLw, listTempPyLw2, listTempAD1, listTempAD2, listTempAD3, AutoStop_Pt, AutoStop_Hp, AutoStop_Py, Folder, listEmisPyKw, listEmisPyLw, listEmisPyLw2

    ### Variablen und Listen Initialisierung:
    actual_date = datetime.datetime.now().strftime('%Y_%m_%d')            # Variablen für den Datei Namen 
    FileOutPrefix = actual_date
    FileOutIndex = str(1).zfill(2)
    FileOutName = ''    
    
    # Boolche Variablen um bestimmte Aktionen zu Verriegeln oder freizuschalten
    AutoStop_Pt = False
    AutoStop_Hp = False
    AutoStop_Py = False

    # listen für die Messwerte
    listTiRe = []                       # Zeit              
    listTempPt = []                     # PT1000 der Heizplatte
    listTempHp = []                     # Heizplattensensor
    listTempPyKw = []                   # Pyrometer Temperatur
    listTempPyKw2 = [] 
    listTempPyLw = []
    listTempPyLw2 = []
    listEmisPyKw = []                   # Pyrometer Emissionsgrad
    listEmisPyLw = []
    listEmisPyLw2 = []
    listTempAD1 = []                    # Adafruit PT100
    listTempAD2 = []
    listTempAD3 = []

    # Versionsnummer Lesen:
    version = (
        subprocess.check_output(["git", "describe", "--tags", "--dirty", "--always"])
        .strip()
        .decode("utf-8")
    )

    # Erstellung des Filesnamen bzw. Dateinamens und des Ordners, wo alles liegt:
    Folder = 'Bilder_und_Daten/Daten_vom_' + FileOutPrefix                      # Erstelle Ordner Pfad
    if not os.path.exists(Folder):                                              # schaue ob es den Ordner schon gibt
        os.makedirs(Folder)                                                     # wenn nicht dann erstelle ihn
    if args.log == True:   logging.info(f'Ordner - {Folder} erstellt/geprüft') 
    
    FileOutName = FileOutPrefix + '_#' + FileOutIndex + '_temp.txt'             # hier könnte man auch .dat schreiben (muss man dann nur überall anpassen!!)
    j = 1
    while os.path.exists(Folder + '/' + FileOutName) :                          # Schaut ob es den Namen schon in dem Verzeichnis gibt ...
        j = j + 1                                                               # ... wenn ja wird der FleOutIndex (j) solange erhöht bis es eine neue Datei erstellen kann
        FileOutIndex = str(j).zfill(2)
        FileOutName = FileOutPrefix + '_#' + FileOutIndex + '_temp.txt'
    print ('Output data: ', FileOutName)  
    if args.log == True:   logging.info('File Name erzeugt') 

    # Öffnen und Erstellen der Datei
    with open(Folder + '/' + FileOutName,"w", encoding="utf-8") as fo:                 
        fo.write("Temperaturdaten der Heizplatte\n") 
        fo.write(f"Datum: {actual_date}\n\n")
        fo.write(f"Version: {version}\n\n")
        if py3_In == True or py2_In == True:                        
            fo.write('AV - Aspektverhältniss \n')
        if AD1_In == True:
            fo.write(f'Adafruit 1 Ort -> {sAD1} \n')
        if AD2_In == True:
            fo.write(f'Adafruit 2 Ort -> {sAD2} \n')
        if AD3_In == True:
            fo.write(f'Adafruit 3 Ort -> {sAD3} \n')
        fo.write("\nabs. Zeit".ljust(15) + "rel. Zeit [s]".ljust(20) + "Temp. Platte [°C]".ljust(22) + "Temp. PT1000 [°C]".ljust(22))
        if py1_In == True:                                                      # Ab hier: Ausgabe wenn gewollt!
            fo.write("Temp. Pyro. Kurzw. [°C]".ljust(28))
        if py2_In == True:
            fo.write("Temp. Pyro. Langw. AV: 20:1 [°C]".ljust(35))
        if py3_In == True:
            fo.write("Temp. Pyro. Langw. AV: 10:1 [°C]".ljust(35))
        if py4_In == True:                                          
            fo.write("Temp. Pyro. Kurzw. Quo. [°C]".ljust(35))
        if AD1_In == True:
            fo.write("Temp. Adafruit 1 [°C]".ljust(35))
        if AD2_In == True:
            fo.write("Temp. Adafruit 2 [°C]".ljust(35))
        if AD3_In == True:
            fo.write("Temp. Adafruit 3 [°C]".ljust(35))
        fo.write('\n')
        if args.log == True:   logging.info('File Kopf erstellt') 

    # Datei für die Emissionswerte - Erstellung im Manuellen und Rezept Modus:
    # Alle Emissionswerte:
    FileOutNameE = FileOutPrefix + '_#' + FileOutIndex + '_Emis.txt'
    print ('Output data: ', FileOutNameE) 
    with open(Folder + '/' + FileOutNameE,"w", encoding="utf-8") as foE:
        foE.write('Auflistung der Emissionsgrade:\n')
        foE.write(f"Datum: {actual_date}\n\n")
        foE.write(f"Version: {version}\n\n")
        if Config == True:
            foE.write('Rezept:\n')
            foE.write('-------\n')
            foE.write(f'Solltemperaturen:     {TempTrep}\n')
            foE.write(f'Regelbereich:         {TempArea}\n')
            foE.write(f'Zeit im Regelbereich: {TempTime}\n\n')
        foE.write('Emissionsrad ist 100 % - wenn keine Anpassung vorgenommen wird!\n\n')
        foE.write("abs. Zeit".ljust(15) + "Zeit [s]".ljust(15))
        if py1_In == True:                                          
            foE.write("Emissionsgrad Py. Kw. [%]".ljust(35))
        if py2_In == True:
            foE.write("Emissionsgrad Py. Lw. 20:1 [%]".ljust(35))
        if py3_In == True:
            foE.write("Emissionsgrad Py. Lw. 10:1 [%]".ljust(35))
        foE.write('\n')
        if args.log == True:   logging.info('File für Emissionsgrade erstellt')
        
    # Nur die Letzten: 
    FileOutNameEEnd = FileOutPrefix + '_#' + FileOutIndex + '_Emis_Ende.txt'
    print ('Output data: ', FileOutNameEEnd)
    with open(Folder + '/' + FileOutNameEEnd,"w", encoding="utf-8") as foEE:
        foEE.write('Auflistung der Emissionsgrade:\n')
        foEE.write(f"Datum: {actual_date}\n\n")
        foEE.write(f"Version: {version}\n\n")
        if Vergleich_Ort == sAD1 and AD1_In == False:            # Wenn das Gerät für den Vergleich nicht da ist, so wird der Pt1000 als Default eingetragen
            new_Vergleich_Ort = 'Pt1000 Heizplatte'              # new_Vergleich_Ort ist eine lokale Variable, dadurch kann man im Manuellen Modus mit Stopp arbeiten, da der alte Vergleich_Ort dann nicht überschrieben wird
        elif Vergleich_Ort == sAD2 and AD2_In == False:
            new_Vergleich_Ort = 'Pt1000 Heizplatte'
        elif Vergleich_Ort == sAD3 and AD3_In == False:
            new_Vergleich_Ort = 'Pt1000 Heizplatte'
        else:
            new_Vergleich_Ort = Vergleich_Ort
        foEE.write(f'Vergleichsgeräte für die Pyrometeranpassung: {new_Vergleich_Ort}\n\n')
        if args.log == True:   logging.info(f'Vergleichsgerät = {Vergleich_Ort}')
        if Config == True:
            foEE.write('Rezept:\n')
            foEE.write('-------\n')
            foEE.write(f'Solltemperaturen:     {TempTrep}\n')
            foEE.write(f'Regelbereich:         {TempArea}\n')
            foEE.write(f'Zeit im Regelbereich: {TempTime}\n\n')
        foEE.write('Emissionsrad ist 100 % - wenn keine Anpassung vorgenommen wird!\n\n')
        foEE.write("Soll. Temperatur".ljust(25))
        foEE.write("Vergleichs-Temperatur".ljust(35))
        if py1_In == True:                                          
            foEE.write("Emissionsgrad Py. Kw. [%]".ljust(35))
        if py2_In == True:
            foEE.write("Emissionsgrad Py. Lw. 20:1 [%]".ljust(35))
        if py3_In == True:
            foEE.write("Emissionsgrad Py. Lw. 10:1 [%]".ljust(35))
        foEE.write('\n')
        if args.log == True:   logging.info('File für Emissionsgrade Endwerte erstellt')
            
###########################################################################  
def fenster_GUI():                                                        # Enthält die Eingabefelder und Knöpfe für die Schaltoberfläche! 
###########################################################################  
    # Quelle - https://pythonbuch.com/gui.html -
    
    # Definitionen der Aktionen der Knöpfe:
    def button_action_1():                  # Start Knopf
        anweisungs_label_1.config(Start())  

    def button_action_2():                  # Stop Knopf
        anweisungs_label_2.config(Stop())   

    def button_action_3():                  # Beenden Knopf
        info_label.config(Stop())
        quit()                      

    def button_action_4():                  # ändere Solltemperatur Knopf 
        entry_text = eingabefeld_SollT.get()
        if (entry_text == ""):
            Sollwert = get_SollTemp()       # ruft aktuelle Sollwerttemperatur auf!
            change_label.config(text=f"Eingabe Solltemperatur bitte! \n Solltemperatur = {Sollwert} °C")
        elif Config == True or Press_Anpass == True:
            Sollwert = get_SollTemp()       # ruft aktuelle Sollwerttemperatur auf!
            change_label.config(text=f"Anpassung/Rezept läuft, \nEingabe nicht möglich! \n Solltemperatur = {Sollwert} °C")
        elif entry_text.isnumeric() == True :
            new_Soll = entry_text
            entry_text = "Solltemperatur ist nun\n " + entry_text + " °C groß!" 
            change_SollTemp(new_Soll) 
            change_label.config(text=entry_text)
        else:
            Sollwert = get_SollTemp()
            change_label.config(text=f"Nur Ganzzahlen sind \n möglich zur Eingabe! \nSolltemperatur = {Sollwert} °C")

    def button_action_5_Pt():                  # Autoscaling beenden Knopf - Pt1000
        global AutoStop_Pt, xBestPt, yBestPt, xVonPt, yVonPt
        AutoStop_Pt = True

        xBestPt = Eingabe_Koordinaten(eingabefeld_xAchsePt, change_label_xPt, 'xEnde')
        yBestPt = Eingabe_Koordinaten(eingabefeld_yAchsePt, change_label_yPt, 'yEnde')
        xVonPt = Eingabe_Koordinaten(eingabefeld_xVonPt, change_label_xvPt, 'xBeginn')
        yVonPt = Eingabe_Koordinaten(eingabefeld_yVonPt, change_label_yvPt, 'yBeginn')
        
    def button_action_5_Hp():                  # Autoscaling beenden Knopf - Heizplatte
        global AutoStop_Hp, xBestHp, yBestHp, xVonHp, yVonHp
        AutoStop_Hp = True

        xBestHp = Eingabe_Koordinaten(eingabefeld_xAchseHp, change_label_xHp, 'xEnde')
        yBestHp = Eingabe_Koordinaten(eingabefeld_yAchseHp, change_label_yHp, 'yEnde')
        xVonHp = Eingabe_Koordinaten(eingabefeld_xVonHp, change_label_xvHp, 'xBeginn')
        yVonHp = Eingabe_Koordinaten(eingabefeld_yVonHp, change_label_yvHp, 'yBeginn')
        
    def button_action_5_Py():                  # Autoscaling beenden Knopf - Pyrometer
        global AutoStop_Py, xBestPy, yBestPy, xVonPy, yVonPy
        AutoStop_Py = True

        xBestPy = Eingabe_Koordinaten(eingabefeld_xAchsePy, change_label_xPy, 'xEnde')
        yBestPy = Eingabe_Koordinaten(eingabefeld_yAchsePy, change_label_yPy, 'yEnde')
        xVonPy = Eingabe_Koordinaten(eingabefeld_xVonPy, change_label_xvPy, 'xBeginn')
        yVonPy = Eingabe_Koordinaten(eingabefeld_yVonPy, change_label_yvPy, 'yBeginn')

    def button_action_6_Pt():                  # Autoscaling einschalten Knopf - Pt1000
        global AutoStop_Pt
        AutoStop_Pt = False  

    def button_action_6_Hp():                  # Autoscaling einschalten Knopf - Heizplatte
        global AutoStop_Hp
        AutoStop_Hp = False  

    def button_action_6_Py():                  # Autoscaling einschalten Knopf - Pyrometer
        global AutoStop_Py
        AutoStop_Py = False  

    def button_action_7():                  # Bild/Graph/Diagramm speichern Knopf
        save_label.config(save())
    
    def button_action_8():                  # Messzeit ändern Knopf
        global sampling_Time
        
        entry_text_MessT = eingabefeld_MessT.get()                                      
        if (entry_text_MessT == ""):                                                                           # bei keinem Eintrag wird der Default Wert genommen                                      
            change_label_MessT.config(text=f"Eingabe Abtastrate bitte! \nAbtastrate beträgt {args.dt} ms!")
            if args.dt:                                                                                        # Wenn ein Wert mit args.dt eingegeben wurde so wird der als Default genommen!
                sampling_Time = args.dt
            else:
                sampling_Time = 1000                                                                           # Wenn man ohne startet werden die 1000 ms genommen!
        else:
            new_MessT = entry_text_MessT
            if new_MessT.isnumeric() == True and int(new_MessT) >= 1000:                                       # Sollte keine Zahl vorliegen oder der Wert kleiner 1000 ms sein, so wird ein Fehler ausgegeben und die Messzeit auf den Default Wert gelegt  
                sampling_Time = int(new_MessT)
                change_label_MessT.config(text="Abtastrate ist nun \n" + new_MessT + " ms groß!")
            else:
                if args.dt:                                                                                    # Wenn ein Wert mit args.dt eingegeben wurde so wird der als Default genommen!
                    sampling_Time = args.dt
                else:
                    sampling_Time = 1000 
                change_label_MessT.config(text=f"Falsche Eingabe oder\n zu klein (A.Rate > 1000 ms)! \n Default -> A.Rate = {sampling_Time} ms")

    def button_action_9():                                              # ändere Emissionsgrad Knopf (Kw)
        if py1_In == True and PyroKw_Init == True:
            entry_text_E = eingabefeld_Emiss.get()
            if (entry_text_E == ""):
                change_label_E.config(text="Eingabe e bitte!")
            elif Config == True or Press_Anpass == True:
                change_label_E.config(text="Anpassung/Rezept läuft, \nEingabe nicht möglich!")
            else:   
                new_e = entry_text_E.replace(',', '.')                                                                  # Durch das replace hier, kann man auch ein Komma eingeben!
                if new_e.isnumeric() == True and float(new_e) <= 100 and float(new_e) >= 5:                             # float da die Genauigkeit eine nachkommerstelle beträgt! Replace brauch man um den Punkt mit lesen zu können!
                    entry_text_E = "e ist nun \n" + new_e + " % groß!" 
                    Write_Pyro_Para(0,'e',new_e)
                    change_label_E.config(text=entry_text_E)
                else:
                    change_label_E.config(text=f"Falsche Eingabe oder \n nicht im Bereich \n (5 % < e < 100 %)!")
        else:
            change_label_E.config(text='Pyrometer (Kw) \n nicht Vorhanden!')

    def button_action_10():                                             # ändere Transmissionsgrad Knopf (Kw)
        if py1_In == True and PyroKw_Init == True:
            entry_text_T = eingabefeld_Trans.get()
            if (entry_text_T == ""):
                change_label_T.config(text="Eingabe t bitte!")
            elif Config == True or Press_Anpass == True:
                change_label_T.config(text="Anpassung/Rezept läuft, \nEingabe nicht möglich!")
            else:   
                new_t = entry_text_T.replace(',', '.')
                if new_t.isnumeric() == True and float(new_t) <= 100 and float(new_t) >= 5:                                                   # float da die Genauigkeit eine nachkommerstelle beträgt!
                    entry_text_T = "t ist nun \n" + new_t + " % groß!" 
                    Write_Pyro_Para(0,'t',new_t)
                    change_label_T.config(text=entry_text_T)
                else:
                    change_label_T.config(text=f"Falsche Eingabe oder \n nicht im Bereich \n (5 % < t < 100 %)!")
        else:
            change_label_T.config(text='Pyrometer (Kw) \n nicht Vorhanden!')

    def button_action_11():                                              # Schalte Laser An und Aus!
        global Laser, Laser2
        if (py1_In == True and PyroKw_Init == True) or (py4_In == True and PyroKw2_Init == True):
            if Laser == False:
                if py1_In == True:
                    Write_Pilot(0,True)
                if py4_In == True:
                    Write_Pilot(1,True)    
                change_label_Laser.config(text='Laser An!')
                Laser = True
            else:
                if py1_In == True:
                    Write_Pilot(0,False)
                if py4_In == True:
                    Write_Pilot(1,False) 
                change_label_Laser.config(text='Laser Aus!')
                Laser = False
        else:
            change_label_Laser.config(text='Kein Pyrometer (Kw) \n Vorhanden!')
                
    def button_action_12():                                                  # Abfrage Fokus (Kw)
        if py1_In == True and PyroKw_Init == True:
            fokus = Get_Focus(0).replace('\r','')[4:]                        # die hinteren 4 Zahlen sind für uns interessant (Antwort endet mit \r)
            if args.debug:
                print(repr('Antwort des Pyrometers: ' + Get_Focus(0)))
            change_label_Fokus.config(text=f'Fokus des Pyrometers (Kw) \n ist {fokus} mm.')
        else:
            change_label_Fokus.config(text='Pyrometer (Kw) \n nicht Vorhanden!')
        if py4_In == True and PyroKw2_Init == True:
            fokus = Get_Focus(1).replace('\r','')[4:]                        # die hinteren 4 Zahlen sind für uns interessant (Antwort endet mit \r)
            if args.debug:
                print(repr('Antwort des Pyrometers: ' + Get_Focus(1)))
            change_label_Fokus2.config(text=f'Fokus des Pyrometers (Kw2) \n ist {fokus} mm.')
        else:
            change_label_Fokus2.config(text='Pyrometer (Kw2) \n nicht Vorhanden!')

    def button_action_13():                                              # Abfrage Sicherheitstemperatur der Heizplatte
        saveST = get_SaveTemp()                    
        change_label_saveST.config(text=f'Sicherheitstemp. der \n Heizplatte ist {saveST} °C.')

    def button_action_14():                  # Messgeräte Rein oder Raus
        global py1_In, py2_In, py3_In, py4_In, AD1_In, AD2_In, AD3_In

        if nStart == False:                  # Nur wenn man außerhalb des Startes ist, kann man die Variablen verändern und Messgeräte rein- oder rausnehmen!
            py1_In = var_py1.get()           # Pyrometer Kw
            py2_In = var_py2.get()           # Pyrometer Lw 20:1
            py3_In = var_py3.get()           # Pyrometer Lw 10:1
            py4_In = var_py4.get()           # Pyrometer Quotientenpyrometer 
            AD1_In = var_APT1.get()          # PT100 Adafruit 1
            AD2_In = var_APT2.get()          # PT100 Adafruit 2
            AD3_In = var_APT3.get()          # PT100 Adafruit 3

    def button_action_15():                                              # ändere Emissionsgrad Knopf (Lw 20:1)
        if py2_In == True and PyroLw_Init == True:
            entry_text_E = eingabefeld_EmissLw.get()
            if (entry_text_E == ""):
                change_label_ELw.config(text="Eingabe Emissionsgrad bitte!")
            elif Config == True or Press_Anpass == True:
                change_label_ELw.config(text="Anpassung/Rezept läuft, \nEingabe nicht möglich!")
            else:   
                new_e = entry_text_E.replace(',', '.')
                if new_e.replace('.','').isnumeric() == True and float(new_e) <= 120 and float(new_e) >= 10:                   # float da die Genauigkeit eine nachkommerstelle beträgt!
                    entry_text_E = "Emissionsgrad ist nun " + new_e + " % groß!" 
                    Write_Pyro_Array_Para(0,'e',new_e)
                    change_label_ELw.config(text=entry_text_E)
                else:
                    change_label_ELw.config(text=f"Falsche Eingabe oder \n nicht im Bereich \n (10 % < e < 120 %)!")
        else:
            change_label_ELw.config(text='Pyrometer (Lw 20:1) \n nicht Vorhanden!')

    def button_action_16():                                              # ändere Emissionsgrad Knopf (Lw 10:1)
        if py3_In == True and PyroLw_Init == True:
            entry_text_E = eingabefeld_EmissLw2.get()
            if (entry_text_E == ""):
                change_label_ELw2.config(text="Eingabe Emissionsgrad bitte!")
            elif Config == True or Press_Anpass == True:
                change_label_ELw2.config(text="Anpassung/Rezept läuft, \nEingabe nicht möglich!")   
            else:   
                new_e = entry_text_E.replace(',', '.')  
                if new_e.replace('.','').isnumeric() == True and float(new_e) <= 120 and float(new_e) >= 10:                   # float da die Genauigkeit eine nachkommerstelle beträgt!
                    entry_text_E = "Emissionsgrad ist nun " + new_e + " % groß!" 
                    Write_Pyro_Array_Para(1,'e',new_e)
                    change_label_ELw2.config(text=entry_text_E)
                else:
                    change_label_ELw2.config(text=f"Falsche Eingabe oder \n nicht im Bereich \n (10 % < e < 120 %)!")
        else:
            change_label_ELw2.config(text='Pyrometer (Lw 10:1) \n nicht Vorhanden!')

    def button_action_17():                  # Graph aktualisieren anhalten, Toggelend
        global Stop_Graph
        
        if Stop_Graph == False:
            Stop_Graph = True
            change_label_nogra.config(text="Graph Stopp")
        else:
            Stop_Graph = False
            change_label_nogra.config(text="Graph Weiter")
        
    def button_action_18():                  # Emiss.-Anpassung manuel starten, Toggelend
        global Press_Anpass, nEMess, e_py1, e_py2, e_py3, e_Drauf1, e_Drauf2, e_Drauf3
        
        if Config == False:
            if Press_Anpass == False:
                Press_Anpass = True
                change_label_EmissAn.config(text="Anpassung Ein")
                # Da mann die Emissionsgrade auch selber Eingeben kann im Manuelen Modus, soll der Emissionsgrad zuerst auf 100 % wieder gesetzt werden!
                if py1_In == True:                                                      # Pyrometer Kw wird zurückgesetzt, wenn da
                    Write_Pyro_Para(0, 'e', 100)
                if py2_In == True:                                                      # Pyrometer Lw 20:1 wird zurückgesetzt, wenn da
                    Write_Pyro_Array_Para(0, 'e', 100)
                if py3_In == True:                                                      # Pyrometer Lw 10:1 wird zurückgesetzt, wenn da
                    Write_Pyro_Array_Para(1, 'e', 100)
                print('Anpassung Startet!')
                if args.log == True:   logging.info('Anpassung Manuell wurde gestartet.')
                nEMess = 0
            else:
                Press_Anpass = False
                change_label_EmissAn.config(text="Anpassung Aus")
                with open(Folder + '/' + FileOutNameE,"a", encoding="utf-8") as foE:
                    endtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    foE.write(f'- - - Anpassung ist abgeschlossen! - {endtime} - - -\n')
                if py1_In == True:                                                      # Pyrometer Kw wird zurückgesetzt, wenn da
                    Write_Pyro_Para(0, 'e', 100)                                        # Hiermit wird nach der Anpassung der Wert wieder auf Hundert Prrozent gesetzt!
                    e_py1 = 100
                    e_Drauf1 = 100
                if py2_In == True:                                                      # Pyrometer Lw 20:1 wird zurückgesetzt, wenn da
                    Write_Pyro_Array_Para(0, 'e', 100)
                    e_py2 = 100
                    e_Drauf2 = 100
                if py3_In == True:                                                      # Pyrometer Lw 10:1 wird zurückgesetzt, wenn da
                    Write_Pyro_Array_Para(1, 'e', 100)
                    e_py3 = 100
                    e_Drauf3 = 100
                print('Anpassung Beendet!')
                if args.log == True:   logging.info('Anpassung Manuell wurde beendet.')
        else:
            change_label_EmissAn.config(text="Rezeptmodus!")

    # Dadurch wird die Messung in ca. jeder Sekunde durchgeführt (Abweichungen von ms sind möglich!)
    def task():
        if nStart == True:                         # Startet nur wenn auch der Start-Knopf betätigt wird!
            get_Measurment()
            fenster.after(sampling_Time, task) 
        else:
            fenster.after(10, task)                # Solange Start nicht gedrückt wird, soll der task so schnell wie möglich widerholt werden! So kommen bei größeren Messabständen keine Riesiegen Lücken zum KoordinatenUrsprung zustande!

    def Eingabe_Koordinaten(Einagbefeld, ChangeLabel, Modi):                    # Funktion für die Einstellung der Koordinaten der Graphen
        wert = 0
        entry_text = Einagbefeld.get()                                          # Eingabe für die koordinate
        if (entry_text == ""):                                                  # Bei Leerem Eingabefeld wird das gegeben
            if Modi == 'xEnde':                                                 # Je nach Modi wird etwas anderes verändert (hätte man auch mit case machen können)
                ChangeLabel.config(text="x = 100 s")
                wert = 100
            elif Modi == 'yEnde':
                ChangeLabel.config(text="y = 100 °C")
                wert = 100
            elif Modi == 'xBeginn':
                ChangeLabel.config(text="x startet bei 0 s")
                wert = 0
            elif Modi == 'yBeginn':
                ChangeLabel.config(text="y startet bei 0 °C")
                wert = 0
        else:
            new = entry_text.replace(',','.')                                   # Wenn ein Text vorhanden ist, so wird bei Komma Eingabe, das zu einem Punkt - Somit ist als Eingabe sowohl ein Komma als auch der Punkt möglich
            if new.replace('.','').isnumeric() == True:                         # Wenn die Eingabe eine Zahl ist - so wird die Koordinate geändert
                wert = float(new)
                if Modi == 'xEnde':
                    ChangeLabel.config(text="x = "+ new + " s")
                elif Modi == 'yEnde':
                    ChangeLabel.config(text="y = " + new + " °C")
                elif Modi == 'xBeginn':
                    ChangeLabel.config(text="x beginnt bei "+ new + " s")
                elif Modi == 'yBeginn':
                    ChangeLabel.config(text="y beginnt bei " + new + " °C")
            else:                                                                # Sollte die Eingabe falsch sein, so wird es auch als Falsch ausgegeben, der Defaultwert wird ausgegeben!
                ChangeLabel.config(text="Die Eingabe ist Falsch!")
                if Modi == 'xEnde' or Modi == 'yEnde':
                    wert = 100
                elif Modi == 'xBeginn' or Modi == 'yBeginn' :
                    wert = 0
        return wert

    # X -Button wird außer Betrieb genommen!
    def disable_event():
        pass

    ################################################################################################################

    # Ein Fenster erstellen:
    fenster = Tk()
    # Den Fenstertitle erstellen:
    fenster.title("Temperaturmessung einer Heizplatte")

    ################################################################################################################

    # Buttons:
    Start_button_1 = Button(fenster, text="Start", command=button_action_1)                                # Start der Heizung und Messung
    Stop_button_1 = Button(fenster, text="Stop", command=button_action_2)                                  # Stop der Heizung und Messung
    exit_button = ttk.Button(fenster, text="Beenden", command=button_action_3)                             # Fenster Schließen und Heizung Stoppen
    # Heizplatte und Pt1000
    Eingabe_button_1 = Button(fenster, text="Ändere Solltemperatur", command=button_action_4)              # Solltemperatur ändern
    # Allgemeine Funktionen
    AutoStop_button_1_Pt = Button(fenster, text="AutoScale Aus + Ändern", command=button_action_5_Pt)      # Beenden Auto Skalieren - Pt1000
    AutoStop_button_1_Hp = Button(fenster, text="AutoScale Aus + Ändern", command=button_action_5_Hp)      # Beenden Auto Skalieren - Heizplatte
    AutoStop_button_1_Py = Button(fenster, text="AutoScale Aus + Ändern", command=button_action_5_Py)      # Beenden Auto Skalieren - Pyrometer
    AutoStop_button_2_Pt = Button(fenster, text="AutoScale Ein", command=button_action_6_Pt)               # Einschalten Auto Skalieren - Pt1000
    AutoStop_button_2_Hp = Button(fenster, text="AutoScale Ein", command=button_action_6_Hp)               # Einschalten Auto Skalieren - Heizplatte
    AutoStop_button_2_Py = Button(fenster, text="AutoScale Ein", command=button_action_6_Py)               # Einschalten Auto Skalieren - Pyrometer
    save_button = Button(fenster, text="Bild speichern!", command=button_action_7)                         # Bild soll gespeichert werden
    Eingabe_button_2 = Button(fenster, text="Ändere Abtastrate", command=button_action_8)                  # Messzeit ändern
    # Pyrometer Kw
    Eingabe_button_3 = Button(fenster, text="Ändere e (Kw)", command=button_action_9)                      # Emissionsgrad Kw ändern
    Eingabe_button_4 = Button(fenster, text="Ändere t (Kw)", command=button_action_10)                     # Transmissionsgrad Kw ändern
    Laser_Button = Button(fenster, text="Laser", command=button_action_11)                                 # Laser des Pyrometers Ein und Ausschalten
    Fokus_Button = Button(fenster, text="Erfrage Fokus", command=button_action_12)                         # Fokus des Pyrometers erfragen
    # Pyrometer Lw
    Eingabe_button_5 = Button(fenster, text="Ändere e (Lw 20:1)", command=button_action_15)                # Emissionsgrad Lw 20:1 ändern
    # Pyrometer Lw
    Eingabe_button_6 = Button(fenster, text="Ändere e (Lw 10:1)", command=button_action_16)                # Emissionsgrad lw 10:1 ändern
    # Sicherheitstemperatur:
    SaveST_Button = Button(fenster, text="Erfrage Save-Temp.", command=button_action_13)                   # Sicherheitstemperatur der Heizplatte erfragen
    # Checkbox:
    check_Button = Button(fenster, text="Geräte Bestätigen", command=button_action_14)                     # Checkboxen Aktualisieren
    # Graph anhalten/weitermachen:
    nogra_button = Button(fenster, text="Graph I/O", command=button_action_17)                             # Hält das Aktualisieren des Plottes an!
    # Graph anhalten/weitermachen:
    EmissAn_button = Button(fenster, text="Anpassung", command=button_action_18)                           # Startet die Anpassung des Emissionsgrades

    ################################################################################################################

    # Labels (Texte auf der Schaltoberfläche):
    ### Start, Stop und Beenden:
    anweisungs_label_1 = Label(fenster, text="Start \nHeizung/Messung!")
    anweisungs_label_2 = Label(fenster, text="Stop \nHeizung/Messung!")
    info_label = Label(fenster, text="Schließen und Stoppen")
    ### Solltemperatur:
    change_label = Label(fenster)
    my_label = Label(fenster, text="Solltemperatur: ")
    ### Auto Scaling:
    change_label_xPt = Label(fenster)                               # Ende der Skala
    change_label_yPt = Label(fenster)
    change_label_xvPt = Label(fenster)                              # Beginn der Skala
    change_label_yvPt = Label(fenster)
    #
    change_label_xHp = Label(fenster)                               # Ende der Skala
    change_label_yHp = Label(fenster)
    change_label_xvHp = Label(fenster)                              # Beginn der Skala
    change_label_yvHp = Label(fenster)
    #
    change_label_xPy = Label(fenster)                               # Ende der Skala
    change_label_yPy = Label(fenster)
    change_label_xvPy = Label(fenster)                              # Beginn der Skala
    change_label_yvPy = Label(fenster)
    #
    label_x = Label(fenster, text="x-Achse Ende: ")                 # Ende der Skala
    label_y = Label(fenster, text="y-Achse Ende: ")
    label_xv = Label(fenster, text="x-Achse Beginn: ")              # Beginn der Skala
    label_yv = Label(fenster, text="y-Achse Beginn: ")
    #
    label_pt = Label(fenster, text="Pt1000 Koordinaten")            # Welche Eingabefelder welchem Graph gehören
    label_heiz = Label(fenster, text="Heizplatten Koordinaten")
    label_py = Label(fenster, text="Pyrometer Koordinaten")

    ### Save:
    save_label = Label(fenster, text="Zwischen Speichern")

    ### Messzeit ändern:
    Mess_label = Label(fenster, text="Abtastrate in ms: ")
    change_label_MessT = Label(fenster)

    ### Pyrometer Kw Daten:
    change_label_E = Label(fenster)
    change_label_T = Label(fenster)
    my_label_E = Label(fenster, text='e (Kw) in %:')
    my_label_T = Label(fenster, text='t (Kw) in %:')
    #
    change_label_Laser = Label(fenster)
    change_label_Fokus = Label(fenster)
    change_label_Fokus2 = Label(fenster)
    label_pyro = Label(fenster, text='Pyrometer Knöpfe (Kw):')

    ### Pyrometer Lw1 Daten:
    change_label_ELw = Label(fenster)
    my_label_ELw = Label(fenster, text='e (Lw 20:1) in %:')

    ### Pyrometer Lw2 Daten:
    change_label_ELw2 = Label(fenster)
    my_label_ELw2 = Label(fenster, text='e (Lw 10:1) in %:')

    ### Sicherheitstemperatur:
    change_label_saveST = Label(fenster)
    label_Heizplatte = Label(fenster, text='Heizplatte Knöpfe:')

    ### Checkbox:
    checkbox_label = Label(fenster, text="Messgeräte:")

    ### # Graph anhalten/weitermachen:
    change_label_nogra = Label(fenster)

    ### Emiss. Anpassung anhalten/weitermachen:
    change_label_EmissAn = Label(fenster)

    ################################################################################################################

    # Eingabefelder:
    eingabefeld_SollT = Entry(fenster, bd=5, width=10)          # Solltemperatur
    #
    eingabefeld_xAchsePt = Entry(fenster, bd=2, width=10)       # Achsen-Koordinaten Graph Pt1000
    eingabefeld_yAchsePt = Entry(fenster, bd=2, width=10)
    eingabefeld_xVonPt = Entry(fenster, bd=2, width=10)
    eingabefeld_yVonPt = Entry(fenster, bd=2, width=10)
    #
    eingabefeld_xAchseHp = Entry(fenster, bd=2, width=10)       # Achsen-Koordinaten Graph Heizplatte
    eingabefeld_yAchseHp = Entry(fenster, bd=2, width=10)
    eingabefeld_xVonHp = Entry(fenster, bd=2, width=10)
    eingabefeld_yVonHp = Entry(fenster, bd=2, width=10)
    #
    eingabefeld_xAchsePy = Entry(fenster, bd=2, width=10)       # Achsen-Koordinaten Graph Pyrometer
    eingabefeld_yAchsePy = Entry(fenster, bd=2, width=10)
    eingabefeld_xVonPy = Entry(fenster, bd=2, width=10)
    eingabefeld_yVonPy = Entry(fenster, bd=2, width=10)
    #
    eingabefeld_MessT = Entry(fenster, bd=5, width=10)          # Messzeit

    # Pyrometer (Kw) Werte:
    eingabefeld_Emiss = Entry(fenster, bd=5, width=10)          # Emissionsgrad Kw
    eingabefeld_Trans = Entry(fenster, bd=5, width=10)          # Transmissionsgrad Kw

    # Pyrometer (Lw1) Werte:
    eingabefeld_EmissLw = Entry(fenster, bd=5, width=10)        # Emissionsgrad Lw 20:1

    # Pyrometer (Lw2) Werte:
    eingabefeld_EmissLw2 = Entry(fenster, bd=5, width=10)       # Emissionsgrad lw 10:1

    ################################################################################################################

    # Checkbox:
    var_py1 = IntVar()
    check_py1 = Checkbutton(fenster, text="Pyrometer Kurzwellig", variable=var_py1)
    var_py2 = IntVar()
    check_py2 = Checkbutton(fenster, text="Pyrometer Langwellig 20:1", variable=var_py2)
    var_py3 = IntVar()
    check_py3 = Checkbutton(fenster, text="Pyrometer Langwellig 10:1", variable=var_py3)
    var_py4 = IntVar()
    check_py4 = Checkbutton(fenster, text="Pyrometer Kw. Quotientenpy.", variable=var_py4)
    var_APT1 = IntVar()
    check_APT1 = Checkbutton(fenster, text=sAD1, variable=var_APT1)
    var_APT2 = IntVar()
    check_APT2 = Checkbutton(fenster, text=sAD2, variable=var_APT2)
    var_APT3 = IntVar()
    check_APT3 = Checkbutton(fenster, text=sAD3, variable=var_APT3)

    ################################################################################################################
    
    # Fenstergröße definieren:
    fenster.geometry("1200x1000")

    # Bestimmung der Orte für die einzelnen Knöpfe, Eingabefeldern und Labels auf der Schaltoberfläche:
 
    #### Start, Stop und Beenden
    anweisungs_label_1.place(x = 30, y = 690, width=120, height=30)
    Start_button_1.place(x = 60, y = 740, width=60, height=30)
    anweisungs_label_2.place(x = 180, y = 690, width=120, height=30)
    Stop_button_1.place(x = 205, y = 740, width=60, height=30)
    info_label.place(x = 65, y = 780, width=200, height=30)
    exit_button.place(x = 125, y = 810, width=70, height=40)
    
    #### Solltemperatur
    my_label.place(x=60, y=410, width=120, height=20)
    eingabefeld_SollT.place(x=180, y=410)
    change_label.place(x=200, y=460, width=200, height=45)
    Eingabe_button_1.place(x=30, y=460, width=170, height=30)
    
    #### Auto Scaling - Knöpfe
    AutoStop_button_1_Pt.place(x=150, y=80, width=180, height=20)       # Aus - Pt1000
    AutoStop_button_1_Hp.place(x=450, y=80, width=180, height=20)       # Aus - Heizplatte
    AutoStop_button_1_Py.place(x=750, y=80, width=180, height=20)       # Aus - Pyrometer
    AutoStop_button_2_Pt.place(x=150, y=50, width=150, height=20)       # Ein - Pt1000
    AutoStop_button_2_Hp.place(x=450, y=50, width=150, height=20)       # Ein - Heizplatte
    AutoStop_button_2_Py.place(x=750, y=50, width=150, height=20)       # Ein - Pyrometer
    #
    #### Auto Scaling - Ende
    eingabefeld_xAchsePt.place(x=160, y=130)
    eingabefeld_yAchsePt.place(x=160, y=180)
    eingabefeld_xAchseHp.place(x=460, y=130)
    eingabefeld_yAchseHp.place(x=460, y=180)
    eingabefeld_xAchsePy.place(x=760, y=130)
    eingabefeld_yAchsePy.place(x=760, y=180)
    #
    change_label_xPt.place(x=210, y=130, width=200, height=20)
    change_label_yPt.place(x=210, y=180, width=200, height=20)
    change_label_xHp.place(x=510, y=130, width=200, height=20)
    change_label_yHp.place(x=510, y=180, width=200, height=20)
    change_label_xPy.place(x=810, y=130, width=200, height=20)
    change_label_yPy.place(x=810, y=180, width=200, height=20)
    #
    label_x.place(x=50, y=130, width=100, height=20)
    label_y.place(x=50, y=180, width=100, height=20)
    #
    #### Auto Scaling - Beginn
    eingabefeld_xVonPt.place(x=160, y=230)
    eingabefeld_yVonPt.place(x=160, y=280)
    eingabefeld_xVonHp.place(x=460, y=230)
    eingabefeld_yVonHp.place(x=460, y=280)
    eingabefeld_xVonPy.place(x=760, y=230)
    eingabefeld_yVonPy.place(x=760, y=280)
    #
    change_label_xvPt.place(x=240, y=230, width=200, height=20)
    change_label_yvPt.place(x=240, y=280, width=200, height=20)
    change_label_xvHp.place(x=540, y=230, width=200, height=20)
    change_label_yvHp.place(x=540, y=280, width=200, height=20)
    change_label_xvPy.place(x=840, y=230, width=200, height=20)
    change_label_yvPy.place(x=840, y=280, width=200, height=20)
    #
    label_xv.place(x=40, y=230, width=120, height=20)
    label_yv.place(x=40, y=280, width=120, height=20)
    #
    #### Auto Scaling - Welche Eingabefelder zu welchen Gerät gehören
    label_pt.place(x=150, y=310, width=160, height=30)
    label_heiz.place(x=450, y=310, width=160, height=30)
    label_py.place(x=750, y=310, width=160, height=30)

    #### Save
    save_label.place(x=370, y=850, width=150, height=30)
    save_button.place(x=390, y=890, width=110, height=30)

    #### Abtastrate ändern:
    Mess_label.place(x=30, y=530, width=150, height=20)
    eingabefeld_MessT.place(x=180, y=530)
    change_label_MessT.place(x=200, y=580, width=200, height=50)
    Eingabe_button_2.place(x=30, y=580, width=150, height=30)    

    #### Pyrometer Daten (Kurzwellig):
    label_pyro.place(x=600, y=700, width=160, height=30)
    # Emission:
    my_label_E.place(x=380, y=410, width=150, height=20)
    eingabefeld_Emiss.place(x=530, y=410)
    change_label_E.place(x=530, y=460, width=200, height=50)
    Eingabe_button_3.place(x=410, y=460, width=120, height=30)
    # Transmission:
    my_label_T.place(x=380, y=530, width=150, height=20)
    eingabefeld_Trans.place(x=530, y=530)
    change_label_T.place(x=530, y=580, width=200, height=50)
    Eingabe_button_4.place(x=410, y=580, width=120, height=30)
    # Laser:
    Laser_Button.place(x=600, y=730, width=100, height=30)
    change_label_Laser.place(x=600, y=770, width=120, height=30)
    # Fokus:
    Fokus_Button.place(x=600, y=820, width=100, height=30)
    change_label_Fokus.place(x=510, y=860, width=300, height=30)
    change_label_Fokus2.place(x=510, y=900, width=300, height=30)

    #### Pyrometer Daten (Langwellig 1 - 20:1):
    my_label_ELw.place(x=670, y=410, width=230, height=20)
    eingabefeld_EmissLw.place(x=900, y=410)
    change_label_ELw.place(x=910, y=460, width=230, height=50)
    Eingabe_button_5.place(x=730, y=460, width=160, height=30)

    #### Pyrometer Daten (Langwellig 2 - 10:1):
    my_label_ELw2.place(x=670, y=530, width=230, height=20)
    eingabefeld_EmissLw2.place(x=900, y=530)
    change_label_ELw2.place(x=910, y=580, width=230, height=50)
    Eingabe_button_6.place(x=730, y=580, width=160, height=30)

    ### Heizplatte:
    label_Heizplatte.place(x=340, y=700, width=180, height=30)
    # Sicherheitstemperatur:
    SaveST_Button.place(x=370, y=730, width=150, height=30)
    change_label_saveST.place(x=370, y=770, width=150, height=30)

    ### Checkbox:
    checkbox_label.place(x=885, y=680, width=220, height=20)
    check_py1.place(x=885, y=750, width=220, height=20)
    check_py2.place(x=885, y=780, width=220, height=20)
    check_py3.place(x=885, y=810, width=220, height=20)
    check_py4.place(x=885, y=840, width=220, height=20)
    check_Button.place(x=885, y=710, width=220, height=30)
    check_APT1.place(x=885, y=870, width=220, height=20)
    check_APT2.place(x=885, y=900, width=220, height=20)
    check_APT3.place(x=885, y=930, width=220, height=20)

    ### Graph anhalten/weitermachen:
    change_label_nogra.place(x = 1090, y = 60, width=90, height=40)
    nogra_button.place(x = 1100, y = 20, width=70, height=40)

    ### Emiss. Anpassung anhalten/weitermachen:
    change_label_EmissAn.place(x = 1090, y = 150, width=100, height=40)
    EmissAn_button.place(x = 1100, y = 110, width=80, height=40)

    ################################################################################################################

    fenster.protocol("WM_DELETE_WINDOW", disable_event)
    fenster.after(10, task)                                           # nach 1s soll die Funktion task aufgerufen werden!
    
    # In der Ereignisschleife auf Eingabe des Benutzers warten.
    if args.log == True:   logging.info('GUI erzeugt') 
    fenster.mainloop()

###########################################################################
def get_Measurment():                                                     # Aufnahme und Verarbeitung der Messwerte, Werte werden in File eingetragen und ins Diagramm übergeben!                                                 
###########################################################################      
    global nStart, anzFehler, loop, StartConfig, starttimeConfig, nextTempIn, e_py1, e_py2, e_py3, e_Drauf1, e_Drauf2, e_Drauf3, nEMess
    
    # Zeiten für das weitere Arbeiten und für das Dokument:
    time_abs = datetime.datetime.now().strftime('%H:%M:%S')
    time_actual = datetime.datetime.now()
        
    # Messwerte holen:
    tempPt = get_TempPt1000()
    if args.log == True:   logging.info(f'Messwerte Heizplatte Pt1000 = {tempPt}')
    tempHp = get_TempHeizplat()
    if args.log == True:   logging.info(f'Messwerte Heizplatte = {tempHp}')
    if py1_In == True:                                              # Diese Art der Zeile sperrt das Ausführen, wenn das Gerät nicht da ist!
        tempPyKw = Read_Pyro(0)
        if args.log == True:   logging.info(f'Messwerte Pyrometer Kw = {tempPyKw}')
    if py2_In == True:
        tempPyLw = Read_Pyro_Array(0)
        if args.log == True:   logging.info(f'Messwerte Pyrometer Lw 20:1 = {tempPyLw}')
        if tempPyLw == 'n.o':                                        # Sollte ein Fehler bei den beiden Pyrometern auftauchen, so wird dies so erkannt!
            tempPt = ''
            print('Error vom Pyrometer Lw 20:1')                    # Fehlernachricht
            if args.log == True:   logging.info('Fehelr von Lw 20:1')
    if py3_In == True:
        tempPyLw2 = Read_Pyro_Array(1)
        if args.log == True:   logging.info(f'Messwerte Pyrometer Lw 10:1 = {tempPyLw2}')
        if tempPyLw2 == 'n.o':                                       # Sollte ein Fehler bei den beiden Pyrometern auftauchen, so wird dies so erkannt!
            tempPt = ''
            print('Error vom Pyrometer Lw 10:1')                    # Fehlernachricht
            if args.log == True:   logging.info('Fehelr von Lw 10:1')
    if py4_In == True:                                              # Diese Art der Zeile sperrt das Ausführen, wenn das Gerät nicht da ist!
        tempPyKw2 = Read_Pyro(1)
        if args.log == True:   logging.info(f'Messwerte Pyrometer Kw2 Quo. = {tempPyKw2}')
    if AD1_In == True:                                              
        tempAD1 = get_Temperatur(0)
        if args.log == True:   logging.info(f'Messwerte Adafruit 1 Pt100 = {tempAD1}')
    if AD2_In == True:
        tempAD2 = get_Temperatur(1)
        if args.log == True:   logging.info(f'Messwerte Adafruit 2 Pt100 = {tempAD2}')
    if AD3_In == True:
        tempAD3 = get_Temperatur(2)
        if args.log == True:   logging.info(f'Messwerte Adafruit 3 Pt100 = {tempAD3}')
    if args.log == True:   logging.info('Messwerte geholt') 

    # Vergleichstemperatur für Anpassung bestimmen:
    if tempPt == '' or tempHp == '' or tempPt == 0 or tempHp == 0:
        if args.log == True:   logging.info('Vergleichstemperatur wird nicht bestimmt!')
    else:    
        if Vergleich_Ort == sAD1 and AD1_In == True:
            tempVergleich = tempAD1
        elif Vergleich_Ort == sAD2 and AD2_In == True:
            tempVergleich = tempAD2
        elif Vergleich_Ort == sAD3 and AD3_In == True:
            tempVergleich = tempAD3
        else:                                                                               # Wenn kein Vergleichspartner aktiv ist, wird die Temperatur des Pt1000 als Default eingesetzt!
            tempVergleich = tempPt
        if args.log == True:   logging.info('Vergleichstemperatur wird bestimmt!')
        if args.log == True:   logging.info(f'Vergleichstemperatur = {tempVergleich}')

    # Messwerte in die Listen schreiben:
    if tempPt == '' or tempHp == '' or tempPt == 0 or tempHp == 0:                 # leere Strings (und 0°C) werden hier abgefangen und verhindern somit ein Fehler
        print(f'Error - Falsche Ausgabe der Geräte (Leerer String oder 0 °C von Hp oder "n.o" von Pyro.Lw)! - {time_abs}')
        if args.log == True:   logging.info('Fehler - Leerer String oder n.o') 
        anzFehler += 1                                                             # Berechne Anzahl der Fehler
        dt = ''                                                                    # bei fehler ist auch das dann nun leer!
    elif nStart == True:                                            
        dt = (time_actual - time_start).total_seconds()
        if args.log == True:   logging.info(f'Zeit = {dt}')
        listTempPt.append(tempPt)
        if args.log == True:   logging.info(f'Listen Länge von listTempPt = {len(listTempPt)}')
        listTempHp.append(tempHp)
        if args.log == True:   logging.info(f'Listen Länge von listTempHp = {len(listTempHp)}')
        if py1_In == True:
            listTempPyKw.append(tempPyKw)
            if args.log == True:   logging.info(f'Listen Länge von listTempPyKw = {len(listTempPyKw)}')
        if py2_In == True:
            listTempPyLw.append(tempPyLw)
            if args.log == True:   logging.info(f'Listen Länge von listTempPyLw = {len(listTempPyLw)}')
        if py3_In == True:
            listTempPyLw2.append(tempPyLw2)
            if args.log == True:   logging.info(f'Listen Länge von listTempPyLw2 = {len(listTempPyLw2)}')
        if py4_In == True:
            listTempPyKw2.append(tempPyKw2)
            if args.log == True:   logging.info(f'Listen Länge von listTempPyKw2 = {len(listTempPyKw2)}')
        if AD1_In == True:                                              
            listTempAD1.append(tempAD1)
            if args.log == True:   logging.info(f'Listen Länge von listTempAD1 = {len(listTempAD1)}')
        if AD2_In == True:
            listTempAD2.append(tempAD2)
            if args.log == True:   logging.info(f'Listen Länge von listTempAD2 = {len(listTempAD2)}')
        if AD3_In == True:
            listTempAD3.append(tempAD3)
            if args.log == True:   logging.info(f'Listen Länge von listTempAD3 = {len(listTempAD3)}')
        listTiRe.append(dt)
        if args.log == True:   logging.info(f'Listen Länge von listTiRe = {len(listTiRe)}')
        if args.log == True:   logging.info('Messwerte in Listen geschrieben') 

    # Wenn ein Rezept vorliegt, so wird dieser Teil ausgeführt:
    if Config == True:                                                                          # Wenn der Config Modus aktiv ist, so wird ein Rezept/ Ablauf aus einer Textdatei abgespielt
        Area = float(TempArea[loop])
        Time = int(TempTime[loop])
        Soll = float(TempTrep[loop])
        lenght = len(TempTrep)                                                                  # Um das Ende des Ablaufes zu erkennen
        jetzt =  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')                          # aktuelle Zeit

        if tempPt == '' or tempHp == '' or tempPt == 0 or tempHp == 0:                          # Anpassung übrspringen wenn
            print('Keine Emissionsgrad-Anpassung')
            if args.log == True:   logging.info('Emissionsgrad-Anpassung übersprungen!')
        else:
            if (Soll + Area) < tempPt or (Soll - Area) > tempPt:                                # Solange der Istwert außerhalb des Bereiches ist, ...                                                             # ... wird StartConfig auf False gesetzt
                if StartConfig == True:
                    with open(Folder + '/' + FileOutNameE,"a", encoding="utf-8") as foE:        # Wenn der Bereich verlsassen wird, soll dies gemerkt erden
                        foE.write(f'- - - Außerhalb des Bereiches - {jetzt} - - -\n\n')         # Alle Emissionsgrade wieder auf 100 %
                        if args.log == True:   logging.info('Außerhalb des gegeben Temperaturbereiches - Emissionsgrade auf 100 %') 
                        if py1_In == True:                                                      # Pyrometer Kw wird zurückgesetzt, wenn da
                            Write_Pyro_Para(0, 'e', 100)
                            e_py1 = 100
                            e_Drauf1 = 100
                        if py2_In == True:                                                      # Pyrometer Lw 20:1 wird zurückgesetzt, wenn da
                            Write_Pyro_Array_Para(0, 'e', 100)
                            e_py2 = 100
                            e_Drauf2 = 100
                        if py3_In == True:                                                      # Pyrometer Lw 10:1 wird zurückgesetzt, wenn da
                            Write_Pyro_Array_Para(1, 'e', 100)
                            e_py3 = 100
                            e_Drauf3 = 100                                                      # Werte zurücksetzen
                Emis_Update()                                                                   # Der Emissionsgrad wird aus dem Gerät gelesen und in eine Liste getan
                StartConfig = False
            else:
                if StartConfig == False:                                                        # Das in der if-Abfrage soll nur einmal ausgeführt werden und dann so bleiben. solange der Bereich aktiv ist, verlässt die Isttemperatur den Bereich werden die Zeiten geändert!
                    starttimeConfig = datetime.datetime.now()                                   # Startzeit - Bereich erreicht
                    min = datetime.timedelta(minutes=Time)                                      # Wie lange muss die Kurve in dem Bereich bleiben
                    nextTempIn = str(starttimeConfig + min).split('.')[0]                       # Berechne Endzeit und erzeuge String, lässt das Datum dran! (die Nachkommerstellen der Sekunden werden abgetrennt)
                    print(f'Nächster Loop voraussichtlich um {nextTempIn.split(" ")[1]} Uhr am {nextTempIn.split(" ")[0]}!')           
                    if args.log == True:   logging.info('Beginn der Zeitmessung + Emissionsgrad ') 
                    with open(Folder + '/' + FileOutNameE,"a", encoding="utf-8") as foE:
                        foE.write(f'- - - Nächster Loop voraussichtlich um {nextTempIn.split(" ")[1]} Uhr am {nextTempIn.split(" ")[0]}! - - -\n')
                        foE.write(f'- - - Zyklus {loop + 1} - {Soll} °C - - -\n')
                    nEMess = 0                                                                  # durch die Null werden 16 Werte aufgenommen
                    StartConfig = True                                                          # Verriegelung, soll nur einmal beim erreichen ausgelöst werden, die zeitberechnung (oder wenn er mal ausgetreten ist) 
                
                # Emissionsgrad Anpassung - Ziel Temp.Oberfläche = Temp.Pyro:
                if nEMess <= 15:                                                                # das soll nur 16 mal durchgeführt werden, da die Rundung nah 10 - 13 durchgängig keine Änderung mehr bringt 
                    with open(Folder + '/' + FileOutNameE,"a", encoding="utf-8") as foE:        # fehler werte anfangen!
                        foE.write(f'{time_abs:<15}{dt:<15.1f}')
                        if py1_In == True:                                                             # Wenn Prometer Initialisiert ist und ausgewählt ist, dann wird der Emissionsgrad 16 mal angepasst, dies geschieht in der Funktion systematisch
                            e_py1, e_Drauf1 = Emissions_Anpassung(tempPyKw, tempVergleich, e_py1, e_Drauf1, 100, 5)       # Achtung Vergleichspartner müssen auch Initialisiert werden, besonders der AD3!             
                            Write_Pyro_Para(0, 'e', e_py1)
                            foE.write(f'{e_py1:<35}')
                        if py2_In == True:
                            e_py2, e_Drauf2 = Emissions_Anpassung(tempPyLw, tempVergleich, e_py2, e_Drauf2, 100, 10) 
                            Write_Pyro_Array_Para(0, 'e', e_py2)
                            foE.write(f'{e_py2:<35}')
                        if py3_In == True:
                            e_py3, e_Drauf3 = Emissions_Anpassung(tempPyLw2, tempVergleich, e_py3, e_Drauf3, 100, 10)
                            Write_Pyro_Array_Para(1, 'e', e_py3)
                            foE.write(f'{e_py3:<35}')
                        foE.write('\n')
                        nEMess += 1
                    if nEMess == 15:                                                                       # Speichere die endgültigen Emissionsgrade
                        with open(Folder + '/' + FileOutNameEEnd,"a", encoding="utf-8") as foEE:
                            foEE.write(f'{Soll:<25}')
                            foEE.write(f'{tempVergleich:<35.1f}')
                            if py1_In == True:                                                             # Wenn Prometer Initialisiert ist und ausgewählt ist, dann wird der Emissionsgrad 15 mal angepasst, dies geschieht in der Fnktion systematisch
                                foEE.write(f'{e_py1:<35}')
                            if py2_In == True:
                                foEE.write(f'{e_py2:<35}')
                            if py3_In == True:
                                foEE.write(f'{e_py3:<35}')
                            foEE.write('\n')
                Emis_Update()                                                                              # Der Emissionsgrad wird aus dem Gerät gelesen und in eine Liste getan
                      
                # Prüfen ob der nächste Rezept-Zyklus Starten soll:
                if jetzt >= nextTempIn:                                                         # Vergleicht die beiden Zeiten
                    with open(Folder + '/' + FileOutNameE,"a", encoding="utf-8") as foE:
                        foE.write(f'- - - Zyklus {loop +1} abgeschlossen - - -\n')
                    if loop == (lenght-1):                                                      # bei erreichen des Endes wird das Programm beendet!
                        endtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        print()
                        with open(Folder + '/' + FileOutNameE,"a", encoding="utf-8") as foE:
                            foE.write(f'- - - Rezept ist abgeschlossen! - {endtime} - - -\n')
                            if args.log == True:   logging.info('Rezept abgeschlossen') 
                        Stop()                                                                  # Stoppt Heizung und ...
                        if Stop_Graph == True and args.nogra == False:
                            figureEnd = plt.figure(figsize=(12,9))                                                # Fenster Größe des Diagrammes
                            figureEnd.suptitle("Temperatur + Emissionsgrad Messungen",fontsize=25)
                            # Linie PT1000
                            ax1End = plt.subplot(221)                                                              # Erzeugt ersten Teilgraph
                            line1End, = ax1End.plot(listTiRe, listTempPt, 'r', label='Pt1000')          
                            plt.ylabel("Temperatur Pt1000 in °C",fontsize=12)
                            plt.legend(loc='best') 
                            plt.grid()
                            # Linie Heizplatte
                            ax2End = plt.subplot(223)                                                              # erzeugt zweiten Teilgraph
                            line2End, = ax2End.plot(listTiRe, listTempHp)          
                            plt.xlabel("Zeit in s",fontsize=12)                                                 # Haben gemeinsame x-Achse
                            plt.ylabel("Temperatur Heizplatte in °C",fontsize=12)
                            plt.grid()
                            # Linie Pyrometer
                            if len(listPy) >= 1:
                                ax3End = plt.subplot(222)                                                   
                                if py1_In == True:                                                              # Pyrometer Kurzwellig
                                    line3End, = ax3End.plot(listTiRe, listTempPyKw, 'b', label='Py - Kurzwellig')                    
                                if py2_In == True:                                                              # Pyrometer langwellig 20:1
                                    line4End, = ax3End.plot(listTiRe, listTempPyLw, 'r', label='Py - Langwellig 20:1') 
                                if py3_In == True:                                                              # Pyrometer langwellig 10:1
                                    line5End, = ax3End.plot(listTiRe, listTempPyLw2, 'g', label='Py - Langwellig 10:1') 
                                if AD1_In == True:                                                              # Adafruit PT100 Nr 1
                                    line6End, = ax3End.plot(listTiRe, listTempAD1, 'm', label=sAD1) 
                                if AD2_In == True:                                                              # Adafruit PT100 Nr 2
                                    line7End, = ax3End.plot(listTiRe, listTempAD2, 'k', label=sAD2) 
                                if AD3_In == True:                                                              # Adafruit PT100 Nr 3
                                    line8End, = ax3End.plot(listTiRe, listTempAD3, 'c', label=sAD3) 
                                if py4_In == True:                                                              # Pyrometer Kurzwellig
                                    line9End, = ax3End.plot(listTiRe, listTempPyKw2, 'purple', label='Py - Kurzwellig Quo.')          
                                plt.ylabel("Temperatur in °C",fontsize=12)
                                plt.legend(loc='best')                                                          # erzeugt eine Legende am möglichst passendenden Ortes (passt sich automatisch an!)
                                plt.grid()
                            # Linie Emissionsgrad:
                            if Config == True:
                                ax4End = plt.subplot(224)
                                if py1_In == True:                                                                    # Pyrometer Kurzwellig
                                    lineE1End, = ax4End.plot(listTiRe, listEmisPyKw, 'b', label='Py - Kurzwellig')                          
                                if py2_In == True:                                                                    # Pyrometer langwellig 20:1
                                    lineE2End, = ax4End.plot(listTiRe, listEmisPyLw, 'r', label='Py - Langwellig 20:1') 
                                if py3_In == True:                                                                    # Pyrometer langwellig 10:1
                                    lineE3End, = ax4End.plot(listTiRe, listEmisPyLw2, 'g', label='Py - Langwellig 10:1')           
                                plt.ylabel("Emissionsgrad in %",fontsize=12)
                                plt.xlabel("Zeit in s",fontsize=12) 
                                plt.legend(loc='best')                                                          # erzeugt eine Legende am möglichst passendenden Ortes (passt sich automatisch an!)
                                plt.grid()
                            plt.show()
                            NameDia = FileOutName.split('.')[0] + '_Bild_Rezept_End.png'        # das .txt wird vom Datennamen abgeschnitten und dann mit einem Bild-Datei-Ende versehen
                            figureEnd.savefig(Folder + '/' + NameDia)                              # speichert den Graf im Verzeichnis!
                            print ('Output data: ', NameDia)   
                        quit()                                                                  # ... beendet Programm!
                    loop += 1                                                                   # Wenn gleich wird der Loop erhöht
                    change_SollTemp(TempTrep[loop])
                    if args.log == True:   logging.info('Nächster Zyklus')      
    
    # Anpasung außerhalb des Rezept-Modus: (Gibt es zweimal - dürfen aber nicht zusammen an sein)
    # Emissionsgrad Anpassung - Ziel Temp.Oberfläche = Temp.Pyro:
    if Press_Anpass == True:
        if tempPt == '' or tempHp == '' or tempPt == 0 or tempHp == 0:                                          # Anpassung übrspringen wenn
            print('Keine Emissionsgrad-Anpassung')
            if args.log == True:   logging.info('Emissionsgrad-Anpassung übersprungen!')
        else:
            if nEMess <= 15:                                                                                    # das soll nur 16 mal durchgeführt werden, da die Rundung nah 10 - 13 durchgängig keine Änderung mehr bringt 
                with open(Folder + '/' + FileOutNameE,"a", encoding="utf-8") as foE:                            
                    foE.write(f'{time_abs:<15}{dt:<15.1f}')
                    if py1_In == True:                                                                          # Wenn Prometer Initialisiert ist und ausgewählt ist, dann wird der Emissionsgrad 16 mal angepasst, dies geschieht in der Funktion systematisch
                        e_py1, e_Drauf1 = Emissions_Anpassung(tempPyKw, tempVergleich, e_py1, e_Drauf1, 100, 5) # Achtung Vergleichspartner müssen auch Initialisiert werden, besonders der AD3!             
                        Write_Pyro_Para(0, 'e', e_py1)
                        foE.write(f'{e_py1:<35}')
                    if py2_In == True:
                        e_py2, e_Drauf2 = Emissions_Anpassung(tempPyLw, tempVergleich, e_py2, e_Drauf2, 100, 10) 
                        Write_Pyro_Array_Para(0, 'e', e_py2)
                        foE.write(f'{e_py2:<35}')
                    if py3_In == True:
                        e_py3, e_Drauf3 = Emissions_Anpassung(tempPyLw2, tempVergleich, e_py3, e_Drauf3, 100, 10)
                        Write_Pyro_Array_Para(1, 'e', e_py3)
                        foE.write(f'{e_py3:<35}')
                    foE.write('\n')
                    nEMess += 1
                if nEMess == 15:                                                                                # Speichere die endgültigen Emissionsgrade
                    with open(Folder + '/' + FileOutNameEEnd,"a", encoding="utf-8") as foEE:
                        Soll = tempPt
                        foEE.write(f'{Soll:<25}')
                        foEE.write(f'{tempVergleich:<35.1f}')
                        if py1_In == True:                                                                     # Wenn Prometer Initialisiert ist und ausgewählt ist, dann wird der Emissionsgrad 15 mal angepasst, dies geschieht in der Fnktion systematisch
                            foEE.write(f'{e_py1:<35}')
                        if py2_In == True:
                            foEE.write(f'{e_py2:<35}')
                        if py3_In == True:
                            foEE.write(f'{e_py3:<35}')
                        foEE.write('\n')
    
    if Config == False:                                                                                        # Im Manuellen Modus werden hier die Listen erweitert! --> Überlege ob das reichen würde für beide!!
        if tempPt == '' or tempHp == '' or tempPt == 0 or tempHp == 0:
            if args.log == True:   logging.info('Emissionsgrad nicht in Liste geschrieben!')
        else:
            Emis_Update() 

    # File wird erneut geöffnet und dann mit den Daten belegt:
    if nStart == True:                                                                 # nStart = True bedeutet das diese Funktion erts nach Betätigung des Start Buttons funktionieren sollen!
        with open(Folder + '/' + FileOutName,"a", encoding="utf-8") as fo:
                time_abs = datetime.datetime.now().strftime('%H:%M:%S')
                if dt == '':
                    print('Nichts in Datei eingetragen!')                              # Fehler Nachricht
                else:                                                                                       # Diese Zeilen mal beobachten!!
                    fo.write(f"{time_abs:<15}{dt:<20.1f}{tempHp:<22.1f}{tempPt:<22.1f}")
                    if py1_In == True:                                          
                        fo.write(f"{tempPyKw:<28.1f}")
                    if py2_In == True:
                        fo.write(f"{tempPyLw:<35.1f}")
                    if py3_In == True:
                        fo.write(f"{tempPyLw2:<35.1f}")
                    if py4_In == True:
                        fo.write(f"{tempPyKw2:<35.1f}")
                    if AD1_In == True:                                              
                        fo.write(f"{tempAD1:<35.1f}")
                    if AD2_In == True:
                        fo.write(f"{tempAD2:<35.1f}")
                    if AD3_In == True:
                        fo.write(f"{tempAD3:<35.1f}")
                    fo.write('\n')
                if args.log == True:   logging.info('File wird mit Messwerten erweitert') 
                    
    if not args.nogra and not Stop_Graph:                           # Wenn True soll keine Grafik erzeugt werden oder wenn der Knopf "Graph I/O" auf True steht, soll es nicht ausgeführt werden
        # Update des Diagrammes:
        if nStart == True:
            # Autoscaling:
            if tempPt == '' or tempHp == '' or tempPt == 0 or tempHp == 0:                  # bei Fehler muss das übersprungen werden da die Listen durch z sonst nicht mehr gelesen werden können, da ein Eintrag fehlt!!
                print('Autoscroll pausiert!')                                               # Fehler Nachricht
            else:
                AutoScroll(ax1, AutoStop_Pt, xVonPt, xBestPt, yVonPt, yBestPt, 2, 2)        # Pt1000
                AutoScroll(ax2, AutoStop_Hp, xVonHp, xBestHp, yVonHp, yBestHp, 10, 20)      # Heizplatte 
                if len(listPy) >= 1: 
                    AutoScroll(ax3, AutoStop_Py, xVonPy, xBestPy, yVonPy, yBestPy, 1, 5)    # Pyrometer           
                AutoScroll(ax4, False, 0, 101, 0, 1000, 1, 1)    # Emissionsgrad (AutoScroll aus nicht vorhanden - 4 Werte nach False egal)
                
            # https://www.delftstack.com/de/howto/matplotlib/how-to-automate-plot-updates-in-matplotlib/ 
            # Diese Seite wurde genutzt zur Bearbeitung der Grafischen Live Auswertung!
            # Update:
            # Grafik - Temperaturmesser in Heizplatte
            
            Update_Graph(line1, listTempPt)             # PT1000
            Update_Graph(line2, listTempHp)             # Heizplatte
       
            # Grafik Pyrometer
            if len(listPy) >= 1:
                if py1_In == True:                      # Pyrometer Kw
                    Update_Graph(line3, listTempPyKw)

                if py2_In == True:                      # Pyrometer Lw 20:1
                    Update_Graph(line4, listTempPyLw)

                if py3_In == True:                      # Pyrometer Lw 10:1
                    Update_Graph(line5, listTempPyLw2) 
                
                if AD1_In == True:                      # Adafruit PT100 1
                    Update_Graph(line6, listTempAD1)
                
                if AD2_In == True:                      # Adafruit PT100 2
                    Update_Graph(line7, listTempAD2)

                if AD3_In == True:                      # Adafruit PT100 3
                    Update_Graph(line8, listTempAD3)
                
                if py4_In == True:                      # Pyrometer Kw2 - Quotientenpyrometer 
                    Update_Graph(line9, listTempPyKw2)
                
            # Grafik Emissionsgrad:
            if py1_In == True:
                Update_Graph(lineE1, listEmisPyKw)
            if py2_In == True:
                Update_Graph(lineE2, listEmisPyLw)
            if py3_In == True:
                Update_Graph(lineE3, listEmisPyLw2)
        
            if args.log == True:   logging.info('Draw figure!')       # Aktualisiere die Grafik
            figure.canvas.draw()            
            figure.canvas.flush_events()
            if args.log == True:   logging.info('Diagramme werden geupdatet')
        
######################################################################################################################
def Update_Graph(Kurve, Update_Y):                                                                                   # Funktion für das Updaten der Kurven
######################################################################################################################
    updated = Update_Y
    Kurve.set_xdata(listTiRe)               
    Kurve.set_ydata(updated)

######################################################################################################################
def AutoScroll(Graph, AutoStop, xVon, xEnde, yVon, yEnde, minusY, plusY):                                            # Funktion für das Autosrollen
######################################################################################################################
    if args.log == True:   logging.info('Autoscroll')
    if AutoStop == False:                                     # Autoscrollen ist aktiv
            Graph.axis('auto')                                # Schaltet Autoscaling wieder ein!
            Graph.relim()                                     # recompute the ax.dataLim
            ymin, ymax = Graph.get_ylim()                     # holt den max. und min. Wert aus dem jeweiligen Diagramm und ...
            Graph.set_ylim(ymin - minusY, ymax + plusY)       # ... setzt die neuen Grenzen für die Y-Achse und ...
            Graph.set_xlim(0,listTiRe[-1] + 10)               # ... X-Achse (mit dem Plus und Minus, kann man Abstände zu den Achsen erstellen)
            #Graph.autoscale_view()                            # update ax.viewLim using the new dataLim (Die Zeile scheint nicht umbedingt bebraucht zu werden)
    elif AutoStop == True:                                    # Autoscrollen wurde deaktiviert
            Graph.axis([xVon,xEnde,yVon,yEnde])               # Übernimmt die Werte des Manuellen Anpassen der Achsen!

######################################################################################################################
def Emissions_Anpassung(Temp_Pyro, Temp_Oberf, e_Alt, e_Drauf, o_Grenze, u_Grenze):                                  # Funktion für das Emissionsgrad bestimmen
######################################################################################################################
    
    if Temp_Pyro != Temp_Oberf:                               # Wenn die Werte gleich sind, soll der Emissionsgrad bleiben wir er ist
        e_Drauf = e_Drauf/2
    if Temp_Oberf > Temp_Pyro:                                # Wenn die Oberflächentempratur größer als die des Pyrometrs ist, so ...
        e_Alt = round(e_Alt - e_Drauf,1)                      # ... wird der Emissionsgrad kleiner
        if e_Alt < u_Grenze:
            e_Alt = u_Grenze
            e_Drauf = e_Drauf * 2               # Weiß noch nicht!
    if Temp_Oberf < Temp_Pyro:                                # Wenn Pyrometer Temperatur größer ist als die der Oberfläche, dann ...
        e_Alt = round(e_Alt + e_Drauf,1)                      # ... wird der Emissionsgrad größer
        if e_Alt > o_Grenze:
            e_Alt = o_Grenze
            e_Drauf = e_Drauf * 2
    e_Neu = e_Alt                                             # wenn die Temperaturen gleich sind, so wird der Alte_Wert zurückgegeben, sonst der neu berechnete!
    return e_Neu, e_Drauf

#################################################################################################################
def Emis_Update():
#################################################################################################################
        # Emissionsgrad in Listen eintragen:
        # Ist in einer Funktion da es an zwei Stellen (einmal im if und dann noch im else) aufgerufen werden muss
        # Während eines Rezeptes soll in jeder Sekunde der Emissionsgrad ausgelesen werden
        # auch im Letzten Durchgang bevor das Programm beendet wird auch!
        if py1_In == True:                                          
            emisKw = Get_Pyro_Para(0, 'e')
            if args.log == True:   logging.info(f'Messwert Emissionsgrad Pyrometer Kw = {emisKw}')
            listEmisPyKw.append(emisKw)
            if args.log == True:   logging.info(f'Listen Länge von listEmisPyKw = {len(listEmisPyKw)}')
        if py2_In == True:
            emisLw = Get_Pyro_Array_Para(0, 'e')
            if args.log == True:   logging.info(f'Messwert Emissionsgrad Pyrometer Lw 20:1 = {emisLw}')
            listEmisPyLw.append(emisLw)
            if args.log == True:   logging.info(f'Listen Länge von listEmisPyLw = {len(listEmisPyLw)}')
        if py3_In == True:
            emisLw2 = Get_Pyro_Array_Para(1, 'e')
            if args.log == True:   logging.info(f'Messwert Emissionsgrad Pyrometer Lw 10:1 = {emisLw2}')
            listEmisPyLw2.append(emisLw2)
            if args.log == True:   logging.info(f'Listen Länge von listEmisPyLw2 = {len(listEmisPyLw2)}')
        if args.log == True:   logging.info('Messwerte in Listen für Emissionsgrad geschrieben')  

###########################################################################  
def save():                                                               # Funktion zum Zwischen Speichern der Bilder             
###########################################################################  
    if args.log == True:   logging.info('Save-Button betätigt')
    if not args.nogra:                                            # Wenn True soll keine Grafik erzeugt werden
        if nStart == True:                                                    # Soll nur nach dem Start funkionieren (vorher hat es nur eine Fehler Meldung ausgegeben - aber kein Ansturz)
            SaveOutIndex = str(1).zfill(2)
            # Grafik Heizplatte und Pt1000:
            SNameHP = ''
            SNameHP = FileOutName.split('.')[0] + '_Bild_#' + SaveOutIndex + '.png'
                    
            # Speichere das Heizplatte und Pt1000 Bild:
            j = 1
            while os.path.exists(Folder + '/' + SNameHP) :
                j = j + 1
                SaveOutIndex = str(j).zfill(2)
                SNameHP = FileOutName.split('.')[0] + '_Bild_#' + SaveOutIndex + '.png'
            print ('Output data: ', SNameHP)             
            figure.savefig(Folder + '/' + SNameHP)              # speichert den Graf im Arbeitsverzeichnis!
            if args.log == True:   logging.info('Diagramm gespeichert')
                       
###########################################################################
def Start():                                                              # Befehl zum Starten der Hardware + Der Plot wird erzeugt und nach erstmaligen Start auch der File neu erstellt
###########################################################################
    global  time_start, nStart, figure, figure1, figure2, line1, line2, line3, line4, line5, line6, line7, line8, line9, lineE1, lineE2, lineE3, ax1, ax2, ax3, ax4, PyroKw_Init, PyroKw2_Init, PyroLw_Init, PyroLw_Config, PyroLw2_Config, AD1_Init, AD2_Init, AD3_Init, listPy
    
    if nStart == False:                                         # Soll verhindern das eine neue Grafik bei mehreren Drücken von Start aufgeht! - Verriegellung bis Stopp gedrückt wird oder Beenden
        # File erzeugen:
        Init_File()
        
        # Variablen:
        time_start = datetime.datetime.now()
        nStart = True
        
        # Liste für Anzahl Messgeräte initialisieren
        listPy = []                                                                 # Pyrometer Liste

        # Hardware starten:
        Start_Heizung()                                                             # Start für die Heizplatte
        if args.log == True:   logging.info('Heizung Ein') 

        # Pyrometer Kurzwellig Initialiesieren:
        if py1_In == True:
            if PyroKw_Init == False:                                                # Die Initialisierung wird nur einmal durhgeführt
                Init_Pyro(0, comKw, 115200, 8, 1,"E", args.debug, args.test)
                Config_Pyro(0,100,100)
                Write_Pyro_Para(0, 't90', '7')
                e_py1 = 100
                PyroKw_Init = True
                if args.log == True:   logging.info('Pyrometer Kw Initialisiert') 
            if 'PyKw' not in listPy:                                                # Wenn das Gerät noch nicht in die Messgeräte Liste aufgenommen wurde, so wird dies nun getan
                listPy.append('PyKw')
        elif py1_In == False and len(listPy) >= 1:
            if 'PyKw' in listPy:                                                    # Wenn das Häckchen entwernt wird, soll das Messgerät nur entfernt werden, wenn es schon drinnen ist
                listPy.remove('PyKw')

        # Pyrometer Langwellig Initialiesieren:                                     (man könnte das noch in einer Funktion zusammenfassen!)
        if py2_In == True:
            if PyroLw_Init == False:                                                # Die Initialisierung wird nur einmal durhgeführt
                Init_Pyro_Array(comLw, 19200, 8, 1,"E", args.debug, args.test)
                PyroLw_Init = True
                if args.log == True:   logging.info('Pyrometer Lw Initialisiert') 
            if PyroLw_Config == False:                                              # Config wird nur einmal ausgelöst, so wird nach einem Stopp die letzte Eingabe für den Emissionsgrad beibehalten und nicht wieder auf 100 % gesetzt!
                Config_Pyro_Array(0,100)
                e_py2 = 100
                PyroLw_Config = True
                if args.log == True:   logging.info('Pyrometer Lw 20:1 im Betrieb') 
            if 'PyLw' not in listPy:                                                # Wenn das Gerät noch nicht in die Messgeräte Liste aufgenommen wurde, so wird dies nun getan
                listPy.append('PyLw')
        elif py2_In == False and len(listPy) >= 1:                  
            if 'PyLw' in listPy:                                                    # Wenn das Häckchen entwernt wird, soll das Messgerät nur entfernt werden, wenn es schon drinnen ist
                listPy.remove('PyLw')

        # Pyrometer Langwellig 2 Initialiesieren:
        if py3_In == True:
            if PyroLw_Init == False:                                                # Die Initialisierung wird nur einmal durhgeführt
                Init_Pyro_Array(comLw, 19200, 8, 1,"E", args.debug, args.test)
                PyroLw_Init = True
                if args.log == True:   logging.info('Pyrometer Lw Initialisiert') 
            if PyroLw2_Config == False:                                             # Config wird nur einmal ausgelöst, so wird nach einem Stopp die letzte Eingabe für den Emissionsgrad beibehalten und nicht wieder auf 100 % gesetzt!
                Config_Pyro_Array(1,100)
                e_py3 = 100
                PyroLw2_Config = True
                if args.log == True:   logging.info('Pyrometer Lw 10:1 im Betrieb') 
            if 'PyLw2' not in listPy:                                               # Wenn das Gerät noch nicht in die Messgeräte Liste aufgenommen wurde, so wird dies nun getan
                listPy.append('PyLw2')
        elif py3_In == False and len(listPy) >= 1:                  
            if 'PyLw2' in listPy:                                                   # Wenn das Häckchen entwernt wird, soll das Messgerät nur entfernt werden, wenn es schon drinnen ist
                listPy.remove('PyLw2')

        # Pyrometer Kurzwellig 2 (Quotientenpyrometer) Initialiesieren:
        if py4_In == True:
            if PyroKw2_Init == False:                                                # Die Initialisierung wird nur einmal durhgeführt
                Init_Pyro(1, comKw2, 115200, 8, 1,"E", args.debug, args.test)
                Config_Pyro(1,100,100)
                #Write_Pyro_Para(1, 't90', '7')
                e_py4 = 100
                PyroKw2_Init = True
                if args.log == True:   logging.info('Pyrometer Kw2 Initialisiert') 
            if 'PyKw2' not in listPy:                                                # Wenn das Gerät noch nicht in die Messgeräte Liste aufgenommen wurde, so wird dies nun getan
                listPy.append('PyKw2')
        elif py4_In == False and len(listPy) >= 1:
            if 'PyKw2' in listPy:                                                    # Wenn das Häckchen entwernt wird, soll das Messgerät nur entfernt werden, wenn es schon drinnen ist
                listPy.remove('PyKw2')

        #Adafruit PT100 Initialisieren:                                            (man könnte das noch in einer Funktion zusammenfassen!)
        # 1
        if AD1_In == True:
            if AD1_Init == False:                                                  # Die Initialisierung wird nur einmal durhgeführt
                Init_Adafruit(0, args.debug, args.test, board.D16, 100, 430, 4)
                AD1_Init = True
                if args.log == True:   logging.info('Pt100 - Adfruit 1 Initialisiert') 
            if 'AD1' not in listPy:                                                # Wenn das Gerät noch nicht in die Messgeräte Liste aufgenommen wurde, so wird dies nun getan
                listPy.append('AD1')
        elif AD1_In == False and len(listPy) >= 1:                  
            if 'AD1' in listPy:                                                    # Wenn das Häckchen entwernt wird, soll das Messgerät nur entfernt werden, wenn es schon drinnen ist
                listPy.remove('AD1')
        # 2
        if AD2_In == True:
            if AD2_Init == False:                                                  # Die Initialisierung wird nur einmal durhgeführt
                Init_Adafruit(1, args.debug, args.test, board.D24, 100, 430, 4)
                AD2_Init = True
                if args.log == True:   logging.info('Pt100 - Adfruit 2 Initialisiert') 
            if 'AD2' not in listPy:                                                # Wenn das Gerät noch nicht in die Messgeräte Liste aufgenommen wurde, so wird dies nun getan
                listPy.append('AD2')
        elif AD2_In == False and len(listPy) >= 1:                  
            if 'AD2' in listPy:                                                    # Wenn das Häckchen entwernt wird, soll das Messgerät nur entfernt werden, wenn es schon drinnen ist
                listPy.remove('AD2')
        # 3
        if AD3_In == True:
            if AD3_Init == False:                                                  # Die Initialisierung wird nur einmal durhgeführt
                Init_Adafruit(2, args.debug, args.test, board.D23, 100, 430, 4)
                AD3_Init = True
                if args.log == True:   logging.info('Pt100 - Adfruit 3 Initialisiert') 
            if 'AD3' not in listPy:                                                # Wenn das Gerät noch nicht in die Messgeräte Liste aufgenommen wurde, so wird dies nun getan
                listPy.append('AD3')
        elif AD3_In == False and len(listPy) >= 1:                  
            if 'AD3' in listPy:                                                    # Wenn das Häckchen entwernt wird, soll das Messgerät nur entfernt werden, wenn es schon drinnen ist
                listPy.remove('AD3')

        if Config == True:
            change_SollTemp(TempTrep[loop])                                        # loop deshalb, weil nach einen Stop so der Aktuelle Rezeptwert eingetragen wird!
        
        if not args.nogra:                                            # Wenn True soll keine Grafik erzeugt werden
            # Grafik Erzeugung:
                # https://www.delftstack.com/de/howto/matplotlib/how-to-automate-plot-updates-in-matplotlib/ 
                # Diese Seite wurde genutzt zur Bearbeitung der Grafischen Live Auswertung!
            plt.ion()
            figure = plt.figure(figsize=(12,9))                                                # Fenster Größe des Diagrammes
            figure.suptitle("Temperatur + Emissionsgrad Messungen",fontsize=25)                 # Erzeugt eine Gesamt Überschrifft
            
            # Linie PT1000
            ax1 = plt.subplot(221)                                                              # Erzeugt ersten Teilgraph
            line1, = ax1.plot(listTiRe, listTempPt, 'r', label='Pt1000')                                                            
            plt.ylabel("Temperatur Pt1000 in °C",fontsize=12)
            plt.legend(loc='best') 
            plt.grid()
            
            # Linie Heizplatte
            ax2 = plt.subplot(223)                                                              # erzeugt zweiten Teilgraph
            line2, = ax2.plot(listTiRe, listTempHp)          
            plt.xlabel("Zeit in s",fontsize=12)                                                 # Haben gemeinsame x-Achse
            plt.ylabel("Temperatur Heizplatte in °C",fontsize=12)
            plt.grid()
            if args.log == True:   logging.info('Diagramm Heizplatte & Pt1000 erstellt') 

            # Linie Pyrometer
            if len(listPy) >= 1:
                ax3 = plt.subplot(222)                                                   
                if py1_In == True:                                                              # Pyrometer Kurzwellig
                    line3, = ax3.plot(listTiRe, listTempPyKw, 'b', label='Py - Kurzwellig')          # durch das Labeln der Kurve kann man eine Legende später erzeugen           
                if py2_In == True:                                                              # Pyrometer langwellig 20:1
                    line4, = ax3.plot(listTiRe, listTempPyLw, 'r', label='Py - Langwellig 20:1') 
                if py3_In == True:                                                              # Pyrometer langwellig 10:1
                    line5, = ax3.plot(listTiRe, listTempPyLw2, 'g', label='Py - Langwellig 10:1') 
                if AD1_In == True:                                                              # Adafruit PT100 Nr 1
                    line6, = ax3.plot(listTiRe, listTempAD1, 'm', label=sAD1) 
                if AD2_In == True:                                                              # Adafruit PT100 Nr 2
                    line7, = ax3.plot(listTiRe, listTempAD2, 'k', label=sAD2) 
                if AD3_In == True:                                                              # Adafruit PT100 Nr 3
                    line8, = ax3.plot(listTiRe, listTempAD3, 'c', label=sAD3) 
                if py4_In == True:                                                              # Pyrometer Kurzwellig
                    line9, = ax3.plot(listTiRe, listTempPyKw, 'purple', label='Py - Kurzwellig Quo.')          
                plt.ylabel("Temperatur in °C",fontsize=12)
                plt.legend(loc='best')                                                          # erzeugt eine Legende am möglichst passendenden Ortes (passt sich automatisch an!)
                plt.grid()
                if args.log == True:   logging.info('Diagramm Pyrometer & Pt100-Adafruit erstellt') 

            # Linie Emissionsgrad:
            ax4 = plt.subplot(224)
            if py1_In == True:                                                                    # Pyrometer Kurzwellig
                lineE1, = ax4.plot(listTiRe, listEmisPyKw, 'b', label='Py - Kurzwellig')                # durch das Labeln der Kurve kann man eine Legende später erzeugen           
            if py2_In == True:                                                                    # Pyrometer langwellig 20:1
                lineE2, = ax4.plot(listTiRe, listEmisPyLw, 'r', label='Py - Langwellig 20:1') 
            if py3_In == True:                                                                    # Pyrometer langwellig 10:1
                lineE3, = ax4.plot(listTiRe, listEmisPyLw2, 'g', label='Py - Langwellig 10:1')           
            plt.ylabel("Emissionsgrad in %",fontsize=12)
            plt.xlabel("Zeit in s",fontsize=12) 
            plt.legend(loc='best')                                                          # erzeugt eine Legende am möglichst passendenden Ortes (passt sich automatisch an!)
            plt.grid()

###########################################################################
def Stop():                                                               # Befehl zum Stoppen der Heizplatte und zum Schließen und Speichern des Bildes/Graphes/Diagrammes
###########################################################################
    global  nStart, anzFehler
    
    # Abschluss Nachricht für *Emis.txt bei Betätigung von Stop oder Beenden
    if nStart == True:                                                                  
        if Config == True:
            with open(Folder + '/' + FileOutNameE,"a", encoding="utf-8") as foE:
                time_of_End = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                foE.write(f'- - - Vorseitig Beenden gedrückt - {time_of_End} - - -\n')
        elif Press_Anpass == True:
            with open(Folder + '/' + FileOutNameE,"a", encoding="utf-8") as foE:
                endtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                foE.write(f'- - - Anpassung ist abgeschlossen! - {endtime} - - -\n')
    
    # Hardware stoppen:
    Stop_Heizung()            # Stopp für die Heizplatte
    if args.log == True:   logging.info('Heizung Aus') 
    
    if not args.nogra:                                            # Wenn True soll keine Grafik erzeugt werden
        # Grafik Speichern und schließen:
        if nStart == True:
            BNameHP = FileOutName.split('.')[0] + '_Bild.png'          # das .txt wird vom Datennamen abgeschnitten und dann mit einem Bild-Datei-Ende versehen
            figure.savefig(Folder + '/' + BNameHP)                     # speichert den Graf im Verzeichnis!
            print ('Output data: ', BNameHP)          
    nStart = False
    print(f'Anzahl der Fehler (Leeren Strings): {anzFehler}') # für den Anwender, am Ende wird die Anzahl an Fehlern, die durch leere Strings verursacht werden ausgeben!

##################################################################################################################################################################################

# Hauptprogramm:
# Variablen voreinstellen:
sampling_Time = 1000    # Abtastrate
#
nStart = False          # Start noch nicht betätigt
Stop_Graph = False
#
PyroKw_Init = False     # Veriegelungen um ein Einmaliges Initialisieren zu gefährleisten!
PyroKw2_Init = False
PyroLw_Init = False
PyroLw_Config = False   # Veriegelungen um ein Einmaliges Configuration zu gefährleisten!   (Kw ist mit in PyroKw_Init verriegelt)
PyroLw2_Config = False
AD1_Init = False        # Veriegelungen für die Adafruit Initialisierung!
AD2_Init = False
AD3_Init = False
Config = False          # Für den Ablauf von Rezepten
Press_Anpass = False
#
Laser = False           # Laser Pyrometer
#
py1_In = False          # Pyrometer 1 - Kw
py2_In = False          # Pyrometer 2 - Lw 20:1
py3_In = False          # Pyrometer 3 - Lw 10:1
py4_In = False          # Pyrometer 4 - Kw 2 Quo.
AD1_In = False          # Adafruits
AD2_In = False
AD3_In = False
# 
anzFehler = 0           # Anzahl Leere Strings

# Konsolen Eingaben - die das Programm beeinflussen:
parser = argparse.ArgumentParser()
parser.add_argument('-test', help='test mode without connected instruments [optional, default=false]', action = 'store_true')                       # Test-Funktion Starten
parser.add_argument('-debug', help='debug mode - Anzeige der Befehle und Daten [optional, default=false]', action = 'store_true')                   # Debug-Funktion Starten
parser.add_argument('-dt', help='sampling steps in miliseconds [optional, default=1000]', type=int, default=1000)                                   # Abtastzeit Default einstellen
parser.add_argument('-solltemp', help='solltemperture in degrees Celsius  [optional, default=0]', type=str)                                         # Sollwerttemperatur voreinstellen
parser.add_argument('-cfg', help='config file name [optional, default="config.ini"]', type=str)                                                     # Config - Rezept straten
parser.add_argument('-nogra', help='the diagramm is not generatet - measurment without diagram [optional, default=false]', action = 'store_true')   # Soll verhindern das eine Grafik erzeugt wird, z.B. Nutzbar wenn man über Nacht es laufen lässt
parser.add_argument('-log', help='logging the events [optional, default=false]', action = 'store_true')                                             # Soll die Events loggen

args = parser.parse_args()
parser.print_help()

# Erstellt eine Log-Datei
if args.log:
    logging.basicConfig(filename='Logging.log', filemode='w', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S')
    # filename estellt eine Datei mit dem Namen
    # filemode='w' - überschriebt die Datei immer wenn Programm neugestartet
    # level=logging.DEBUG - DEBUG ist das niedrigste Level, alles wird geloggt
    # Format - Für den Zeitstempel

if args.dt:
    sampling_Time = args.dt

# Geräte Schnittstelle bestimmen bzw. aus Datei auslesen
Init_com = configparser.ConfigParser()                                             
Init_com.read('Init_Device.txt')                                                # encoding="utf-8" (wenn gebraucht)
for section_name in Init_com.sections():
        if section_name == 'Device':
            for name, comDevice in Init_com.items(section_name):
                if name == 'heizplatte':                                        # müssen im Programm klein geschrieben werden!!!!! programm macht beim Auslesen jeden Buchstaben KLEIN!!
                    comHp = comDevice
                if name == 'pyro.kw':
                    comKw = comDevice
                if name == 'pyro.lw':
                    comLw = comDevice
                if name == 'pyro.kw2':
                    comKw2 = comDevice

# Heizplatte Initialiesieren:
Init_Heizplatte(comHp, 9600, 7, 1, "E", args.debug, args.test)                      # Com Nummer muss man anpassen!
if args.log == True:   logging.info('Heizplatte Initialisiert') 
if not args.test:
    get_SollTemp()                                                                  # Soll Zubeginn des Programmes die Solltemperatur auf dem Konsolenfenster ausgeben!
    get_SaveTemp()                                                                  # Soll Zubeginn des Programmes die Sicherheitstemperatur auf dem Konsolenfenster ausgeben!

# Konsolen Eingabe - Solltemperatur
if args.solltemp:                                                                   # Muss nach Initialisierung der Heizplatte kommen!!
    change_SollTemp(args.solltemp)

# Emissionsgrad Bestimmung - für Anpassung:
e_Drauf1 = 100
e_Drauf2 = 100
e_Drauf3 = 100
e_py1 = 100
e_py2 = 100
e_py3 = 100
nEMess = 0

# Konsolen Eingabe - Rezept - welcher Ablauf soll durchgeführt werden:
if args.cfg:
    Config = True
    StartConfig = False                                                             # Wenn True, dann ist die Temperatur im Bereich!
    loop = 0
    starttimeConfig = ''
    nextTempIn = ''
    TempTrep = []
    TempArea = []
    TempTime = []
    Config_File = args.cfg
    cp = configparser.ConfigParser()
    cp.read(Config_File)
    for section_name in cp.sections():
        if section_name == 'Heating':
             for name, zeile in cp.items(section_name):
                TempTrep.append(zeile.split(',')[0])
                TempArea.append(zeile.split(',')[1])
                TempTime.append(zeile.split(',')[2])
    print('Start des Rezeptes')
    print(TempTrep)
    print(TempArea)
    print(TempTime)
    if args.log == True:   logging.info('Rezept Eingelesen') 

# GUI öffnen: 
fenster_GUI()

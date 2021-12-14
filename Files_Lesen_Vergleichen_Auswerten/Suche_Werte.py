# Suche Werte im temp.txt
# Das Programm sollte die Vergleichstemperaturen für die Emissionsgradanpassung im "*temp.txt" finden. Dies muss es da alte Messreihen im "*Emis_Ende.txt" nur die Solltemperatur 
# beinhalteten und nicht die Oberflächentemperatur die zum Vergleich dient! 
# Das Programm sucht zunächst in der "*Emis.txt" Datei nach den Zeiten wann die 16 Emissionsgradanpassung stattfand. Danach sucht es in der "*temp.txt" Datei nach den Zeiten und 
# notiert sich die Oberflächen-/Vergleichstemperatur (hier die Temperatur vom Adafruit 3). Zuletzt liest das Programm den Kopf und die Werte der Datei "*Emis_Ende.txt" 
# und fügt den Kopf und die Werte in die Datei "*Emis_Ende_Korrekt.txt". Diese kann dann wie die anderen Files von den anderen Programmen gelesen werden.

import os

# Feste Wege müssen hier angegeben werden
pathT = "../Bilder_und_Daten/Daten_vom_2021_10_18_Grafit/2021_10_18_#01_temp.txt"                 # Suchen
pathE = "../Bilder_und_Daten/Daten_vom_2021_10_18_Grafit/2021_10_18_#01_Emis.txt"                 # Suchen
pathEE = "../Bilder_und_Daten/Daten_vom_2021_10_18_Grafit/2021_10_18_#01_Emis_Ende.txt"           # Suchen
pathEEn = "../Bilder_und_Daten/Daten_vom_2021_10_18_Grafit/2021_10_18_#01_Emis_Ende_Korrekt.txt"  # Erstellen - Speicherort
path_List = [pathT, pathE, pathEE]

# Kontrolle ob es Pfad gibt:
for pfad in path_List:
    if not os.path.exists(pfad):                                             # Überprüfe ob es den Pfad schon gibt
        print('Gibt es nicht!')
        quit()                                            
    else:                                                                    # Plot wird nur bei vorhandenen Pfad erzeugt!
        print('Pfad vorhanden!')

#################################################################################################################################################################################
# Listen
Such_Werte = []
tat_temp = []
Betreff = []

# Zählindex
n = 0

# Lese rel. Zeit Werte aus "*Emis.txt":
with open(pathE,'r', encoding="utf-8") as fi:
    for num, line in enumerate(fi, 1):
            if 'abs' in line:
                break
    lines = fi.readlines()                           # lese alle Zeilen ein (alle Zeilen mit Werten, da die ersten übersprungen wurden)
    for line in lines:
        value = line.split()
        if len(value) == 0 or value[0] == '-':      # überspringt wenn Zeile Leer ist oder mit "-" beginnt 
            #print('Keine Zahl!')
            n = 0
        elif n == 15:                               # es gibt 16 Werte die in den File Emis.txt geschrieben wurde, diese brauchen wir hier
            Such_Werte.append(value[1])             # Wert wird in Liste gespeichert
            n = 0
        else:
            n +=1

print(f'\nDie zu suchenden Zeiten sind: \n{Such_Werte}')
print(f'Es sind {len(Such_Werte)} Emissionsgrade!')

#################################################################################################################################################################################

# Zählindex und Boolche Variablen
anz = 3
Kw = False
Lw20 = False
Lw10 = False

# Suche die Vergleichstemperatur anhand der rel. Zeit in "*temp.txt":
with open(pathT,'r', encoding="utf-8") as fi:
    for num, line in enumerate(fi, 1):
            if 'abs' in line:
                if 'Kurzw.' in line:                      # überprüfe welche Geräte es gibt (alles zur Heizplatte ist immer drin)
                    Kw = True
                    anz += 1
                if '20:1' in line:
                    Lw20 = True
                    anz += 1
                if '10:1' in line:
                    Lw10 = True
                    anz += 1
                if 'Adafruit 1' in line:
                    AD1 = True
                    anz += 1
                if 'Adafruit 2' in line:
                    AD2 = True
                    anz += 1
                if 'Adafruit 3' in line:
                    AD3 = True
                    anz += 1
                break
    lines = fi.readlines()                               # lese alle Zeilen ein (alle Zeilen mit Werten, da die ersten übersprungen wurden)
    for line in lines:
        value = line.split()
        for item in Such_Werte:                          # Suche auf Übereinstimmung der Zeitwerte
            if value[1] == item:
                tat_temp.append(value[anz])              # Wenn Vergleich stimmt, notiere Wert!

print(tat_temp)

#################################################################################################################################################################################

# Listen:
Soll = []
PyKw = []
PyLw20 = []
PyLw10 = []

# Liest die Werte und den Kopf der Datei von "*Emis_Ende.txt" aus
with open(pathEE,'r', encoding="utf-8") as fi:
    for line in fi:
        Betreff.append(line)
        if '[%]' in line:
            break
    lines = fi.readlines()                           # lese alle Zeilen ein (alle Zeilen mit Werten, da die ersten übersprungen wurden)
    for line in lines:
        value = line.split()
        Soll.append(value[0])
        i = 1
        if Kw == True:
            PyKw.append(value[i])
            i += 1
        if Lw20 == True:
            PyLw20.append(value[i])
            i += 1
        if Lw10 == True:
            PyLw10.append(value[i])
            i += 1

#################################################################################################################################################################################

# Schreibt eine Korigierte Datei
with open(pathEEn,'w', encoding="utf-8") as fo:
    for item in Betreff:
        if not '[%]' in item:
            fo.write(item)
    fo.write("Soll. Temperatur".ljust(25))
    fo.write("Vergleichs-Temperatur".ljust(35))
    if Kw == True:                                          
        fo.write("Emissionsgrad Py. Kw. [%]".ljust(35))
    if Lw20 == True:
        fo.write("Emissionsgrad Py. Lw. 20:1 [%]".ljust(35))
    if Lw10 == True:
        fo.write("Emissionsgrad Py. Lw. 10:1 [%]".ljust(35))
    fo.write('\n')
    anz_value = len(Such_Werte)
    for k in range(0, anz_value):
        fo.write(f'{Soll[k]:<25}')
        fo.write(f'{tat_temp[k]:<35}')
        if Kw == True:                                                             # Wenn Prometer Initialisiert ist und ausgewählt ist, dann wird der Emissionsgrad 15 mal angepasst, dies geschieht in der Fnktion systematisch
            fo.write(f'{PyKw[k]:<35}')
        if Lw20 == True:
            fo.write(f'{PyLw20[k]:<35}')
        if Lw10 == True:
            fo.write(f'{PyLw10[k]:<35}')
        fo.write('\n')
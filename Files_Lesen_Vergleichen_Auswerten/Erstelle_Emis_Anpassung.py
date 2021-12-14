# Mit dem Programm kann man sich das untere rechte Bild der Live-Grafik erstellen lassen. Hier wird der Verlauf der Emissionsgrade über die Zeit dargestellt. 
# Der Datei Pfad muss im Programm angegeben werden!!

# In der "*temp.txt" stehen alle Zeitpunkte (relative und absolute Zeit) an den gemessen wurde. Wenn diese nicht in der "*Emis.txt" Datei gefunden werden, so wird eine 100 eingesetzt, 
# es sei denn, die Anpassung läuft noch, dann wird der letzte bestimmte Emissionsgrad eingesetzt. Dieses halten funktioniert über die absolute Zeit. 
# Aus der "*Emis.txt" wird auch immer die absolute Zeit, bei der der Bereich verlassen wurde notiert, diese Zeit wird zum halten verwendet. 

# Bibliothek:
import numpy as np                              # Bibliothek für das Arbeiten mit Vektoren usw.
import matplotlib.pyplot as plt                 # Bibliothek für die Ausgabe von Graphen
from matplotlib.widgets import CheckButtons
import os

# Datei-Pfad:
path_temp = '../Bilder_und_Daten/Daten_vom_2021_11_09/2021_11_09_#11_temp.txt'       # Temperaturwerte (bzw. Zeitwerte)
path_Emis = '../Bilder_und_Daten/Daten_vom_2021_11_09/2021_11_09_#11_Emis.txt'       # Emissionsgrade

# Überprüfe ob Pfad vorhanden, wenn nicht beende Programm:
data = [path_temp, path_Emis]

for pfad in data:                               
    path = pfad
    if not os.path.exists(path):                                             # Überprüfe ob es den Pfad schon gibt
        print('Gibt es nicht!')
        quit()                                                               # wenn nicht vorhanden --> Programm Ende                                          
    else:                                                                    # Plot wird nur bei vorhandenen Pfad erzeugt!
        print('Pfad vorhanden!')                                                             

# Listen, Variablen:
# Aus der "*temp.txt" Datei gelesen:
x = []                         # relative Zeit
abs = []                       # absolute Zeit

# Aus der "*Emis.txt" Datei gelesen:
xEmis = []                      # relative Zeit
EmisKw = []                     # Emissionsgrad
EmisLw20 = []                   # Emissionsgrad
EmisLw10 = []                   # Emissionsgrad
halteE = []                     # Absolutezeiten bei Außerhalb der Anpassung

# Liste für Endgültige alle Emissionsgrade (Anpassung, Halten + 100 %)                      
EmisKw_voll = []                # Emissionsgrad
EmisLw20_voll = []              # Emissionsgrad
EmisLw10_voll = []              # Emissionsgrad

i = 0                           # Zählindex Emissionsgrad
j = 0                           # Zählindex absolute Zeit aller Werte ("*temp.txt")                     
k = 0                           # Zählindex absolute Zeit "Außerhalb der Anpassung" ("*Emis.txt")

hold = False                    # Soll der Emissionsgrad gehalten werden (springt dann nicht diereckt auf 100 %)

# Pyrometer Anwesenheit:
Kw = False                      
Lw20 = False
Lw10 = False

#######################################################################################################################################################################

# Auslesen der Datein:
# Lese die "*temp.txt" datei:
with open(path_temp,'r', encoding="utf-8") as fi:
    for num, line in enumerate(fi, 1):
        if 'abs' in line:                             # gehe bis zur Zeile wo die Werte Namen stehen (wofür die folgenden werte stehen)                      
            if 'Kurzw.' in line:                      # überprüfe welche Geräte es gibt, in dem Fall interessieren nur die Pyrometer
                Kw = True
            if '20:1' in line:
                Lw20 = True
            if '10:1' in line:
                Lw10 = True
            break
    lines = fi.readlines()                           # lese alle zeilen ein (alle Zeilen mit Werten, da die ersten übersprungen wurden)
    for line in lines:
        values = line.split()
        abs.append(values[0])                        # absolute Zeiten merken 
        x.append(float(values[1]))                   # relative Zeiten merken

# Lese die "*Emis.txt" Datei:
with open(path_Emis,'r', encoding="utf-8") as fi:
    for num, line in enumerate(fi, 1):
            if 'abs' in line:                        # gehe bis zur Zeile wo der String drin steht
                break
    lines = fi.readlines()                           # lese alle Zeilen ein (alle Zeilen mit Werten, da die ersten übersprungen wurden)
    for line in lines:
        value = line.split()
        if len(value) == 0 or value[0] == '-':      # überspringt wenn Zeile Leer ist oder mit "-" beginnt 
            if '- - - Außerhalb des Bereiches' in line or '- - - Rezept ist abgeschlossen!' in line or '- - - Anpassung ist abgeschlossen!' in line:        # Wenn die Zeile ein Abschluss einer Anpassung ist (diese Strings findet) merke die absolute Zeit in der Zeile
                halteE.append(value[8])             # steht an 8 Stelle
        else:                                   
            xEmis.append(float(value[1]))             # relative Zeiten merken
            n = 2                                     # Zählindex, für das richtige Auslesen der Pyrometer
            if Kw == True:
                EmisKw.append(float(value[n]))        # Emissionsgrad
                n += 1
            if Lw20 == True:
                EmisLw20.append(float(value[n]))      # Emissionsgrad
                n += 1
            if Lw10 == True:
                EmisLw10.append(float(value[n]))      # Emissionsgrad

#######################################################################################################################################################################

# Emissionsgrad Listen vervollständigen:
for time in x:                                                  # gehe alle relativen Zeiten aus "*temp.txt" durch 
    abstime = abs[j]                                            # aktuelle absolute Zeit aus "*temp.txt" holen
    for timeE in xEmis:                                         # gehe alle relativen Zeiten aus "*Emis.txt" durch und ...
        if timeE == time:                                       # ... vergleiche ob diese vorhanden ist
            answer = 'JA'                                       # wenn Ja, merke dies und verlasse for-Schleife
            break
        else:
            answer = 'Nein'                                     # bei Nein suche weiter, wenn nicht gefunden merke dir das Nein

    if answer == 'JA':                                          # Zeit wurde gefunden
        if Kw == True:
            EmisKw_voll.append(EmisKw[i])                       # hänge den Emissionsgrad an Liste
            Kw_aktuell = EmisKw[i]                              # für Emissiongrad Halten merke dir immer den letzten Emissionsgrad
        if Lw20 == True:
            EmisLw20_voll.append(EmisLw20[i])                   # hänge den Emissionsgrad an Liste
            Lw20_aktuell = EmisLw20[i]                          # für Emissiongrad Halten merke dir immer den letzten Emissionsgrad
        if Lw10 == True:
            EmisLw10_voll.append(EmisLw10[i])                   # hänge den Emissionsgrad an Liste
            Lw10_aktuell = EmisLw10[i]                          # für Emissiongrad Halten merke dir immer den letzten Emissionsgrad
        i += 1                                                  # Zählindex um den richtigen Emissionsgrad zu finden 
        hold = True                                             # wenn abgeschlossen setze hold auf True - dadurch wird der letzte Emissionsgrad solange gehalten, bis die absolute Zeit die absolute Zeit des Anpassungsbereiches überläuft
    else:                                                       # Zeit wurde nicht gefunden:
        if hold == True:                                        # Hold ist True, dann ...
            if abstime >= halteE[k]:                            # ... vergleiche die absolute Zeit der "*temp.txt" Datei mit der Außerhalb der Anpassungs- absoluten Zeit aus der "*Emis.txt" Datei
                k += 1                                          # wenn diese überlaufen wurde dann erhöhe den Zählindex der Liste (fürs Halten) und ...
                hold = False                                    # ...setze hold auf False und ...
                if Kw == True:                                  # ...setzte die Emissionsgrade auf 100 % (ohne das wären die Listen zu klein)
                    EmisKw_voll.append(100)
                if Lw20 == True:
                    EmisLw20_voll.append(100)
                if Lw10 == True:
                    EmisLw10_voll.append(100)
            else:                                               # wenn diese noch nicht überlaufen wurde, dann ...
                if Kw == True:                                  # ... schreibe die letzten Emissionsgrade in die Listen
                    EmisKw_voll.append(Kw_aktuell)
                if Lw20 == True:
                    EmisLw20_voll.append(Lw20_aktuell)
                if Lw10 == True:
                    EmisLw10_voll.append(Lw10_aktuell)
        else:                                                   # Ist hold = False, dann ...
            if Kw == True:                                      # ... schreibe 100 % in die Emissionsgrad Listen
                EmisKw_voll.append(100)
            if Lw20 == True:
                EmisLw20_voll.append(100)
            if Lw10 == True:
                EmisLw10_voll.append(100)
    j += 1                                                      # erhöhe den Zählindex für die absolute Zeit aus "*temp.txt"

#######################################################################################################################################################################

# Erzeuge den Plot:
# selber Code wie in "Daten_Einlesen.py" oder "Vergleiche_Emis_Kurven.py" - nur kleinere Anpassungen

Kurven = []

fig, ax = plt.subplots(figsize=(10,6))
if Kw == True:
    l2, = ax.plot(x, EmisKw_voll, 'b', label ='Pyro. Kw')
    Kurven.append(l2)
if Lw20 == True:
    l3, = ax.plot(x, EmisLw20_voll, 'r', label ='Pyro. Lw20:1')
    Kurven.append(l3)
if Lw10 == True:
    l4, = ax.plot(x, EmisLw10_voll, 'g', label ='Pyro. Lw10:1')
    Kurven.append(l4)
plt.legend(bbox_to_anchor=(1.28, 1.02))                           # Legende frei platzieren! - https://www.physi.uni-heidelberg.de/Einrichtungen/AP/python/xyDiagramme.html
plt.title('Emissionsgrad', fontsize=35)
plt.ylabel("Emissionsgrad in %",fontsize=20)
plt.xlabel("Zeit in s",fontsize=20)
plt.tight_layout()                                                # https://www.delftstack.com/de/howto/matplotlib/how-to-place-legend-outside-of-the-plot-in-matplotlib/ 
plt.grid()

# https://matplotlib.org/3.1.0/gallery/widgets/check_buttons.html
# Make checkbuttons with all plotted lines with correct visibility
rax = plt.axes([0.8, 0.2, 0.18, 0.25])
labels = [str(line.get_label()) for line in Kurven]
visibility = [line.get_visible() for line in Kurven]
check = CheckButtons(rax, labels, visibility)

def func(label):
    index = labels.index(label)
    Kurven[index].set_visible(not Kurven[index].get_visible())
    plt.draw()

check.on_clicked(func)

plt.show()
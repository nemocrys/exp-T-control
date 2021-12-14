# Das Programm basiert auf dem Programm "Daten_Einlesen.py"

import numpy as np                              # Bibliothek für das Arbeiten mit Vektoren usw.
import matplotlib.pyplot as plt                 # Bibliothek für die Ausgabe von Graphen
from matplotlib.widgets import CheckButtons
import os

global KurvenE, color_Nr, look

##################################################################################################################################################
def Emis_Plot(Path):
##################################################################################################################################################
    global KurvenE, color_Nr, look

    # Listen:
    values = []

    solltemp =[]
    vergleichstemp = []
    emisKw = []
    emisLw20 = []
    emisLw10 = []

    Line_color = ['b', 'r', 'y', 'g', 'm', 'c', 'k']                             # Liste der Farben 
    Line_Art = ['-', '--', '-.', ':', 'o', 's', 'D', '^', 'x', '*', '+']         # Liste Linien Art (Notiz: Die ersten 4 Arten machen noch Sinn - das wären 28 Kurven, 7 je Art) [durchgezogene Linie, gestrichelte Linie, Strich-Punkt-Linie, gepunktete Linie, Punkt=Kreis, Punkt=Square, Punkt=Diamant, Punkt=Dreieck, Punkt=x, Punkt=*, Punkt=+]

    # Variablen
    Kw = False
    Lw20 = False
    Lw10 = False
    new_Style = False

    # Datei auslesen:
    with open(Path,'r', encoding="utf-8") as fi:
        for num, line in enumerate(fi, 1):
            if '[%]' in line:                            # gehe bis zur Zeile wo die Werte Namen stehen (wofür die folgenden Werte stehen)
                if 'Vergleichs' in line:                 # um die alten Bilder, ohne Vergleichstemperatur Eintrag angeben zu können!
                    new_Style = True
                if 'Kw.' in line:                    
                    Kw = True
                if '20:1' in line:
                    Lw20 = True
                if '10:1' in line:
                    Lw10 = True
                break
        lines = fi.readlines()                           # lese alle zeilen ein (alle Zeilen mit Werten, da die ersten übersprungen wurden)
        for line in lines:
            values = line.split()
            solltemp.append(float(values[0]))            # schreibe die werte in die richtige Liste
            if new_Style == True:                        # um die alten Bilder, ohne Vergleichstemperatur Eintrag angeben zu können!
                vergleichstemp.append(float(values[1]))
                n = 2
            else:
                n = 1
                vergleichstemp = solltemp                # Damit wird die Solltemperatur für die Grafik genommen!
            if Kw == True:
                emisKw.append(float(values[n]))
                n += 1
            if Lw20 == True:
                emisLw20.append(float(values[n]))
                n += 1
            if Lw10 == True:
                emisLw10.append(float(values[n]))

    # Erzeuge die Kurven:
    if Kw == True:
        if color_Nr + 1 > len(Line_color):                                                                                              # Es wird geschaut ob genügend Farben vorhanden sind
            color_Nr = 0                                                                                                                # wenn nicht wird die Liste von vorn begonnen, 
            look += 1                                                                                                                   # aber das Aussehen verändert
        l0, = ax1.plot(vergleichstemp, emisKw, f'{Line_color[color_Nr]}{Line_Art[look]}', label =f'Pyro. Kw - {material}')              # f'{Line_color[color_Nr]}{Line_Art[look]}' das setzt die Farbe mit der Art zusammen z.B. 'r-' oder 'b-.' | Diese Art geht nicht mit den Farben wie 'orange', 'purple', ... da dies vom Programm nicht gelesen werden kann
        KurvenE.append(l0)
        color_Nr += 1
    if Lw20 == True:
        if color_Nr + 1 > len(Line_color):
            color_Nr = 0
            look += 1
        l1, = ax1.plot(vergleichstemp, emisLw20, f'{Line_color[color_Nr]}{Line_Art[look]}', label =f'Pyro. Lw20:1 - {material}')
        KurvenE.append(l1)
        color_Nr += 1
    if Lw10 == True:
        if color_Nr + 1 > len(Line_color):
            color_Nr = 0
            look += 1
        l2, = ax1.plot(vergleichstemp, emisLw10, f'{Line_color[color_Nr]}{Line_Art[look]}', label =f'Pyro. Lw10:1 - {material}')
        KurvenE.append(l2)
        color_Nr += 1

##################################################################################################################################################

# import                                                                                                            # Angabe der Pfade, keine Individuelle Eingabe
data = { #'Grafit'         : '../Bilder_und_Daten/Daten_vom_2021_10_18_Grafit/2021_10_18_#01_Emis_Ende_Korrekt.txt',
         #'Filz_g'         : '../Bilder_und_Daten/Daten_vom_2021_10_19_Filz_g/2021_10_19_#01_Emis_Ende_Korrekt.txt',
         'Filz_g W'       : '../Bilder_und_Daten/Daten_vom_2021_10_20_Filz_g/2021_10_20_#03_Emis_Ende.txt',
         'Grafit W'       : '../Bilder_und_Daten/Daten_vom_2021_10_21_Grafit/2021_10_21_#01_Emis_Ende.txt',
         'Filz_m'         : '../Bilder_und_Daten/Daten_vom_2021_10_22_Filz_m/2021_10_22_#01_Emis_Ende.txt',
         #'Sili-Wafer'     : '../Bilder_und_Daten/Daten_vom_2021_10_25_Sili-W/2021_10_25_#02_Emis_Ende.txt',
         'Sili-Wafer W'   : '../Bilder_und_Daten/Daten_vom_2021_10_26_Sili-W/2021_10_26_#01_Emis_Ende.txt',
         'Emis_Aufkleber' : '../Bilder_und_Daten/Daten_vom_2021_10_27_Emis_A/2021_10_27_#01_Emis_Ende.txt',
         'Filz_nur_Of-m'  : '../Bilder_und_Daten/Daten_vom_2021_10_28_Filz_m/2021_10_28_#01_Emis_Ende.txt',
         'Emis_Auf.-Rolle': '../Bilder_und_Daten/Daten_vom_2021_10_29_Emis_A-R/2021_10_29_#01_Emis_Ende.txt'
        }

# Variablen
KurvenE = []                                                                 # Liste der Linien

color_Nr = 0                                                                 # Farbindex
look = 0                                                                     # Welche Art der Linie gewählt wird 

fig1, ax1 = plt.subplots(figsize=(18,10))                                     # Grafik erzeugen 

for material in data:                               
    path = data[material]
    if not os.path.exists(path):                                             # Überprüfe ob es den Pfad schon gibt
        print('Gibt es nicht!')                                              
    else:                                                                    # Plot wird nur bei vorhandenen Pfad erzeugt!
        print('Pfad vorhanden!')
        Emis_Plot(path)                                                      # Aufruf der Funktion
      
plt.legend(bbox_to_anchor=(1.28, 1.02))                           # Legende frei platzieren! - https://www.physi.uni-heidelberg.de/Einrichtungen/AP/python/xyDiagramme.html
plt.title('Emissionsgrad über Temperatur', fontsize=35)
plt.ylabel("Emissionsgrad in %",fontsize=20)
plt.xlabel("Temperatur in °C",fontsize=20)
plt.tight_layout()                                                # https://www.delftstack.com/de/howto/matplotlib/how-to-place-legend-outside-of-the-plot-in-matplotlib/ 
plt.grid()

# https://matplotlib.org/3.1.0/gallery/widgets/check_buttons.html
# Make checkbuttons with all plotted lines with correct visibility
raxE = plt.axes([0.8, 0.2, 0.18, 0.25])
labelsE = [str(line.get_label()) for line in KurvenE]
visibilityE = [line.get_visible() for line in KurvenE]
checkE = CheckButtons(raxE, labelsE, visibilityE)

def func(label):
    indexE = labelsE.index(label)
    KurvenE[indexE].set_visible(not KurvenE[indexE].get_visible())
    plt.draw()

checkE.on_clicked(func)

plt.show()
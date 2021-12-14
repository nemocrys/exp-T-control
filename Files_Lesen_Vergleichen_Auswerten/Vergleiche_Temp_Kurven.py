# Das Programm basiert auf dem Programm "Daten_Einlesen.py"

import numpy as np                              # Bibliothek für das Arbeiten mit Vektoren usw.
import matplotlib.pyplot as plt                 # Bibliothek für die Ausgabe von Graphen
from matplotlib.widgets import CheckButtons
import os

global Kurven, Line_color, color_Nr, color_len

################################################################################################################################
def Plott_Graph(Pfad, VP):                              # VP - Vergleichspartner
################################################################################################################################
    global Kurven, color_Nr, color_len
    
    # Listen:
    values = []

    # Listen Messwerte
    x = []
    y_PH = []
    y_Hp = []
    y_PyKw = []
    y_PyLw20 = []
    y_PyLw10 = []
    y_AD1 = []
    y_AD2 = []
    y_AD3 = []

    # Variablen:
    Kw = False
    Lw20 = False
    Lw10 = False
    AD1 = False
    AD2 = False
    AD3 = False

    # Datei auslesen:
    with open(Pfad,'r', encoding="utf-8") as fi:
        for num, line in enumerate(fi, 1):
            if 'abs' in line:                             # gehe bis zur Zeile wo die Werte Namen stehen (wofür die folgenden werte stehen)                      
                if 'Kurzw.' in line:                      # überprüfe welche Geräte es gibt (alles zur Heizplatte ist immer drin)
                    Kw = True
                if '20:1' in line:
                    Lw20 = True
                if '10:1' in line:
                    Lw10 = True
                if 'Adafruit 1' in line:
                    AD1 = True
                if 'Adafruit 2' in line:
                    AD2 = True
                if 'Adafruit 3' in line:
                    AD3 = True
                break
        lines = fi.readlines()                           # lese alle Zeilen ein (alle Zeilen mit Werten, da die ersten übersprungen wurden)
        for line in lines:
            values = line.split()
            x.append(float(values[1]))                   # schreibe die Werte in die richtige Liste
            y_Hp.append(float(values[2]))
            y_PH.append(float(values[3]))
            n = 4
            if Kw == True:
                y_PyKw.append(float(values[n]))
                n += 1
            if Lw20 == True:
                y_PyLw20.append(float(values[n]))
                n += 1
            if Lw10 == True:
                y_PyLw10.append(float(values[n]))
                n += 1
            if AD1 == True:
                y_AD1.append(float(values[n]))
                n += 1
            if AD2 == True:
                y_AD2.append(float(values[n]))
                n += 1
            if AD3 == True:
                y_AD3.append(float(values[n]))

    color_len += n                                                                                              # Dadurch sind beliebig viele Kurven möglich, bei zu vielen Kurven wird es aber unübersichtlich!                 
    if color_len > len(Line_color):
        color_len = 0
        color_Nr = 0

    # Linien erstellen
    l0, = ax.plot(x, y_Hp, Line_color[color_Nr], label =f'Heizplatte - VP{VP}')
    color_Nr += 1
    Kurven.append(l0)
    l1, = ax.plot(x, y_PH, Line_color[color_Nr], label =f'PT1000 - Hp - VP{VP}')
    color_Nr += 1
    Kurven.append(l1)
    if Kw == True:
        l2, = ax.plot(x, y_PyKw, Line_color[color_Nr], label =f'Pyro. Kw - VP{VP}')
        color_Nr += 1
        Kurven.append(l2)
    if Lw20 == True:
        l3, = ax.plot(x, y_PyLw20, Line_color[color_Nr], label =f'Pyro. Lw20:1 - VP{VP}')
        color_Nr += 1
        Kurven.append(l3)
    if Lw10 == True:
        l4, = ax.plot(x, y_PyLw10, Line_color[color_Nr], label =f'Pyro. Lw10:1 - VP{VP}')
        color_Nr += 1
        Kurven.append(l4)
    if AD1 == True:
        l5, = ax.plot(x, y_AD1, Line_color[color_Nr], label =f'Adafruit PT100 1 - VP{VP}')
        color_Nr += 1
        Kurven.append(l5)
    if AD2 == True:
        l6, = ax.plot(x, y_AD2, Line_color[color_Nr], label =f'Adafruit PT100 2 - VP{VP}')
        color_Nr += 1
        Kurven.append(l6)
    if AD3 == True:
        l7, = ax.plot(x, y_AD3, Line_color[color_Nr], label =f'Adafruit PT100 3 - VP{VP}')
        color_Nr += 1
        Kurven.append(l7)

################################################################################################################################

# Variablen/Listen/etc.
i = 0                                                                                # Zählindex
color_Nr = 0                                                                         # Farbindex
color_len = 0

path_list = []
Kurven = []                                                                          # Liste der Linien
Line_color = ['b', 'r', 'y', 'grey', 'g', 'm', 'k', 'c', 'orange', 'purple', 'brown', 'pink', 'olive', 'lime', 'darkred', 'crimson', 'gold', 'silver', 'greenyellow', 'orangered', 'skyblue', 'darkmagenta','tomato','turquoise','yellow','navy','darkmagenta','beige','peru']
    # eventuell auf Standard Zyklus wechseln

fig, ax = plt.subplots(figsize=(18,10))                                               # Grafik erzeugen 

while 1:                                                                             # Eingabeaufforderung bis Exit oder Break (E oder N) 
    print(f'\nEingabe für den {i + 1} Vergleichspartner:')
    name = input('Dateiname (ohne Dateiende): ')
    ordner = input('Ordner Pfad (am Ende / setzen): ')
    path = '../Bilder_und_Daten/' + ordner + name + '.txt'

    # Prüfe ob es den Pfad schon gibt:
    while 1:
        print(path)
        Antwort = input('Ist der Pfad richtig? J/N/E: ').upper()                     # Mit namen einverstanden wird abgefragt, E - Ende (Programm wird beendet)
        if Antwort == 'J':
            if not os.path.exists(path):                                             # Überprüfe ob es den Pfad schon gibt
                print('Gibt es nicht!')                                              # wenn nicht wird die Schleife fortgeführt
            else:
                break                                                                # wenn es ihn gibt, so wird der Plot gestartet
        if Antwort == 'E':                                                           # E für Ende
            quit()
        name = input('Dateiname (ohne Dateiende): ')
        ordner = input('Ordner Pfad (am Ende / setzen): ')
        path = '../Bilder_und_Daten/' + ordner + name + '.txt'

    path_list.append(path)                                                           # Pfad wird in Liste gelegt (so kann man den Pfad noch nutzen)

    Plott_Graph(path_list[i], i+1)                                                   # Aufruf der Funktion

    Antwort = input('\nWillst du eine weitere Datei einlesen? J/N: ').upper()        # Bei der Antwort Nein werden keine weiteren Daten aufgenommen/ausgeleen
    if Antwort == 'N':
        break
    i += 1

plt.legend(bbox_to_anchor=(1.28, 1.02))                           # Legende frei platzieren! - https://www.physi.uni-heidelberg.de/Einrichtungen/AP/python/xyDiagramme.html
plt.title('Vergleich der Kurven', fontsize=35)
plt.ylabel("Temperatur in °C",fontsize=20)
plt.xlabel("Zeit in s",fontsize=20)
plt.tight_layout()                                                # https://www.delftstack.com/de/howto/matplotlib/how-to-place-legend-outside-of-the-plot-in-matplotlib/ 
plt.grid()

# https://matplotlib.org/3.1.0/gallery/widgets/check_buttons.html
# Make checkbuttons with all plotted lines with correct visibility
rax = plt.axes([0.8, 0.2, 0.18, 0.25])                                   # [left, bottom, width, height] - Eventuell noch schöner machen!!!!!
labels = [str(line.get_label()) for line in Kurven]
visibility = [line.get_visible() for line in Kurven]
check = CheckButtons(rax, labels, visibility)

def func(label):
    index = labels.index(label)
    Kurven[index].set_visible(not Kurven[index].get_visible())
    plt.draw()

check.on_clicked(func)

plt.show()
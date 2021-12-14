import numpy as np                              # Bibliothek für das Arbeiten mit Vektoren usw.
import matplotlib.pyplot as plt                 # Bibliothek für die Ausgabe von Graphen
from matplotlib.widgets import CheckButtons
import os

# Mit dem Ersten Teil-Programm kann man die Temperaturdaten auslesen lassen!
# Eingabe für Dateinamen und Ordnernamen:
print('Datein liegen in einem Unterordner von "Bilder_und_Daten"! \nDer Ordner Pfad Teil muss nicht mit angegeben werden!!\n')
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

# Listen:
values = []

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
with open(path,'r', encoding="utf-8") as fi:
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
    lines = fi.readlines()                           # lese alle zeilen ein (alle Zeilen mit Werten, da die ersten übersprungen wurden)
    for line in lines:
        values = line.split()
        x.append(float(values[1]))                   # schreibe die werte in die richtige Liste
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

# Erzeuge den Plot:
fig, ax = plt.subplots(figsize=(18,10))
l0, = ax.plot(x, y_Hp, 'b', label ='Heizplatte')
l1, = ax.plot(x, y_PH, 'r', label ='PT1000 - Hp')
Kurven = [l0, l1]
if Kw == True:
    l2, = ax.plot(x, y_PyKw, 'y', label ='Pyro. Kw')
    Kurven.append(l2)
if Lw20 == True:
    l3, = ax.plot(x, y_PyLw20, 'grey', label ='Pyro. Lw20:1')
    Kurven.append(l3)
if Lw10 == True:
    l4, = ax.plot(x, y_PyLw10, 'g', label ='Pyro. Lw10:1')
    Kurven.append(l4)
if AD1 == True:
    l5, = ax.plot(x, y_AD1, 'm', label ='Adafruit PT100 1')
    Kurven.append(l5)
if AD2 == True:
    l6, = ax.plot(x, y_AD2, 'k', label ='Adafruit PT100 2')
    Kurven.append(l6)
if AD3 == True:
    l7, = ax.plot(x, y_AD3, 'c', label ='Adafruit PT100 3')
    Kurven.append(l7)
plt.legend(bbox_to_anchor=(1.28, 1.02))                           # Legende frei platzieren! - https://www.physi.uni-heidelberg.de/Einrichtungen/AP/python/xyDiagramme.html
plt.title('Vergleich der Kurven',fontsize=35)
plt.ylabel("Temperatur in °C",fontsize=20)
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

##################################################################################################################
# Plotten der Daten in der Datei für die Endgültigen Emissionsgrade:

# Listen:
values = []
KurvenE = []

solltemp =[]
vergleichstemp = []
emisKw = []
emisLw20 = []
emisLw10 = []

new_Style = False

Antwort = input('\nWollen sie sich auch die Emissionsgrade Graphisch anzeigen lassen? J/N/E: ').upper()
if Antwort == 'J':
    nameE = name.split('.')[0][:-4] + 'Emis_Ende.txt'
    path = '../Bilder_und_Daten/' + ordner + nameE
if not Antwort == 'N':                                                               # Wenn man ein N eingibt, so sagt man dem Programm ds es die datei nicht gibt oder man es nicht sehen will
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
        nameE = input('Dateiname (ohne Dateiende): ')
        ordner = input('Ordner Pfad (am Ende / setzen): ')
        path = '../Bilder_und_Daten/' + ordner + nameE + '.txt'

    # Datei auslesen:
    with open(path,'r', encoding="utf-8") as fi:
        for num, line in enumerate(fi, 1):
            if '[%]' in line:                            # gehe bis zur Zeile wo die Werte Namen stehen (wofür die folgenden werte stehen)
                if 'Vergleichs' in line:                 # um die alten Bilder, ohne Vergleichstemperatur eintrag angeben zu können!
                    new_Style = True                      
                break
        lines = fi.readlines()                           # lese alle zeilen ein (alle Zeilen mit Werten, da die ersten übersprungen wurden)
        for line in lines:
            values = line.split()
            solltemp.append(float(values[0]))            # schreibe die werte in die richtige Liste
            if new_Style == True:                        # um die alten Bilder, ohne Vergleichstemperatur eintrag angeben zu können!
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
            
    # Erzeuge den Plot:
    fig1, ax1 = plt.subplots(figsize=(18,10))
    if Kw == True:
        l0, = ax1.plot(vergleichstemp, emisKw, 'y', label ='Pyro. Kw')
        KurvenE.append(l0)
    if Lw20 == True:
        l1, = ax1.plot(vergleichstemp, emisLw20, 'grey', label ='Pyro. Lw20:1')
        KurvenE.append(l1)
    if Lw10 == True:
        l2, = ax1.plot(vergleichstemp, emisLw10, 'g', label ='Pyro. Lw10:1')
        KurvenE.append(l2)
    plt.legend(bbox_to_anchor=(1.28, 1.02))                           # Legende frei platzieren! - https://www.physi.uni-heidelberg.de/Einrichtungen/AP/python/xyDiagramme.html
    plt.title('Emissionsgrad über Tempratur',fontsize=35)
    plt.ylabel("Emissionsgrad in %",fontsize=20)
    plt.xlabel("Tempratur in °C",fontsize=20)
    plt.tight_layout()                                                # https://www.delftstack.com/de/howto/matplotlib/how-to-place-legend-outside-of-the-plot-in-matplotlib/ 
    plt.grid()

    raxE = plt.axes([0.8, 0.2, 0.18, 0.25])
    labelsE = [str(line.get_label()) for line in KurvenE]
    visibilityE = [line.get_visible() for line in KurvenE]
    checkE = CheckButtons(raxE, labelsE, visibilityE)

    def func(label):
        indexE = labelsE.index(label)
        KurvenE[indexE].set_visible(not KurvenE[indexE].get_visible())
        plt.draw()

    checkE.on_clicked(func)

######################################################################################################################
plt.show()                                                        # zeigt die Bilder an
    

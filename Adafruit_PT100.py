import board
import digitalio
import adafruit_max31865

import random

global Adafruit_array, debug_A, test_A, maxI
maxI = 0
Adafruit_array = []

###########################################################################
def Init_Adafruit(i, dbg, test, GPIO, Res, RefRes, Wire):                 # Initaliesiere Adafruit
###########################################################################
        global Adafruit_array, debug_A, test_A, maxI

        debug_A = dbg
        test_A = test

        if not test_A:
            spi = board.SPI()
            cs = digitalio.DigitalInOut(GPIO)                                  # Chip select of the MAX31865 board. (GPIO = z.B. board.D16)
            sensor = adafruit_max31865.MAX31865(spi, cs, rtd_nominal=Res, ref_resistor=RefRes, wires=Wire)
            if maxI <= i:                                                      # Schaut ob i größer ist als der aktuelle Größte Wert
                diff = i - maxI + 1                                            # Wenn ja muss die Liste erweitert werden, zuerst wird eine Differenz erzeugt
                maxI = i + 1                                                   # dann wird der aktuelle Max. Wert überschrieben (+1 da Listen bei 0 anfangen und range nicht bis zur Endzahl geht)
                n = 0
                for n in range(diff):                                          # nun wird die Liste um einige Plätze erweitert (alle unbelegten Plätze bis zum Max, werden mit einer Null belegt)             
                    Adafruit_array.append(0)                                   # hier wird die Null angehangen
            Adafruit_array[i] = sensor                                         # hier werden die Nullen dann mit dem Sensor überchrieben, somit kann man immer den richtigen sensor ansprechen ohne das man die verschiedenen Sensoren in einer festgelegten Reihe initialisiert            
            print(f'Adafruit PT100 {i+1} initialisiert!')
            if debug_A == True:
                print(f'Sensor am {GPIO} / Widerstand = {Res} Ohm / Ref. Widerstand = {RefRes}/ {Wire}-Leiter Verkabelung\n')
                print(sensor)

###########################################################################
def get_Temperatur(i):                                                    # Initaliesiere Adafruit
###########################################################################
        if test_A == False:
            tempA = Adafruit_array[i].temperature
            if debug_A == True:
                print(f'Reading from {Adafruit_array[i]}: {tempA} °C') 
        else:
            tempA = random.uniform(15,25)                                  # Bei Test werden zufällige Zahlen als Messwerte genommen!
        return tempA
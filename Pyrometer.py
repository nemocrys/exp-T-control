import serial
import random
import numpy

global ser_py, debug_pyro, test_pyro, maxI
maxI = 0
ser_py = []

###########################################################################
def Init_Pyro(i, com, rate, bits, stop, parity, dbg, test):               # Initialisierung des Pyrometers
###########################################################################
    
    global ser_py, debug_pyro, test_pyro, maxI
    
    debug_pyro = dbg
    test_pyro = test
    portName = com                                                        # 'COM'+str(com)
    try:
        serial.Serial(port=portName)
    except serial.SerialException:
        print ('Port ' + portName + ' not present')
        if not test_pyro:
            quit()
    
    # noch mal überlegen!!
    if not test_pyro:
        if maxI <= i:                                                      # Schaut ob i größer ist als der aktuelle Größte Wert
            diff = i - maxI + 1                                            # Wenn ja muss die Liste erweitert werden, zuerst wird eine Differenz erzeugt
            maxI = i + 1                                                   # dann wird der aktuelle Max. Wert überschrieben (+1 da Listen bei 0 anfangen und range nicht bis zur Endzahl geht)
            n = 0
            for n in range(diff):                                          # nun wird die Liste um einige Plätze erweitert (alle unbelegten Plätze bis zum Max, werden mit einer Null belegt)             
                ser_py.append(0)                                           # hier wird die Null angehangen
                
        ser_py_ = serial.Serial(
            port = portName,
            baudrate = int(rate),
            parity = parity,
            stopbits = int(stop),
            bytesize = int(bits),            
            timeout = 0.1)
        print('Pyrometer Initialiesiert!')
        
        ser_py[i] = ser_py_

###########################################################################
def Config_Pyro(i, em, tr):                                               # Configuration des Pyrometers mit Emissions- und Transmissionsgrad
###########################################################################

    if not test_pyro:
        print ('Pyrometer ', i+1, ' : ', Get_ID(i))
        Write_Pilot(i, False)                               # Laser vorerst ausschalten
        Write_Pyro_Para(i, 'e', str(em))                    # Emissionsgrad
        Write_Pyro_Para(i, 't', str(tr))                    # Transmissonsgrad
    
###########################################################################
def Get_Focus(i):                                                         # Bestimmung des Abstandes, Messabstand von Pyrometer zum Messobjekt, Fokus einstellen nur am Gerät
###########################################################################

    p = '00df\r'
    ser_py[i].write(p.encode())                                           # Abstand wird vomm Programm erfragt und kann dann Ausgegeben werden vom Programm
    pyro_focus = ser_py[i].readline().decode()
    return (pyro_focus)

###########################################################################
def Get_ID(i):                                                            # Ausgabe des Gerätenamens/-typs
###########################################################################
    
    p = '00na\r'
    ser_py[i].write(p.encode())
    #print(ser_py[i].readline())
    pyro_id = ser_py[i].readline().decode()
    return (pyro_id)

###########################################################################
def Get_OK(i):                                                            # Gibt ein Okay zurück, wenn es einen Befehl bekommen hat 
###########################################################################
    
    #print(ser_py[i].readline())
    answer = ser_py[i].readline().decode()
    print ('Pyrometer ', str(i+1), ' = ', answer)
    return answer
      
###########################################################################
def Write_Pyro_Para(i, para, str_val):                                    # Übergibt einen Befehl an das Pyrometer
###########################################################################
    
    if para == 'e':                                                             # Emission (e)
        val = '%05.1f' % float(str_val)
        str_val = str(val).replace('.', '')    
        p = '00em' + str_val + '\r'
    if para == 't':                                                             # Transmission (t)                      
        val = '%05.1f' % float(str_val)
        str_val = str(val).replace('.', '')    
        p = '00et' + str_val + '\r'
    if para == 't90':                                                           # Erfassungszeit (t90)
        p = '00ez' + str_val + '\r'
    if not test_pyro:
        if debug_pyro:
            print ('Sending to ' + ser_py[i].port +': ', p.encode())
        ser_py[i].write(p.encode())                                             # Übergibt den jeweiligen Befehl an das Pyrometer
        check = Get_OK(i)                                                       # Erfragt ob der Befehl eingegangen ist
        while 'no' in check:                                                    # sollte der Wert nicht eingegangen sein, so soll er es solange probieren bis es geklappt hat
            ser_py[i].write(p.encode())                                         
            check = Get_OK(i)
        answer = Get_Pyro_Para(i, para)                                         # Sendet den Befehl an das Gerät und die Antwort wird in diese Variable geschrieben
        if para == 'e':
            print ('Pyrometer ', str(i+1), ' emission = ', answer)
        if para == 't':
            print ('Pyrometer ', str(i+1), ' transmission = ', answer)     
        if para == 't90':
            print ('Pyrometer ', str(i+1), ' t90 = ', answer)     
    else:
        print ('Pyro ' +str(i+1) + ' parameter: ', p)

        
###########################################################################
def Get_Pyro_Para(i, para):                                               # Erfragt die Daten (e, t und t90) vom Pyrometer
###########################################################################
### e = emission, t = transmission, t90 = Erfassungszeit
    
    if para == 'e':
        p = '00em\r'
    if para == 't':
        p = '00et\r'
    if para == 't90':
        p = '00ez\r'
    if not test_pyro:
        if debug_pyro:
            print ('Sending to ' + ser_py[i].port +': ', p.encode())
        ser_py[i].write(p.encode())
        answer = ser_py[i].readline().decode()
        while 'no' in answer:                                             # Soll bei einem "no" das senden widerholen!
            ser_py[i].write(p.encode())
            answer = ser_py[i].readline().decode()
        if para == 'e' or para == 't':                                    # Bei Emissionsgrad und Transmissionsgrad werden so sofort die Werte in einen float gelegt
            answer = answer[:-1]
            l = len(answer)
            answer = answer[:l-1] + '.' + answer[l-1:]
            answer = float(answer)  
    else:                                                                 # Im Test-Modus wird in Zufälliger Wert übergeben, für den Live-Emissions-Plot
        print ('Pyro ' +str(i+1) + ' parameter: ', p)
        answer = random.uniform(30,40)
    return (answer)

###########################################################################
def Read_Pyro(i):                                                         # Erfragt den Messwert
###########################################################################

    p = '00ms\r'                                                          # Befehl zur Erfragung des Messwertes
    if not test_pyro:
        if debug_pyro:
            print ('Sending to ' + ser_py[i].port + ': ', p.encode())
        ser_py[i].write(p.encode())
        temp = ser_py[i].readline().decode()
        temp = temp[:-1]                                                  # Abschlusszeichen entfernen
        l = len(temp)
        temp = temp[:l-1] + '.' + temp[l-1:]                              # Zusammensetzung zur Zahl, Punkt (Komma) einfügen (Rückgabe z.B. 00740 = 74,0 bzw 74.0)
        if debug_pyro:
            print ('Reading from ' + ser_py[i].port + ': ', float(temp))
    else:
        temp = random.uniform(20,22)                                      # Bei Test werden zufällige Zahlen als Messwerte genommen!
    return (float(temp))

###########################################################################
def Write_Pilot(i, state):                                                # Zum Einschalten des Lasers
###########################################################################

    print ('Pilot-'+str(i+1)+' : ' +str(state))
    if not test_pyro:
        if state:
            p = '00la1\r'                                               # Laser Ein
        else:
            p = '00la0\r'                                               # Laser Aus
        if debug_pyro:
            print ('Sending to ' + ser_py[i].port +': ', p.encode()) 
        ser_py[i].write(p.encode())
        check = Get_OK(i)
import serial
import random
import numpy

global ser_py_array, debug_pyro, test_pyro

###########################################################################
def Init_Pyro_Array(com, rate, bits, stop, parity, dbg, test):            # Initaliesiert das Pyrometer
###########################################################################
    
    global ser_py_array, debug_pyro, test_pyro
    
    debug_pyro = dbg
    test_pyro = test
    portName = com                                                        # 'COM'+str(com)
    try:
        serial.Serial(port=portName)
    except serial.SerialException:
        print ('Port ' + portName + ' not present')
        if not test_pyro:
            quit()
    
    if not test_pyro:
        ser_py_array = serial.Serial(
            port = portName,
            baudrate = int(rate),
            parity = parity,
            stopbits = int(stop),
            bytesize = int(bits),            
            timeout = 0.1)
            
###########################################################################
def Config_Pyro_Array(i, em):                                             # Konfiguration des Pyrometers mit Ausgabe der ID
###########################################################################
# i is the head number, starts with 0
    
    if not test_pyro:
        print ('Pyrometer array head', i+1, ' : ', Get_head_ID(i))
        Write_Pyro_Array_Para(i, 'e', str(em))
    
###########################################################################
def Get_nb_of_head():                                                     # Anzahl der Sensoren an der Box
###########################################################################
    
    p = '00oc\r'

###########################################################################
def Get_head_ID(i):                                                       # gibt die Seriennummer des Sensors zurück, 5-Stellige Dezimal-Zahl
###########################################################################
# i is the head number, starts with 0
    
    p = '00A' + str(i+1) + 'sn\r'
    ser_py_array.write(p.encode())
    pyro_head_id = ser_py_array.readline().decode()
    return (pyro_head_id)

###########################################################################
def Get_OK(i):                                                            # Gibt wie beim anderen Pyrometer ein Ok zurück, wenn das Gerät einen Befehl bekommt
###########################################################################
    
    answer = ser_py_array.readline().decode()
    print ('Pyrometer array head', str(i+1), ' = ', answer)
    return answer
    
    
###########################################################################
def Write_Pyro_Array_Para(i, para, str_val):                              # Übergabe bestimmter Parameter
###########################################################################
### e = emission
### i is the head number, starts with 0
    
    if para == 'e':
        val = '%05.1f' % float(str_val)
        str_val = str(val).replace('.', '')    
        p = '00A' + str(i+1) + 'em' + str_val + '\r'
    if para == 't90':
        p = '00A' + str(i+1) + 'ez' + str_val + '\r'
    if not test_pyro:
        if debug_pyro:
            print ('Sending to head ' + str(i+1) +': ', p.encode())
        ser_py_array.write(p.encode())
        check = Get_OK(i)
        #while check == "no":
        while 'no' in check:                                                    # Soll bei einem "no" das senden widerholen!
            ser_py_array.write(p.encode())
            check = Get_OK(i)
        answer = Get_Pyro_Array_Para(i, para)
        if para == 'e':
            print ('Pyrometer array head ', str(i+1), ' emission = ', answer)
        if para == 't90':
            print ('Pyrometer array head ', str(i+1), ' t90 = ', answer)     
    else:
        print ('Pyrometer array head ' +str(i+1) + ' parameter: ', p)

        
###########################################################################
def Get_Pyro_Array_Para(i, para):                                         # holt die Parameter Daten vom Gerät
###########################################################################
### e = emission, t = transmission
    
    if para == 'e':
        p = '00A' + str(i+1) + 'em\r'
    if para == 't90':
        p = '00A' + str(i+1) + 'ez\r'
    if not test_pyro:
        if debug_pyro:
            print ('Sending to pyrometer head ' + str(i+1) + ': ', p.encode())
        ser_py_array.write(p.encode())
        answer = ser_py_array.readline().decode()
        while 'no' in answer:                                                   # Soll bei einem "no" das senden widerholen!
            ser_py_array.write(p.encode())
            answer = ser_py_array.readline().decode()
        if para == 'e':                                                         # Bei Emissionsgrad werden so sofort die Werte in einen float gelegt
            answer = answer[:-1]
            l = len(answer)
            answer = answer[:l-1] + '.' + answer[l-1:]
            answer = float(answer)  
    else:                                                                       # Im Test-Modus wird in Zufälliger Wert übergeben, für den Live-Emissions-Plot
        print ('Pyrometer array head ' + str(i+1) + ' parameter: ', p)    
        answer = random.uniform(30,40)
    return (answer)    

###########################################################################
def Read_Pyro_Array(i):                                                   # liest die Messdaten aus
###########################################################################
# i is the head number, starts with 0
    
    p = '00A' + str(i+1) + 'ms\r'
    if not test_pyro:
        if debug_pyro:
            print ('Sending to head ' + str(i+1) + ': ' ,p.encode())           # Warum sind da Kommas
        ser_py_array.write(p.encode())
        temp = ser_py_array.readline().decode()
        temp = temp[:-1]
        l = len(temp)
        temp = temp[:l-1] + '.' + temp[l-1:]
        if debug_pyro:
            print ('Reading from head ' + str(i+1) + ': ', float(temp))
    else:
        temp = random.uniform(20,22)
    if temp == 'n.o':                                                           # Fehlerausgabe!
        return 'n.o'
    return (float(temp))



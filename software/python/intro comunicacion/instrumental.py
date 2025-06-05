import visa
import numpy as np
import time
import serial # Si falla, instalar con: "conda install -c anaconda pyserial" o "pip install pyserial"
import datetime

class HantekPPS2320A:
    """
    Fuente DC
    Send Command Word	Perform Operation
    a + line break (Hereafter, every command must take 0x0a as the line break to over, ignore the following)	Back to device model
    suXXXX	CH1 preset output voltage, units V; e.g. 1200 stands for 12.00V
    siXXXX 	CH1 preset output current, units A; e.g. 2500 stands for 2.500A
    saXXXX	CH2 preset output voltage, units V; e.g. 1200 stands for 12.00V
    sdXXXX	CH2 preset output current, units A; e.g. 2500 stands for 2.500A
    O0	Output indicator light switch-off
    O1	Output indicator light switch-on
    O2	Parallel, series, trace, output indicator light switch-off
    O3	Series, trace, output indicator switch-off; Parallel indicator light switch-on
    O4	Parallel, trace, output indicator switch-off; Series indicator light switch-on
    O5	Parallel, series, output indicator switch-off; Trace indicator light switch-on
    O6	CH1 indicator light switch-on
    O7	CH2 indicator light switch-on
    O8	CH3 3.3V indicator light switch-on
    O9	CH3 5V indicator light switch-on
    Oa	CH3 2.5V indicator light switch-on
    rv	Read the measured voltage of CH1
    ra	Read the measured current of CH1
    ru	Read the preset voltage of CH1
    ri	Read the preset current of CH1
    rh	Read the measured voltage of CH2
    rj	Read the measured current of CH2
    rk	Read the preset voltage of CH2
    rq	Read the preset current of CH2
    rm	Read the device working mode
    rl	Read lock state
    rp	Read CH2 state
    rs	Read CH1 state
    rb	Read CH3 state	
    """    
    def __init__(self, resource):
        self._fuente = visa.ResourceManager().open_resource(resource)
        print(self._fuente.query('*IDN?'))
                
    def set_voltage1(self, value):
        if value > 3:
            raise ValueError("El valor no puede ser mayor que 3")
        self._fuente.write("su{0:04d}".format(round(value*100)))

class SR830:
    '''Clase para el manejo amplificador Lockin SR830 usando PyVISA de interfaz'''

    scale_values = (2e-9, 5e-9, 10e-9, 20e-9, 50e-9, 100e-9, 200e-9, 500e-9, 1e-6,
                    2e-6, 5e-6, 10e-6, 20e-6, 50e-6, 100e-6, 200e-6, 500e-6, 1e-3,
                    2e-3, 5e-3, 10e-3, 20e-3, 50e-3, 100e-3, 200e-3, 500e-3, 1) # in V

    time_constant_values = (10e-6, 30e-6, 100e-6, 300e-6, 1e-3, 3e-3, 10e-3, 30e-3, 100e-3, 300e-3,
                    1e0, 3e0, 10e0, 30e0, 100e0, 300e0, 1e3, 3e3, 10e3, 30e3) # in s

    def __init__(self, resource):
        self._lockin = visa.ResourceManager().open_resource(resource)
        #print(self._lockin.query('*IDN?')) # habria que ver si es mejor no pedir IDN. Puede que trabe la comunicacion al ppio
        self._lockin.write("LOCL 2") #Bloquea el uso de teclas del Lockin
        time.sleep(1) # tal vez ayuda a evitar errores de comunicacion del pyvisa
        self.scale = self.get_scale()
        self.time_constant = self.get_time_constant()

    def __del__(self):
        self._lockin.write("LOCL 0") #Desbloquea el Lockin
        self._lockin.close()

    def set_modo(self, modo):
        '''Selecciona el modo de medición, A, A-B, I, I(10M)'''
        self._lockin.write("ISRC {0}".format(modo))

    def set_filtro(self, sen, tbase, slope):
        '''Setea el filtro de la instancia'''
        #Página 90 (5-4) del manual
        self._lockin.write("OFLS {0}".format(slope))
        self._lockin.write("OFLT {0}".format(tbase))
        self._lockin.write("SENS {0}".format(sen))
       
    def set_aux_out(self, auxOut = 1, auxV = 0):
        '''Setea la tensión de salida de al Aux Output indicado.
        Las tensiones posibles son entre -10.5 a 10.5'''
        self._lockin.write('AUXV {0}, {1}'.format(auxOut, auxV))
           
    def set_referencia(self,isIntern, freq, voltaje = 1):
        if isIntern:
            #Referencia interna
            #Configura la referencia si es así
            self._lockin.write("FMOD 1")
            self._lockin.write("SLVL {0:f}".format(voltaje))
            self._lockin.write("FREQ {0:f}".format(freq))
        else:
            #Referencia externa
            self._lockin.write("FMOD 0")
           
    def set_scale(self, scale_number):
        self.scale = min(scale_number,len(self.scale_values))
        self._lockin.write(f'SENS {self.scale}')
        return self.scale
   
    def get_scale(self):
        self.scale = int(self._lockin.query_ascii_values('SENS ?')[0])
        return self.scale

    def set_time_constant(self, time_constant_number):
        self._lockin.write(f'OFLT {time_constant_number}')
        self.time_constant = time_constant_number
        return self.time_constant
   
    def get_time_constant(self):
        return int(self._lockin.query_ascii_values('OFLT ?')[0])

    def set_display(self, isXY):
        if isXY:
            self._lockin.write("DDEF 1, 0") #Canal 1, x
            self._lockin.write('DDEF 2, 0') #Canal 2, y
        else:
            self._lockin.write("DDEF 1,1") #Canal 1, R
            self._lockin.write('DDEF 2,1') #Canal 2, T
   
    def get_display(self):
        '''Obtiene la medición que acusa el display.
        Es equivalente en resolución a la medición de los parámetros con SNAP?'''
        orden = "SNAP? 10, 11"
        return self._lockin.query_ascii_values(orden, separator=",")
       
    def get_medicion(self,isXY = True):
        '''Obtiene X,Y o R,Ang, dependiendo de isXY'''
        orden = "SNAP? "
        if isXY:
            self._lockin.write("DDEF 1,0") #Canal 1, XY
            orden += "1, 2" #SNAP? 1,2
        else:
            self._lockin.write("DDEF 1,1") #Canal 1, RTheta
            orden += "3, 4" #SNAP? 3, 4
        return self._lockin.query_ascii_values(orden, separator=",")

    def auto_scale(self):
        '''
            Utiliza medicion polar (r, angulo)          
            inf_threshold es el porcentaje minimo de la escala  para el cual el
            autoescalado empiza a efectuarse: intenta mantenerse sobre ese rango. valor float de 0 a 1
        '''
        debug = True
        sup_theshold = 1
        inf_threshold = 0.1        
        nespera = 5 # se recomienda esperar entre 3 y 5 veces el tiempo de medicion entre escalado y medicion        
        tespera = self.time_constant_values[self.time_constant] * nespera
        time.sleep(tespera)
        r,tita = self.get_medicion(isXY=False)

        while r < self.scale_values[self.scale] * inf_threshold and self.scale > 0:
            if debug:
                print('Valor por debajo de threshold, bajo escala (r=%g, oldscale=%g)'%(r,self.scale_values[self.scale]))
            self.scale -= 1
            self.set_scale(self.scale)
            time.sleep(tespera) # esperar N * el tiempo de integracion antes de medir
            r,tita = self.get_medicion(isXY=False)

        while r > self.scale_values[self.scale] * sup_theshold and self.scale < (len(self.scale_values)-1):
            if debug:
                print('Overloaded, subo escala (oldscale=%g)'%(self.scale_values[self.scale]))
            self.scale += 1
            self.set_scale(self.scale)
            time.sleep(tespera)
            r,tita = self.get_medicion(isXY=False)
       
        if debug:
            print('Listo (r=%g, scale=%g)'%(r, self.scale_values[self.scale]))

        return r, tita
		
class AFG3021B:
    
    def __init__(self, name='USB0::0x0699::0x0346::C034165::INSTR'):
        self._generador = visa.ResourceManager().open_resource(name)
        print(self._generador.query('*IDN?'))
        
        #Activa la salida
        self._generador.write('OUTPut1:STATe on')
        # self.setFrequency(1000)
        
    def __del__(self):
        self._generador.close()
        
    def setFrequency(self, freq):
        self._generador.write(f'FREQ {freq}')
        
    def getFrequency(self):
        return self._generador.query_ascii_values('FREQ?')
        
    def setAmplitude(self, freq):
        print('falta')
        
    def getAmplitude(self):
        print('falta')
        return 0

class TDS1002B:
    """Clase para el manejo osciloscopio TDS2000 usando PyVISA de interfaz
    """
    
    def __init__(self, name):
        self._osci = visa.ResourceManager().open_resource(name)
        print(self._osci.query("*IDN?"))

    	#Configuración de curva
        
        # Modo de transmision: Binario positivo.
        self._osci.write('DAT:ENC RPB') 
        # 1 byte de dato. Con RPB 127 es la mitad de la pantalla
        self._osci.write('DAT:WID 1')
        # La curva mandada inicia en el primer dato
        self._osci.write("DAT:STAR 1") 
        # La curva mandada finaliza en el último dato
        self._osci.write("DAT:STOP 2500") 

        #Adquisición por sampleo
        self._osci.write("ACQ:MOD SAMP")
				
        #Bloquea el control del osciloscopio
        self._osci.write("LOC")
    	
    def __del__(self):
        self._osci.close()			

    def config(self):
        #Seteo de canal
        self.set_channel(channel=1, scale=20e-3)
        self.set_channel(channel=2, scale=20e-3)
        self.set_time(scale=1e-3, zero=0)

    def unlock(self):
         #Desbloquea el control del osciloscopio
        self._osci.write("UNLOC")

    def set_channel(self, channel, scale, zero=0):
    	#if coup != "DC" or coup != "AC" or coup != "GND":
    	    #coup = "DC"
    	#self._osci.write("CH{0}:COUP ".format(canal) + coup) #Acoplamiento DC
    	#self._osci.write("CH{0}:PROB 
        self._osci.write("CH{0}:SCA {1}".format(channel, scale))
        self._osci.write("CH{0}:POS {1}".format(channel, zero))
	
    def get_channel(self, channel):
        return self._osci.query("CH{0}?".format(channel))
		
    def set_time(self, scale, zero=0):
        self._osci.write("HOR:SCA {0}".format(scale))
        self._osci.write("HOR:POS {0}".format(zero))	
	
    def get_time(self):
        return self._osci.query("HOR?")
	
    def read_data(self, channel):
        # Hace aparecer el canal en pantalla. Por si no está habilitado
        self._osci.write("SEL:CH{0} ON".format(channel)) 
        # Selecciona el canal
        self._osci.write("DAT:SOU CH{0}".format(channel)) 
    	#xze primer punto de la waveform
    	#xin intervalo de sampleo
    	#ymu factor de escala vertical
    	#yoff offset vertical
        xze, xin, yze, ymu, yoff = self._osci.query_ascii_values('WFMPRE:XZE?;XIN?;YZE?;YMU?;YOFF?;', 
                                                                 separator=';') 
        data = (self._osci.query_binary_values('CURV?', datatype='B', 
                                               container=np.array) - yoff) * ymu + yze        
        tiempo = xze + np.arange(len(data)) * xin
        return tiempo, data
    
    def get_range(self, channel):
        xze, xin, yze, ymu, yoff = self._osci.query_ascii_values('WFMPRE:XZE?;XIN?;YZE?;YMU?;YOFF?;', 
                                                                 separator=';')         
        rango = (np.array((0, 255))-yoff)*ymu +yze
        return rango   

class Agilent34970A:
    """Clase para el manejo multiplexor Agilent34970A usando PyVISA de interfaz
    """

    def __init__(self, name, 
                 scanInterval = 1, 
                 channelDelay = 0.2,
				 channelsList = (101,102,103,104,105,106,107,108)):
        self.scanInterval = scanInterval
        self.channelDelay = channelDelay
        self.channelsList = channelsList
        self.nChannels = len(self.channelsList)
        self._mux = visa.ResourceManager().open_resource(name)
        print(self._mux.query("*IDN?"))
        self.config(scanInterval =scanInterval, 
                 channelDelay = channelDelay,
				 channelsList =channelsList) 

    def __del__(self):
        self._mux.close()		
	
    def config(  self, 
                 scanInterval = 1, 
                 channelDelay = 0.2,
				 channelsList = (101,102,103,104,105,106,107,108)):
        
        #Setear atributos
        self.scanInterval = scanInterval
        self.channelDelay = channelDelay
        self.channelsList = channelsList
        self.nChannels = len(self.channelsList)

        #Limpiar configuración
        self._mux.write('*CLS')
        
        #Configurar barrido
        self._mux.write('ROUTE:SCAN (@' + str(self.channelsList)[1:])
        self._mux.write('ROUT:CHAN:DELAY ' + str(self.channelDelay))
        self._mux.write('FORMAT:READING:CHAN ON') #Return channel number with each reading
        self._mux.write('FORMAT:READING:TIME ON') # Return time stamp with each reading
		#self._mux.write('FORMat:READing:TIME:TYPE  RELative') #Return time stamp im seconds since scanstart
        self._mux.write('FORMat:READing:TIME:TYPE  ABSolute') #Return time stamp absolute
        self._mux.write('FORMat:READing:UNIT OFF')
        self._mux.write('TRIG:TIMER ' + str(self.scanInterval))		
        self._mux.write('TRIG:COUNT ' + str(1)) # one scan sweep per measure
    
    def get_time(self):	
        self.initialTime = self._mux.query_ascii_values('SYSTEM:TIME?') #pido la hora de inicio			
        return float(self.initialTime[0])*3600 + float(self.initialTime[1])*60 + self.initialTime[2]	
	
    def query(self, myquery):
        return self._mux.query(myquery)

    def write(self, myquery):
        self._mux.write(myquery)
    
    def one_scan(self):
        # time.sleep(.5+(self.channelDelay+0.1)*self.nChannels)
        
        data = self._mux.query_ascii_values('READ?')
        data2 = np.transpose(np.reshape(np.array(data), (self.nChannels, 8) ) )
        temperatura = data2[0]
        tiempo = np.array(data2[1:7])
        tiempo = [datetime.datetime(int(x[0]), int(x[1]), int(x[2]), int(x[3]), int(x[4]), int(x[5]), int((x[5] % 1)*1000000)).timestamp() for x in np.transpose(tiempo)]          
        canal = data2[7]
        
        return data, temperatura, tiempo, canal

class Amporobe38XRA:
    def __init__(self,port='COM1'): 
        self._mult = serial.Serial()        
        self._mult.baudrate = 9600
        self._mult.port = port
        self._mult.bytesize = 8
        self._mult.parity = 'N'
        self._mult.stopbits = 1
        self._mult.timeout = None    
        self.open() 

            
    def open(self):
        if not self._mult.is_open:
            self._mult.open()            

    def close(self):
        self._mult.close()	        

    def __del__(self):
        self._mult.close()	        
        
    def __LeeStringAmprobe(self):
        #%Lee el string que manda el multimetro.
        #%A veces manda strings de distintas longitudes. Itero hasta que me da uno
        #%de 15 caracteres.
    
        self._mult.flushInput()
        count = 0
        mystr = ""
        while len(mystr)!=15:
            count = count+1
            mystr =self._mult.readline().decode('ascii')
            if len(mystr)==0:
                print('Salgo, probablemente timeout, desconecatado')
                return mystr
        return mystr        

    def __ProcesaStringAmprobe(self,mystr,verbose):
        #%extraigo los valores pertinentes del string
        code = mystr[0:2]
        data=(mystr[2:6])
        modo=float(mystr[6])
        exponente=float(mystr[8])
        acdc=float(mystr[9])
        absrel=(mystr[11]) # 8|A  8: rango fijo, A: Autorango
        signo=float(mystr[12])
        
        if data == 'B0DD':
            print('Resistencia infinita')
            data = float('inf')
        else:
            data = float(data)
    
        #%muestro en pantalla (si me lo piden)
        if verbose:
            print('Str:  %s'%(mystr))
            print('Code: %s'%(code))
            print('Data:   %04.0f'%(data))
            print('Modo:       %d'%(modo))
            print('str(8):      %s'%(mystr[7]))
            print('Exp:          %d'%(exponente))
            print('AC|DC|AC+DC:   %d'%(acdc))
            print('str(11):        %s'%(mystr[10]))
            print('absrel:          %s'%(absrel))
            print('Signo:            %d'%(signo))
        
        if code == '10': #Voltmeter ~
            if modo == 0:
                Ylab = 'Voltage ~ [V]'  
                value = data*1e-4*1.0*pow(10,exponente)
            else: 
                Ylab  = 'Voltage ~ [dBm]';
                value = pow(-1,signo)*data*0.01;
        elif code == '0C': #Voltmeter --
            Ylab = 'Voltage';        
            Ylab = Ylab +' DC [V]'
            value = pow(-1,signo)*data*1.0*pow(10,exponente-4)
        elif code=='08': # Ohm-meter
            Ylab  = 'Resistance [Ohm]';
            value = pow(-1,signo)*data*1.0*pow(10,4-exponente)
        elif code == '04':  # Test diode
            Ylab = 'Test diode [V]'
            value = data/1000
        elif code == '0F':  # Frequencemeter
            value = pow(-1,signo)*data*0.01*pow(10,exponente)
            if modo == 2:
                Ylab  = 'Cyclic Rate [%]'
            else:
                Ylab = 'Frequency [Hz]'
        elif code == '0B':  # Capacity
            Ylab = 'Capacity [µF]'    
            value = pow(-1,signo)*data*pow(10,exponente-5)
        elif code == '07':  # Current µA
            Ylab = 'Current [A]'
            value = pow(-1,signo)*data*pow(10,exponente-8)
            if acdc == 0:
                Ylab= 'DC ' + Ylab  
            elif acdc == 1:
                Ylab= 'AC ' + Ylab  
            elif acdc == 2:
                Ylab= 'AC+DC ' + Ylab  
        elif code == '0E':  # Current mA
            Ylab = 'Current [A]'
            value = pow(-1,signo)*data*pow(10,exponente-6)
            if acdc == 0:
                Ylab= 'DC ' + Ylab  
            elif acdc == 1:
                Ylab= 'AC ' + Ylab  
            elif acdc == 2:
                Ylab= 'AC+DC ' + Ylab  
        elif code == '0A':  # Current A
            Ylab = 'Current [A]'
            value = pow(-1,signo)*data/1000
            if acdc == 0:
                Ylab= 'DC ' + Ylab  
            elif acdc == 1:
                Ylab= 'AC ' + Ylab  
            elif acdc == 2:
                Ylab= 'AC+DC ' + Ylab  
        elif code == '03':  # mA 4-20 --
            Ylab = 'Current 4-20 [mA] --'
            value = data
        elif code == '06':  #Temperature [°C]
            Ylab = 'Temperature [°C]'
            value = pow(-1,signo)*data
        elif code == '02':  #Temperature [°F]
            Ylab = 'Temperature [°F]'
            value = pow(-1,signo)*data
        else:
            value = 0
            Ylab = ""
            
        if absrel=='8':
            Ylab= 'Delta ' + Ylab  
            
        return value,Ylab
    
    def GetValue(self,verbose=False):
        mystr = self.__LeeStringAmprobe()
        value, Ylab = self.__ProcesaStringAmprobe(mystr,verbose)
        return value, Ylab
        
    

# -*- coding: utf-8 -*-
"""
Multiplexor Agilent 34970A
Manual U (pdf): https://github.com/diegoshalom/labosdf/blob/master/manuales/Agilent34970a%20user%20manual.pdf
Manual P (pdf): https://github.com/diegoshalom/labosdf/blob/master/manuales/Agilent34970a%20command%20reference.pdf
Manual P (chm original): https://github.com/diegoshalom/labosdf/blob/master/manuales/Agilent34970a%20command%20reference.chm
"""

import visa
import time
import datetime

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
        self._mux.write('ROUTE:SCAN (@' + str(self.channelsList)[1:-1] + ")")
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

#Ejemplo comunicacion Multiplexor Difusividad térmica
from instrumental import Agilent34970A
mux = Agilent34970A('GPIB0::9::INSTR')
data, temperatura, tiempo, canal = mux.one_scan()
print(tiempo)
print(temperatura)
print(canal)
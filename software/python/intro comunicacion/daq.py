# NI-DAQmx Python Documentation: https://nidaqmx-python.readthedocs.io/en/latest/index.html
# NI USB-621x User Manual: https://www.ni.com/docs/en-US/bundle/usb-621x-manual/resource/usb-621x-manual.pdf
import matplotlib.pyplot as plt
import numpy as np
import nidaqmx
import math
import time


#para saber el ID de la placa conectada (DevX)
system = nidaqmx.system.System.local()
for device in system.devices:
    print(device)

#para setear (y preguntar) el modo y rango de un canal analógico
with nidaqmx.Task() as task:
    ai_channel = task.ai_channels.add_ai_voltage_chan("Dev1/ai1",max_val=10,min_val=-10)
    print(ai_channel.ai_term_cfg)    # puede ser DIFF o DIFFERENTIAL
    print(ai_channel.ai_max)
    print(ai_channel.ai_min)	
	

## Medicion por tiempo/samples de una sola vez
def medicion_una_vez(duracion, fs):
    cant_puntos = int(duracion*fs)
    with nidaqmx.Task() as task:
        modo= nidaqmx.constants.TerminalConfiguration.DIFFERENTIAL # puede ser DIFF o DIFFERENTIAL 
        task.ai_channels.add_ai_voltage_chan("Dev1/ai1", terminal_config = modo)
               
        task.timing.cfg_samp_clk_timing(fs,samps_per_chan = cant_puntos,
                                        sample_mode = nidaqmx.constants.AcquisitionType.FINITE)
        
        datos = task.read(number_of_samples_per_channel=nidaqmx.constants.READ_ALL_AVAILABLE, timeout=duracion+0.1)           
    datos = np.asarray(datos)    
    return datos

duracion = 1 #segundos
fs = 250000 #Frecuencia de muestreo
y = medicion_una_vez(duracion, fs)
plt.plot(y)
plt.grid()
plt.show()


## Medicion continua
def medicion_continua(duracion, fs):
    cant_puntos = int(duracion*fs)
    with nidaqmx.Task() as task:
        modo= nidaqmx.constants.TerminalConfiguration.DIFFERENTIAL # puede ser DIFF o DIFFERENTIAL 
        task.ai_channels.add_ai_voltage_chan("Dev1/ai1", terminal_config = modo)
        task.timing.cfg_samp_clk_timing(fs, sample_mode = nidaqmx.constants.AcquisitionType.CONTINUOUS)
        task.start()
        t0 = time.time()
        total = 0
        data =[]
        while total<cant_puntos:
            time.sleep(0.1)
            datos = task.read(number_of_samples_per_channel=nidaqmx.constants.READ_ALL_AVAILABLE)           
            data.extend(datos)
            total = total + len(datos)
            t1 = time.time()
            print("%2.3fs %d %d %2.3f" % (t1-t0, len(datos), total, total/(t1-t0)))            
        return data

fs = 2500 #Frecuencia de muestreo
duracion = 10 #segundos
y = medicion_continua(duracion, fs)
plt.plot(y)
plt.grid()
plt.show()

## Modo conteo de flancos 
# Obtengo el nombre de la primera placa y el primer canal de conteo (ci)
cDaq = system.devices[0].name
ci_chan1 = system.devices[0].ci_physical_chans[0].name
print(cDaq)
print(ci_chan1 )

# Pinout: 
# NiUSB6212 
# gnd: 5 or 37
# src: 33


def daq_conteo(duracion):
    with nidaqmx.Task() as task:

        # Configuro la task para edge counting
        task.ci_channels.add_ci_count_edges_chan(counter=ci_chan1,
            name_to_assign_to_channel="",
            edge=nidaqmx.constants.Edge.RISING,
            initial_count=0)
        
        # arranco la task
        task.start()
        counts = [0]
        t0 = time.time()
        try:
            while time.time() - t0 < duracion:
                count = task.ci_channels[0].ci_count
                print(f"{time.time()-t0:.2f}s {count-counts[-1]} {count}")
                counts.append(count)
                time.sleep(0.2)
                
        except KeyboardInterrupt:
            pass
        
        finally:
            task.stop()
            
    return counts  

duracion = 10 # segundos
y = daq_conteo(duracion)
plt.plot(y)
plt.grid()
plt.show()

## Medición con trigger
# Pinout: 
# NiUSB6210 
# PFI0: 1
# D GND: 5 o 11
from nidaqmx.constants import AcquisitionType, Edge

def medicion__una_vez_con_trigger(duracion, fs):
    cant_puntos = int(duracion*fs)
    with nidaqmx.Task() as task:
        # Canal analógico a medir
        modo= nidaqmx.constants.TerminalConfiguration.DIFFERENTIAL # puede ser DIFF o DIFFERENTIAL PREGUNTAR
        task.ai_channels.add_ai_voltage_chan("Dev1/ai1", terminal_config = modo)
   
        # Configuración de muestreo
        task.timing.cfg_samp_clk_timing(rate=fs, sample_mode=AcquisitionType.FINITE, samps_per_chan=cant_puntos)
   
        # Configurar trigger digital
        task.triggers.start_trigger.cfg_dig_edge_start_trig(trigger_source="/Dev1/PFI0", trigger_edge=Edge.RISING)
   
        task.start()
        datos = task.read(number_of_samples_per_channel=cant_puntos)
    datos = np.asarray(datos)
    return datos

duracion = 1 #segundos
fs = 250000 #Frecuencia de muestreo
y = medicion__una_vez_con_trigger(duracion, fs)
plt.plot(y)
plt.grid()
plt.show()
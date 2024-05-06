
import numpy as np
import matplotlib.pyplot as plt
from numpy.fft import fft
from scipy.signal import butter,lfilter

Fs = 100000;           #[Hz ] Sampling frequency                    
T = 1/Fs;              #[s] Sampling period       
L = 20000;             #[samples] Length of signal
t = np.array(range(0,L))*T;         #[s] Time vector
MaxT = L/Fs;           #[s] Tiempo maximo

A1 = 8;                #[V] amplitud
A2 = 4;                #[V] amplitud
FREC = 200;            #[Hz] Frecuencia de la señal y la referencia
OMEGA = FREC*2*np.pi;     #[rad/s] frecuencia angular
FASE1 = 0;             #[rad] Fase de la señal respecto a la referencia
FASE2 = np.pi/2;          #[rad] Fase de la señal respecto a la referencia
ruido = 4;             #[V] ruido
timeconstant=0.02;     #[s] Constante de tiempo del lockin, para el filtro

#Armo la señal con dos tramos de distinta amplitud y fase, y le sumo ruido
SENIAL=np.concatenate([A1*np.sin(OMEGA*t[:int(L/2)]+FASE1), A2*np.sin(OMEGA*t[int((L/2)):]+FASE2)])
RUIDO = ruido*np.random.randn(len(SENIAL));
ORIGINAL = SENIAL + RUIDO;

#Referencia
REFERENCIA1 = np.sin(OMEGA*t);#referencia en fase
REFERENCIA2 = np.cos(OMEGA*t);#referencia en cuadratura

plt.clf()
plt.subplot(3,2,1)
plt.plot(t,ORIGINAL,t,SENIAL,t,REFERENCIA1)
plt.ylabel('Señal original [V]')
plt.xlabel('Tiempo [s]')
plt.grid(True)
plt.legend(['Señal con ruido','Señal','Referencia en fase'])


plt.subplot(3,2,2)
Y = fft(ORIGINAL);
frecuencia = np.arange(len(Y))*Fs/(len(Y))
plt.semilogy(frecuencia,np.abs(Y),'-') 
plt.ylabel('Potencia Original ')
plt.xlabel('Frecuencia [Hz]')
plt.grid(True)
plt.xlim([0, 2000])

#PSD
PSD1 = 2 * ORIGINAL * REFERENCIA1
PSD2 = 2 * ORIGINAL * REFERENCIA2

#PSD
plt.subplot(3,2,3)
plt.plot(t,PSD1)
plt.ylabel('Señal PSD [V]')
plt.xlabel('Tiempo [s]')
plt.grid(True)

#FFT PSD
plt.subplot(3,2,4)
Y = fft(PSD1)
frecuencia = np.arange(len(Y))*Fs/(len(Y))
plt.semilogy(frecuencia,np.abs(Y),'-') 
plt.ylabel('Potencia PSD ')
plt.xlabel('Frecuencia [Hz]')
plt.grid(True)
plt.xlim([0, 2000])

#Filtro la señal que sale del PSD 
plt.subplot(3,2,5)

def butter_lowpass_filter(data, cutoff, fs, order):    
    nyq = 0.5 * fs  # Nyquist Frequency
    normal_cutoff = cutoff / nyq
    # Get the filter coefficients 
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = lfilter(b, a, data)
    return y

# Filter requirements.
cutoff = 1/timeconstant  #[Hz] Frecuencia de corte
order = 2       # sin wave can be approx represented as quadratic

PSD1FILTRADA = butter_lowpass_filter(PSD1, cutoff, Fs, order)
PSD2FILTRADA = butter_lowpass_filter(PSD2, cutoff, Fs, order)

#filtrada
plt.plot(t,PSD1FILTRADA)
plt.plot(t,PSD2FILTRADA)
plt.ylabel('PSD Filtrada [V]')
plt.xlabel('Tiempo [s]')
plt.grid(True)
plt.legend(['X ','Y '])

#FFR PDF Filtrada
plt.subplot(3,2,6)
Y = fft(PSD1FILTRADA)
frecuencia = np.arange(len(Y))*Fs/(len(Y))
plt.semilogy(frecuencia,np.abs(Y),'-') 
plt.ylabel('Potencia PSD Filtrada')
plt.xlabel('Frecuencia [Hz]')
plt.grid(True)
plt.xlim([0, 2000])

plt.show()

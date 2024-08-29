import numpy as np
from matplotlib.image import imsave
import matplotlib.pyplot as plt 
import cv2
import serial as ser
import time

def trackTemplate(vs, template, limites):
    '''
    Parameters
    ----------
    vs : cámara
        DESCRIPTION.
    template : string
        Path de la imagen template.
    limites : list
        Extremos para recortar el tubo en la imagen.

    Returns
    -------
    int
        La posición (en px) del extremo superior del template detectado.

    '''
    # Toma foto. Si no puede devuelve None
    im = vs.read()[1]
    if im is None:
        return None
    
    # Corte zona del tubo y pasado a escala de grises y a enteros.
    min_x, max_x, min_y, max_y = limites
    im = im[min_y:max_y, min_x:max_x, :]
    im = np.mean(im, axis=2)
    im = np.asarray(im, uint8)
    
    # Lee el template y lo trackea. Devuelve como posición la esquina superior izquierda.
    template = cv2.imread(template)
    template = np.mean(template, axis=2)
    template = np.asarray(template, uint8)
    res = cv2.matchTemplate(im, template, cv2.TM_CCOEFF)
    top_left = cv2.minMaxLoc(res)[3]
    
    return top_left[0]
    

# Inicialización de la cámara
vs = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Guardado imagen completa, en escala de grises
im = vs.read()[1]
im = np.mean(im, axis=2)
imsave('completa.png', im, cmap='gray')

# Guardado imagen recortada (tubo/template), en escala de grises
im = vs.read()[1]
limites=[0, 640, 100, 300]
min_x, max_x, min_y, max_y = limites
im = im[min_y:max_y, min_x:max_x, :]
im = np.mean(im, axis=2)
imsave('corte.png', im, cmap='gray')

# Ubicación imagen template
template = 'c:/path.to.template.png'

# Inicialización comunicación Arduino (VER COM)
arduino = ser.Serial(port='COM6', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=0.05, xonxoff=0, rtscts=0)
time.sleep(2)

# Apagado ventiladores
valor = 0
arduino.write(bytes(f'a{valor}\n', 'utf-8'))

# Inicialización variables para loop
tiempo = []
posicion = []
duracion = 10  # s
valor = 0
t0 = time.time()

# Loop
while time.time() - t0 < duracion:
    
    tiempo.append(time.time() - t0)
    pos = trackTemplate(vs, template, limites)
    posicion.append(pos)

    # Encendido ventiladores 
    if time.time() - t0 > 5:
        valor = 255
    arduino.write(bytes(f'a{valor}\n', 'utf-8'))
    print(tiempo[-1], posicion[-1], valor)

# Cierre comunicación con Arduino
time.sleep(2)
arduino.close()

# Figura
plt.plot(tiempo, posicion)
plt.xlabel('Tiempo [s]')
plt.ylabel('Posición [px]')

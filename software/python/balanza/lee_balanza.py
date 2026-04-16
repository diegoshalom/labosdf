# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 12:10:41 2024

@author: lpavlov
"""

import serial

ser = serial.Serial(port='COM10')
def leer_balanza():
    ser.write('M'.encode())
    rta = ser.readline()
    peso_g = float(str(rta).split("b'")[1].split('\\r')[0])
    return peso_g

'''
Codigo de Arduino en el HX711:
    

// Calibrating the load cell
#include "HX711.h"

// HX711 circuit wiring
const int LOADCELL_DOUT_PIN = 3;
const int LOADCELL_SCK_PIN = 2;
char c ;
int numberOfMeasurements = 5 ;
float slope = 1612.17/1514715 ; // gramos/cuentas

HX711 scale;

void setup() {
  Serial.begin(9600);
  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  scale.set_scale();    
  delay(2000);
  scale.tare();
  while (scale.is_ready() == false){
    delay(10);
  }
}

void loop() {
  if (Serial.available() > 0){
    c = Serial.read() ;
    if (c == 'R'){
      if (scale.is_ready()) {
        long reading = scale.get_units(numberOfMeasurements);
        Serial.println(reading);
      } 
      else {
        Serial.println("HX711 not found.");
        delay(1000) ;
      }
    } else if (c == 'M'){
      if (scale.is_ready()) {
        long reading = scale.get_units(numberOfMeasurements);
        Serial.println(reading*slope);
      } 
      else {
        Serial.println("HX711 not found.");
        delay(1000) ;
      }
    } else if (c == 'T'){
      scale.tare() ;
    }
  }
}
        
'''
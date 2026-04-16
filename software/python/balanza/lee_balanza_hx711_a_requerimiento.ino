/*
  Rui Santos
  Complete project details at https://RandomNerdTutorials.com/arduino-load-cell-hx711/
  
  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files.
  
  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.
*/

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

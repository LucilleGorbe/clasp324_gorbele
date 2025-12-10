/*
 * HC-SR04 example sketch
 *
 * https://create.arduino.cc/projecthub/Isaac100/getting-started-with-the-hc-sr04-ultrasonic-sensor-036380
 *
 * by Isaac100
 */

// example sketch for using Neptune Control humidity sensors
// RH101 (reports relative humidity)
// also reports low-resolution temperature (1C resolution)
// Roger De Roo  2025 Nov 04

#include <Wire.h>
// for the Nano, A4 = SDA and A5 = SCL

// pin locations on arduino for HC-SR04 trigger and echo pulses
const int trigPin = 9;
const int echoPin = 10;

const float distance = 95.2; // distance between sensor bases in cm
const float spsound = 343; // speed of sound in m/s at operating temperatures

float duration, windspeed;

void setup() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  // high serial baud rate likely unnecessary
  Serial.begin(115200);
  Wire.begin();
  while (!Serial) yield;
  Serial.print("RH101 starting");
  Serial.println();

  // Set units out
  Serial.println("RH  TEMP  WINDSPEED  ELAPSEDTIME");
  Serial.println("%  degC  cm/s  ms");
}

void loop() {
  float starttime = millis();

  // Send a pulse from trigger on both sensors, measure duration from catching
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH); 
  
  // dist / duration (starts in cm/microsecond convert to cm/s) = sound v + wind v
  windspeed = ((distance)/ duration) * 10000 - spsound; 

  // collect relative humidity and sensor temp data
  float rh=-999., tc=-999.;
  readRH101(&rh,&tc);

  // print out all data to erial monitor
  Serial.print(rh, 4);
  Serial.print("  ");
  Serial.print(tc);
  Serial.print("  ");
  Serial.print(windspeed, 6);
  Serial.print("  ");
  Serial.println(millis() - starttime);
  // delay extra amount to achieve 9 Hz
  delay(100);
}

void readRH101(float *rh, float *tc) {
  // rh:  relative humidity in percent
  // tc:  temperature in degrees Celsius
  const byte RH101addr = 0x40;
  byte c;
  Wire.requestFrom(RH101addr,3);
  c=Wire.read();
  *rh=c;
  c=Wire.read();
  *rh+=(float)c/256;
  c=Wire.read();
  *tc=(float)c;  
}

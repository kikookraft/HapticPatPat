#include <Arduino.h>
#include <Wire.h>
#include <BluetoothSerial.h>
#include <string>

// Initialization of constants for haptic
#define INTERNAL_LED 2 // indicates if connected with server (low active)
#define HAPTIC_LEFT GPIO_NUM_18 // D1
#define HAPTIC_RIGHT GPIO_NUM_4 // D2

static unsigned int haptic_left_level = 0;
static unsigned int haptic_right_level = 0;

// bluetooth initialization
#define CONNECTION_TIMEOUT 5
BluetoothSerial SerialBT;



void setup() {
  pinMode(INTERNAL_LED, OUTPUT);
  pinMode(HAPTIC_LEFT, OUTPUT);
  pinMode(HAPTIC_RIGHT, OUTPUT);

  digitalWrite(HAPTIC_LEFT, LOW);
  digitalWrite(HAPTIC_RIGHT, LOW);

  SerialBT.begin("ESP32-PatPat"); //Bluetooth device name
  SerialBT.setTimeout(CONNECTION_TIMEOUT);
  Serial.begin(9600);
  Serial.println("The device started, now you can pair it with bluetooth!");

  // update parameters to lower the latency

  // Wait for connection
  while (!SerialBT.connected()) {
    delay(100);
    digitalWrite(INTERNAL_LED, HIGH);
    delay(100);
    digitalWrite(INTERNAL_LED, LOW);
  }
  Serial.println("Connected to Bluetooth");

  digitalWrite(HAPTIC_LEFT, HIGH);
  digitalWrite(HAPTIC_RIGHT, HIGH);
  delay(500);
  digitalWrite(HAPTIC_LEFT, LOW);
  digitalWrite(HAPTIC_RIGHT, LOW);
  delay(500);
}

String received = "";

void send (String message) {
  SerialBT.println(message);
}

String receive() {
  if (SerialBT.available()) {
    String received = SerialBT.readString();
    return received;
  }
  return "";
}

void loop() {
  while (!SerialBT.connected()) {
    digitalWrite(HAPTIC_LEFT, LOW);
    digitalWrite(HAPTIC_RIGHT, LOW);
    delay(100);
    digitalWrite(INTERNAL_LED, HIGH);
    delay(100);
    digitalWrite(INTERNAL_LED, LOW);
  }

  received = receive();
  
  if (received[0] == 'v') {
    // convert string to int (v 0f 0f) -> 0x0F left and 0x0F right
    haptic_left_level = strtol(received.substring(2, 4).c_str(), NULL, 16);
    haptic_right_level = strtol(received.substring(5, 7).c_str(), NULL, 16);
    Serial.println("Left: " + String(haptic_left_level) + " Right: " + String(haptic_right_level));
  } else if (received[0] == 'k') {
    // send keep_alive package when asked
    send("k");
  }
  
  // create PWM signal for both haptic sensors 
  analogWrite(HAPTIC_LEFT, haptic_left_level);
  analogWrite(HAPTIC_RIGHT, haptic_right_level);
  Serial.println("Left: " + String(haptic_left_level) + " Right: " + String(haptic_right_level));
  delay(5);
}
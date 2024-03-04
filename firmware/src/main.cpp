#include <Arduino.h>
#include <Wire.h>
#include <BluetoothSerial.h>
#include <string>

// Initialization of constants for haptic
#define INTERNAL_LED 2 // indicates if connected with server (low active)
#define HAPTIC_LEFT GPIO_NUM_5 // D1
#define HAPTIC_RIGHT GPIO_NUM_4 // D4

// Initialization of variables for haptic
static unsigned int haptic_left_level = 0;
static unsigned int haptic_right_level = 0;

// bluetooth initialization
#define CONNECTION_TIMEOUT 5 // allow lower latency
BluetoothSerial SerialBT;

// the variable to store the received data
String received = "";

void send (String message) {
  // send message to the server
  SerialBT.println(message);
}

String receive() {
  // receive message from the server
  if (SerialBT.available()) {
    String received = SerialBT.readString();
    return received;
  }
  // return empty string if no message is available
  return "";
}

void setup() {
  // initialize the digital pin as an output.
  pinMode(INTERNAL_LED, OUTPUT);
  pinMode(HAPTIC_LEFT, OUTPUT);
  pinMode(HAPTIC_RIGHT, OUTPUT);

  // initialize the digital pin with an off state
  digitalWrite(HAPTIC_LEFT, LOW);
  digitalWrite(HAPTIC_RIGHT, LOW);

  // initialize serial communication for debugging and bluetooth
  SerialBT.begin("ESP32-PatPat"); //Bluetooth device name
  SerialBT.setTimeout(CONNECTION_TIMEOUT);
  Serial.begin(9600);
  Serial.println("The device started, now you can pair it with bluetooth!");

  // Wait for connection
  while (!SerialBT.connected()) {
    delay(200);
    digitalWrite(INTERNAL_LED, HIGH);
    delay(200);
    digitalWrite(INTERNAL_LED, LOW);
  }
  Serial.println("Connected to Bluetooth");
}

void loop() {
  while (!SerialBT.connected()) {
    // wait for connection
    digitalWrite(HAPTIC_LEFT, LOW);
    digitalWrite(HAPTIC_RIGHT, LOW);
    delay(200);
    digitalWrite(INTERNAL_LED, HIGH);
    delay(200);
    digitalWrite(INTERNAL_LED, LOW);
  }

  // receive message from the server
  received = receive();
  
  if (received[0] == 'v') {
    // vibrate based on the received intensity
    // convert string to int (v 0f 0f) -> 0x0F left and 0x0F right
    haptic_left_level = strtol(received.substring(2, 4).c_str(), NULL, 16);
    haptic_right_level = strtol(received.substring(5, 7).c_str(), NULL, 16);
    Serial.println("Left: " + String(haptic_left_level) + " Right: " + String(haptic_right_level));
  } else if (received[0] == 'k') {
    // send keep_alive package when asked to notifiy the server that the device is still connected
    send("k");
  }
  
  // create PWM signal for both haptic sensors 
  analogWrite(HAPTIC_LEFT, haptic_left_level);
  analogWrite(HAPTIC_RIGHT, haptic_right_level);
  
  // delay to prevent spamming the server
  delay(10);
}
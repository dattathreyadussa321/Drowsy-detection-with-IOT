
const int ledPin = 13;
char receivedChar;

void setup() {
  Serial.begin(9600);
 
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, HIGH); // LED on by default
}

void loop() {
  if (Serial.available() > 0) {
    receivedChar = Serial.read();
    if (receivedChar == 'A') {
      digitalWrite(ledPin, HIGH);   // LED off
            // Buzzer on
    } else if (receivedChar == 'B') {
              // Buzzer off
      digitalWrite(ledPin, LOW);  // LED on
    }
  }
}

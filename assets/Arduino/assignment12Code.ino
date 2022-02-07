#define redLED 12
#define greenLED 11
#define whiteLED 10
#define buttonPort 9
#define debounceTime 500
#define longPressTime 1000

int state = 0;
/*
  0: all off
    1: red only
    2: green only
    3: white only
    4: all on
*/
unsigned long lastDebounceTime = millis();
unsigned long startHoldMillis;
boolean lastButtonState = false;
boolean buttonState;

void decodeState(int s) {
  // first reset all leds to starting state (off)
  digitalWrite(redLED, LOW);
  digitalWrite(greenLED, LOW);
  digitalWrite(whiteLED, LOW);

  switch (s) {
    case 1:
      digitalWrite(redLED, (millis() / 100) % 2 == 0);
      break;
    case 2:
      digitalWrite(greenLED, (millis() / 100) % 2 == 0);
      break;
    case 3:
      digitalWrite(whiteLED, (millis() / 100) % 2 == 0);
      break;
    case 4:
      digitalWrite(redLED, (millis() / 100) % 2 == 0);
      digitalWrite(greenLED, (millis() / 100) % 2 == 0);
      digitalWrite(whiteLED, (millis() / 100) % 2 == 0);
      break;
  }
}

int checkSwitch() {
  // return 0 for off, 1 for normal press, 2 for long press
  buttonState = !digitalRead(buttonPort);
  int returnValue = 0;

  // button has since changed state
  if (lastButtonState != buttonState) {
    if (buttonState) {
      // button switched into the on state, check
      // if button state is constant after the debounce timing
      if (millis() > lastDebounceTime + 100) {
        lastDebounceTime = millis();
        startHoldMillis = millis();
      }
    } else {
      // button transitioned into the off position
      if (millis() > startHoldMillis + longPressTime) {
        returnValue = 2;
      } else {
        returnValue = 1;
      }
    }
  }

  // save the current state of the button as the last state
  lastButtonState = buttonState;
  return returnValue;
}

void setup()
{
  // LED
  pinMode(redLED, OUTPUT);
  pinMode(greenLED, OUTPUT);
  pinMode(whiteLED, OUTPUT);

  // since we are using a internal pullup resistor
  // when the switch is open it will be HIGH
  // hence we use the exclaimation mark to invert the value
  // to LOW, which is more intuitive

  // button
  pinMode(buttonPort, INPUT_PULLUP);

  Serial.begin(9600);
}

void loop()
{
  switch (checkSwitch()) {
    case 1:
      state = (state + 1) % 5;
      break;
    case 2:
      state = 0;
      break;
  }

  decodeState(state);
}

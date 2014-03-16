/*
   Driver for catlight
 */

const int RED_PIN = 9;
const int GREEN_PIN = 10;
const int BLUE_PIN = 11;

uint8_t buffer[6];

void setup()
{
    memset(buffer,0,sizeof(buffer));

    Serial.begin(115200);
    Serial.flush();

    pinMode(RED_PIN, OUTPUT);
    pinMode(GREEN_PIN, OUTPUT);
    pinMode(BLUE_PIN, OUTPUT);
}

void loop()
{
    if (Serial.available() >= 5) {
        Serial.readBytes((char*)buffer,5);
        if (buffer[0] == 0x02 && buffer[4] == 0x03) {
            analogWrite(RED_PIN, buffer[1]);
            analogWrite(GREEN_PIN, buffer[2]);
            analogWrite(BLUE_PIN, buffer[3]);
        }
    }
}

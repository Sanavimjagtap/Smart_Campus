#include <WiFi.h>
#include <HTTPClient.h>

#include <DHT.h>

#include <ESP32Servo.h>

// -------------------- WIFI --------------------
String lightsStatus = "OFF";
String occupancyStatus = "available";

const char* ssid = "Galaxy A14 5G";
const char* password = "sanavi0110";

const char* server =
"http://10.172.59.89:5000/update_classroom";

// -------------------- PINS --------------------

#define PIR_PIN      5
#define MQ135_PIN    34
#define DHT_PIN      4

#define LED1         22
#define LED2         23
#define LED3         19

#define SERVO_PIN    18
#define RELAY_PIN    27

// -------------------- DHT --------------------

#define DHTTYPE DHT11

DHT dht(DHT_PIN, DHTTYPE);

// -------------------- SERVO --------------------

Servo windowServo;

// -------------------- VARIABLES --------------------

float temperature = 0;

int airValue = 0;

bool motionDetected = false;

bool roomOccupied = false;

bool lightsOn = false;

bool windowOpen = false;

bool fireDetected = false;

bool doorUnlocked = false;

// -------------------- TIMERS --------------------

unsigned long lastMotion = 0;

const unsigned long LIGHT_DELAY = 10000;

// -------------------- THRESHOLDS --------------------

const float TEMP_THRESHOLD = 30.0;

const int AIR_THRESHOLD = 1500;

const int FIRE_THRESHOLD = 300;

// -------------------- FUNCTIONS --------------------

void connectWiFi();

void readSensors();

void handleOccupancy();

void handleVentilation();

void handleFire();

void sendStatus();


// ====================================================

void setup()
{

    Serial.begin(115200);

    pinMode(PIR_PIN, INPUT);

    pinMode(LED1, OUTPUT);
    pinMode(LED2, OUTPUT);
    pinMode(LED3, OUTPUT);

    pinMode(RELAY_PIN, OUTPUT);

    digitalWrite(LED1, LOW);
    digitalWrite(LED2, LOW);
    digitalWrite(LED3, LOW);

    digitalWrite(RELAY_PIN, LOW);

    dht.begin();

    windowServo.attach(SERVO_PIN);

    windowServo.write(0);

    connectWiFi();

}
void connectWiFi()
{
    WiFi.begin(ssid, password);

    Serial.print("Connecting");

    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }

    Serial.println();
    Serial.println("WiFi Connected!");

    Serial.print("ESP32 IP : ");

    Serial.println(WiFi.localIP());
}

void readSensors()
{
    temperature = dht.readTemperature();

    airValue = analogRead(MQ135_PIN);

    motionDetected = digitalRead(PIR_PIN);

    Serial.println("--------------------------");

    Serial.print("Temperature : ");
    Serial.println(temperature);

    Serial.print("Air Value : ");
    Serial.println(airValue);

    Serial.print("Motion : ");
    Serial.println(motionDetected);

    Serial.println("--------------------------");
}
void handleOccupancy()
{
    if (motionDetected)
    {
        roomOccupied = true;

        lightsOn = true;

        occupancyStatus = "occupied";
        lightsStatus = "ON";

        lastMotion = millis();

        digitalWrite(LED1, HIGH);
        digitalWrite(LED2, HIGH);
        digitalWrite(LED3, HIGH);
    }

    else
    {
        if (millis() - lastMotion > LIGHT_DELAY)
        {
            roomOccupied = false;

            lightsOn = false;

            occupancyStatus = "available";
            lightsStatus = "OFF";

            digitalWrite(LED1, LOW);
            digitalWrite(LED2, LOW);
            digitalWrite(LED3, LOW);
        }
    }


    Serial.print("Room : ");

    Serial.println(occupancyStatus);


    Serial.print("Lights : ");

    Serial.println(lightsStatus);
}
void handleVentilation()
{
    // Open window if temperature OR CO2 is high

    if (temperature > TEMP_THRESHOLD || airValue > AIR_THRESHOLD)
    {
        if (!windowOpen)
        {
            windowServo.write(90);

            windowOpen = true;

            Serial.println("Window Opened");
        }
    }

    else
    {
        if (windowOpen)
        {
            windowServo.write(0);

            windowOpen = false;

            Serial.println("Window Closed");
        }
    }

    Serial.print("Window : ");

    if(windowOpen)
        Serial.println("Open");

    else
        Serial.println("Closed");
}

void handleFire()
{
    if (airValue > FIRE_THRESHOLD)
    {
        if (!fireDetected)
        {
            fireDetected = true;

            Serial.println();
            Serial.println("################################");
            Serial.println("######## FIRE DETECTED #########");
            Serial.println("################################");

            // Open Window
            windowServo.write(90);
            windowOpen = true;

            // Unlock Door
            digitalWrite(RELAY_PIN, HIGH);

            doorUnlocked = true;

            Serial.println("Door Unlocked");

            Serial.println("Emergency Ventilation Activated");
        }
    }

    else
    {
        if (fireDetected)
        {
            fireDetected = false;

            Serial.println("Fire Cleared");

            digitalWrite(RELAY_PIN, LOW);

            doorUnlocked = false;

            Serial.println("Door Locked");
        }
    }
}

void sendStatus()
{
    if(WiFi.status()==WL_CONNECTED)
    {
        HTTPClient http;

        http.begin(server);

        http.addHeader(
            "Content-Type",
            "application/json"
        );


        String json = "{";
        
        json += "\"room\":\"AC-1\",";
        json += "\"occupancy\":\"" + occupancyStatus + "\",";
        json += "\"lights\":\"" + lightsStatus + "\",";
        json += "\"temperature\":" + String(temperature) + ",";
        json += "\"air\":" + String(airValue) + ",";
        
        json += "\"window\":\"";
        json += (windowOpen ? "Open" : "Closed");
        json += "\",";

        json += "\"fire\":\"";
        json += (fireDetected ? "FIRE" : "SAFE");
        json += "\",";

        json += "\"door\":\"";
        json += (doorUnlocked ? "Unlocked" : "Locked");
        json += "\"";

        json += "}";


        Serial.println("JSON:");
        Serial.println(json);


        int response = http.POST(json);

        Serial.print("HTTP Code: ");
        Serial.println(response);


        http.end();
    }
}
void loop()
{

    readSensors();

    handleFire();

    if(!fireDetected)
    {
        handleVentilation();

        handleOccupancy();
    }

    sendStatus();

    delay(500);

}
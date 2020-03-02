#include "HX711.h"
#include <DHT.h>;
#define DHTPIN 7     // what pin we're connected to
#define DHTTYPE DHT22   // DHT 22  (AM2302)

DHT dht(DHTPIN, DHTTYPE);
HX711 scale(4, 3);

float calibration_factor = 870;//his calibration factor is adjusted according to my load cell
float units;
int chk;
float hum;  //Stores humidity value
float temp; 

//float ounces;

char dataString[50] = {0};
//int a =0; 

void setup() {
  Serial.begin(9600);
  dht.begin();
  scale.set_scale();
  scale.tare();

  long zero_factor = scale.read_average();
}
void dht_sensor(){
	  hum = dht.readHumidity();
    temp= dht.readTemperature();
	  //Serial.print("Humidity: ");
    Serial.print(hum);
    Serial.print(",");
    Serial.print(temp);
    Serial.print(",");
    delay(1000);
}

void hx711_sensor(){
  scale.set_scale(calibration_factor); //Adjust to this calibration factor

  units = scale.get_units(), 10;
  if (units < 0){
    units = 0.00;
  }
  Serial.print(units);
  Serial.print(",");
  delay(1000);
}

void loop() {  
  hx711_sensor();
  dht_sensor();
}
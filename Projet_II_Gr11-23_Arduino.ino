// Inclut la bibliothèque Arduino Stepper.h:
#include <Stepper.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Définit le nombre de pas par rotation:
const int stepsPerRevolution = 512;
// Câblage:
// Broche 8 à IN1 sur le pilote ULN2003
// Broche 9 à IN2 sur le pilote ULN2003
// Broche 10 à IN3 sur le pilote ULN2003
// Broche 11 à IN4 sur le pilote ULN2003
// Créez un objet stepper appelé 'myStepper', notez l'ordre des broches:

int led = A2;

//Init joystick variables
const int SW_pin = 4;
const int X_pin = 2;
const int Y_pin = 3;

//Init LCD variables
LiquidCrystal_I2C lcd(0x27,20,4);


Stepper myStepper = Stepper ( stepsPerRevolution, 8, 10, 9, 11 ) ;

//Nombre de boissons restants par utilisateur
int leftUser1 = 12;
int leftUser2 = 3;
int leftUser3 = 30;

int Metal = 0; //0 =pas de métal, 1 = métal

void setup() {

//contenu de l'initialisation
  pinMode(led, OUTPUT); //L1 est une broche de sortie
  pinMode(A1, INPUT); // BP est une broche d'entree
  pinMode(A0, INPUT);

  pinMode(SW_pin, INPUT);
  digitalWrite(SW_pin, HIGH);

  lcd.init(); // initialisation de l'afficheur

// Réglez la vitesse sur 5 tr / min:
  myStepper.setSpeed(15);
// Commencez la communication série à une vitesse de transmission de 9600:
  Serial.begin(9600);


    //Initialisation de l'affichage de l'écran
    lcd.clear();

    lcd.setCursor(2, 0);
    lcd.print("Select Profile");

    lcd.setCursor(2, 1);
    lcd.print("User 1");
    lcd.setCursor(10, 1);
    lcd.print(String(leftUser1));
    lcd.setCursor(13, 1);
    lcd.print("left");


    lcd.setCursor(2, 2);
    lcd.print("User 2");
    lcd.setCursor(10, 2);
    lcd.print(String(leftUser2));
    lcd.setCursor(13, 2);
    lcd.print("left");


    lcd.setCursor(2, 3);
    lcd.print("User 3");
    lcd.setCursor(10, 3);
    lcd.print(String(leftUser3));
    lcd.setCursor(13, 3);
    lcd.print("left");

}
//initialisation des variables
int cursorX = 0;
int cursorY = 1;
int SelectedProfile = 0;
String actualScreen = "Home";

int i = 0;

void loop() {
  lcd.backlight();

  //Interprétation du signal de sortie du circuit
  if(analogRead(A0) >=100){
    Metal = 1;
  }else{
    i = i + 1;
    if(i>=200){
      i = 0;
      Metal = 0;
    }
  }

  //déplacement curseur
  if(digitalRead(SW_pin) == 0){
    lcd.setCursor(cursorX,cursorY);
    lcd.print("0");
    SelectedProfile = cursorY;
    delay(500);
  }
  if(analogRead(Y_pin)<=200){
    lcd.setCursor(cursorX, cursorY);
    lcd.print(" ");
    cursorY = cursorY - 1;
    lcd.setCursor(cursorX,cursorY);
    lcd.print("X");
    delay(500);
  }

    if(analogRead(Y_pin)>=900){
    lcd.setCursor(cursorX, cursorY);
    lcd.print(" ");
    cursorY = cursorY + 1;
    lcd.setCursor(cursorX, cursorY);
    lcd.print("X");
    delay(500);

  }
  
  /*if(analogRead(X_pin)>=100){
    cursorX = cursorX + 1;
    lcd.setCursor(cursorX, cursorY);
    lcd.print("X");
    delay(500);
  }
    if(analogRead(X_pin)<=1){
    cursorX = cursorX - 1;
    lcd.setCursor(cursorX, cursorY);
    lcd.print("X");
    delay(500);

  }*/
// Étape d'une révolution dans une direction:
 
  if(analogRead(A1) < 500 and Metal == 0) // Si test est à l'état bas
  {
    if(SelectedProfile == 1 and leftUser1>0 or SelectedProfile==2 and leftUser2>0 or SelectedProfile==3 and leftUser3>0){
      digitalWrite(led, HIGH); // Allumer L1
      myStepper.step(stepsPerRevolution);
      int j = 0;
      int arrived = 0;
      while(analogRead(A0)<= 100 and j<=1500 and arrived == 0){
        j ++;
        delay(10);
        if(analogRead(A0)>=100){
          arrived = 1;
        }        
      }
      if(arrived == 1){
        if(SelectedProfile == 1){
          leftUser1 = leftUser1 - 1;
          lcd.setCursor(10, 1);
          lcd.print("  ");
          lcd.setCursor(10, 1);
          lcd.print(String(leftUser1));
        }
        if(SelectedProfile == 2){
          leftUser2 = leftUser2 -1;
          lcd.setCursor(10, 2);
          lcd.print("  ");
          lcd.setCursor(10, 2);
          lcd.print(String(leftUser2));
        }
        if(SelectedProfile == 3){
          leftUser3 = leftUser3 - 1;
          lcd.setCursor(10, 3);
          lcd.print("  ");
          lcd.setCursor(10, 3);
          lcd.print(String(leftUser3));
        }
      }     
    SelectedProfile = 0;    
    }
  }
  else // Sinon
  {
    digitalWrite(led, LOW); // Eteindre L1
  }



// // Étape d'une révolution dans l'autre sens:
// Serial.println("counterclockwise");
//   myStepper.step(-stepsPerRevolution);
//   delay(500);
}
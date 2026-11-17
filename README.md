# Código do Hardware - Sensor de Estacionamento (Arduino)

Este repositório contém o firmware desenvolvido para o **Arduino Uno**, responsável por realizar a leitura de distância utilizando um sensor ultrassônico (**HC-SR04**) e acionar os alertas locais (LED RGB e Buzzer).

## Mapeamento de Pinos
* **Pino 6:** Echo (Sensor Ultrassônico)
* **Pino 7:** Trigger (Sensor Ultrassônico)
* **Pino 8:** Buzzer Piezoelétrico
* **Pino 9:** LED RGB - Canal Azul
* **Pino 10:** LED RGB - Canal Verde
* **Pino 11:** LED RGB - Canal Vermelho

## Faixas de Operação
* **Acima de 30 cm:** Vaga Livre (LED Verde aceso, Buzzer desligado).
* **Entre 30 cm e 15 cm:** Veículo Manobrando (LED Amarelo aceso, Buzzer desligado).
* **Entre 15 cm e 7 cm:** Veículo Estacionado na posição ideal (LED Azul aceso, Buzzer desligado).
* **Abaixo de 7 cm:** Alerta de Perigo / Risco de Colisão (LED Vermelho aceso, Buzzer acionado a 1000 Hz).

## Código-Fonte (`Projeto.ino`)

```cpp
const int LEDvermelho = 11;
const int LEDverde = 10;
const int LEDazul = 9;

const int buzzer = 8;
const int trig = 7;
const int echo = 6;

void setup()
{
  pinMode(LEDvermelho, OUTPUT);
  pinMode(LEDverde, OUTPUT);
  pinMode(LEDazul, OUTPUT);
  pinMode(buzzer, OUTPUT);
 
  pinMode(trig, OUTPUT);
  pinMode(echo, INPUT);
 
  Serial.begin(9600);
}

void loop(){
  digitalWrite(trig, LOW);
  delayMicroseconds(2);
  digitalWrite(trig, HIGH);
  delayMicroseconds(10);
  digitalWrite(trig, LOW);
 
  long duracao = pulseIn(echo, HIGH);
  int distancia = duracao * 0.034 / 2;

  Serial.print("Distancia: ");
  Serial.print(distancia);
  Serial.println(" cm");
 
  if(distancia > 30){
    analogWrite(LEDvermelho, 0);
    analogWrite(LEDverde, 255);
    analogWrite(LEDazul, 0);
    noTone(buzzer);
  }
  else if(distancia <= 30 && distancia >= 15){
    analogWrite(LEDvermelho, 255);
    analogWrite(LEDverde, 255);
    analogWrite(LEDazul, 0);
    noTone(buzzer);
  }
  else if(distancia < 15 && distancia >= 7){
    analogWrite(LEDvermelho, 0);
    analogWrite(LEDverde, 0);
    analogWrite(LEDazul, 255);
    noTone(buzzer);
  }
  else if(distancia < 7){
    analogWrite(LEDvermelho, 255);
    analogWrite(LEDverde, 0);
    analogWrite(LEDazul, 0);
    tone(buzzer, 1000);
  }
  delay(100);
}
```
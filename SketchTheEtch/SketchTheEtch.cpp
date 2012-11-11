#include "Arduino.h"
#include "LocalLibrary.h"

void setup() {
    for (int i = 4; i <= 11; i++) {
        pinMode(i, OUTPUT);
    }
    pinMode(13, OUTPUT);
    
    pinMode(2, INPUT);
    pinMode(3, INPUT);
    pinMode(12, INPUT_PULLUP);
    Serial.begin(9600);
}

const int PIN_COUNT = 4;
const int RIGHT_ORDER[] = {8,9,10,11};
const int LEFT_ORDER[] = {11,10,9,8};
const int UP_ORDER[] = {4,5,6,7};
const int DOWN_ORDER[] = {7,6,5,4};

void stopHorizontal() {
    for (int i = 0; i < PIN_COUNT; i++) {
        digitalWrite(RIGHT_ORDER[i], LOW);
    }
}

void stopVertical() {
    for (int i = 0; i < PIN_COUNT; i++) {
        digitalWrite(UP_ORDER[i], LOW);
    }
}

void stopAll() {
    stopVertical();
    stopHorizontal();
}

void motorReset() {
    for (int i=0; i<10; i++) {
        digitalWrite(8, LOW);
        digitalWrite(9, HIGH);
        delay(10);
        digitalWrite(8, HIGH);
        digitalWrite(9, LOW);
        delay(10);
    }
    stopAll();
}

void driveMotor(const int order[], int pause) {
//    for (int i=0; i<PIN_COUNT; i++) {
//    }
    digitalWrite(order[2], LOW);
    digitalWrite(order[0], HIGH);
    delay(pause);
    digitalWrite(order[3], LOW);
    digitalWrite(order[1], HIGH);
    delay(pause);
    digitalWrite(order[0], LOW);
    digitalWrite(order[2], HIGH);
    delay(pause);
    digitalWrite(order[1], LOW);
    digitalWrite(order[3], HIGH);
    delay(pause);
}

// 4-7
void driveDown(int pause=5) {
    driveMotor(DOWN_ORDER, pause);
}

void driveUp(int pause=5) {
    driveMotor(UP_ORDER, pause);
}

// 8-11
void driveLeft(int pause=5) {
    driveMotor(LEFT_ORDER, pause);
}

void driveRight(int pause=5) {
    driveMotor(RIGHT_ORDER, pause);
}

int clamp(int value, int lowerBound, int upperBound) {
    if (value < lowerBound) {
        return lowerBound;
    }
    else if (value > upperBound) {
        return upperBound;
    }
    else {
        return value;
    }
}

int blockingRead() {
    int result = -1;
    while (result == -1) {
        result = Serial.read();
    }
    return result;
}

int pauseTime = 5;
void loop() {
    int result = digitalRead(12);
    digitalWrite(13, result);
    if (result == HIGH) {
        int data = Serial.read();
        if (data >= 0) {
            if (data == 'd') {
                driveDown(pauseTime);
            }
            else if (data == 'u') {
                driveUp(pauseTime);
            }
            else if (data == 'l') {
                driveLeft(pauseTime);
            }
            else if (data == 'r') {
                driveRight(pauseTime);
            }
            else if (data == 's') {
                stopAll();
            }
            else if (data == 'q') {
                int result = blockingRead();
                pauseTime = clamp(result, 5, 200);
            }
            else if (data == 'x') {
                int result = blockingRead();
                if (result == 0) {
                    Serial.print("pauseTime: ");
                    Serial.println(pauseTime);
                }
                else if (result == 1) {
                    motorReset();
                    Serial.println("motorReset()");
                }
                else {
                    Serial.println("Unknown 'x' command");
                }
            }
        }
    }
    else {
        driveRight();
    }
}

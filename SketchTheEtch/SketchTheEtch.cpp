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
const int* ALL_DIRS[] = {
    RIGHT_ORDER,
    LEFT_ORDER,
    UP_ORDER,
    DOWN_ORDER
};

enum DirectionOrder {
    kRightOrder = 0,
    kLeftOrder = 1,
    kUpOrder = 2,
    kDownOrder = 3
};

/**
 speed = [0, 200]
 delay = [5, 204]
 */
int speedToPause(int speed) {
    if (speed == 0) {
        return 0;
    }
    else {
        return 205 - speed;
    }
}

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

void driveMotor(const int order[], int speed) {
    int pause = speedToPause(speed);
    if (pause == 0) {
        for (int i=0; i<PIN_COUNT; i++) {
            digitalWrite(order[i], LOW);
        }
    }
    else {
        int lowIdx = 2;
        int highIdx = 0;
        for (int i=0; i<PIN_COUNT; i++) {
            digitalWrite(order[lowIdx], LOW);
            digitalWrite(order[highIdx], HIGH);
            lowIdx++;
            highIdx++;
            lowIdx = lowIdx % PIN_COUNT;
            highIdx = highIdx % PIN_COUNT;
            delay(pause);
        }
    }
}

typedef void (*DriveFunc)(int);

// 4-7
void driveDown(int speed=200) {
    driveMotor(DOWN_ORDER, speed);
}

void driveUp(int speed=200) {
    driveMotor(UP_ORDER, speed);
}

// 8-11
void driveLeft(int speed=200) {
    driveMotor(LEFT_ORDER, speed);
}

void driveRight(int speed=200) {
    driveMotor(RIGHT_ORDER, speed);
}

const DriveFunc DRIVE_FUNC_LOOKUP[] = {
    driveRight,
    driveLeft,
    driveUp,
    driveDown
};

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

int pauseTime = 200;
void loop() {
    int result = digitalRead(12);
    digitalWrite(13, result);
    if (result == HIGH) {
        int data = Serial.read();
        if (data >= 0) {
            if (data >= 0 && data <= 3) {
                const int* dir = ALL_DIRS[data];
                int pause = speedToPause(blockingRead());
                if (pause == 0) {
                    if (data == 0 || data == 1) {
                        stopHorizontal();
                    }
                    else {
                        stopVertical();
                    }
                }
                else {
                    driveMotor(dir, pause);
                }
            }
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
            else if (data == 'v') {
                int dir1 = blockingRead();
                int dir1StepCount = blockingRead();
                int dir2 = blockingRead();
                int dir2StepCount = blockingRead();
                
                const int SPEED = 200;
                
                // Make sure the vector includes two directions
                if ( ((dir1 == kLeftOrder || dir1 == kRightOrder) && (dir2 == kUpOrder || dir2 == kDownOrder)) ||
                     ((dir2 == kLeftOrder || dir2 == kRightOrder) && (dir1 == kUpOrder || dir1 == kDownOrder))) {
                    
                    int maxStepCount = 0;
                    int minStepCount = 0;
                    DriveFunc driveMax = NULL;
                    DriveFunc driveMin = NULL;
                    if (dir1StepCount > dir2StepCount) {
                        maxStepCount = dir1StepCount;
                        minStepCount = dir2StepCount;
                        driveMax = DRIVE_FUNC_LOOKUP[dir1];
                        driveMin = DRIVE_FUNC_LOOKUP[dir2];
                    }
                    else {
                        maxStepCount = dir2StepCount;
                        minStepCount = dir1StepCount;
                        driveMax = DRIVE_FUNC_LOOKUP[dir2];
                        driveMin = DRIVE_FUNC_LOOKUP[dir1];
                    }
                    
                    if (minStepCount == 0) {
                        for (int i=0; i<maxStepCount; i++) {
                            driveMax(SPEED);
                        }
                    }
                    else { // minStepCount > 0
                        // Number of sections we want to break the long direction of the line into
                        // Eg: 10:1 ratio we would break it into two pieces of length 5 with an
                        // offset of 1
                        int numLineSections = minStepCount + 1;
                        
                        // Approimate segment length
                        int segmentLength = maxStepCount / numLineSections;
                        
                        // Total number of steps in the max direction that are not accounted for with segmentLength
                        int remainder = maxStepCount % numLineSections;
                        
                        // case where it was 1:1 ratio
                        if (segmentLength == 0) {
                            segmentLength = 1;
                            remainder = 0;
                        }
                        
                        int minCounter = numLineSections;
                        for (int i=0; i<numLineSections; i++) {
                            if (minCounter <= remainder) {
                                driveMax(SPEED);
                            }
                            for (int j=0; j<segmentLength; j++) {
                                driveMax(SPEED);
                            }
                            driveMin(SPEED);
                            minCounter -= remainder;
                            if (minCounter <= 0) {
                                minCounter += numLineSections;
                            }
                        }
                    }
                }
            }
        }
    }
    else {
        for (int i=0; i<50; i++) {
            driveRight();
            driveUp();
        }
        for (int i=0; i<50; i++) {
            driveLeft();
            driveDown();
        }
    }
}

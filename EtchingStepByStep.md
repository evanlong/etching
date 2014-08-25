# Build your own automated Etch-a-Sketch

![Reference Mona](/ref/mona.jpg) and ![Result Mona](/result/mona.jpg)
Once completed the Etch-a-Sketch should be able to draw arbitrary black and white images. 

## Getting Started

Start by making sure you have all the parts listed here:

1. 1x [Etch-a-Sketch](http://www.amazon.com/Classic-Etch-Sketch-Magic-Screen/dp/B00000J0HG/)
2. 1x [Arduino UNO](http://www.adafruit.com/products/50)
3. 2x [Stepper Motors](https://www.adafruit.com/products/918)
4. 1x 12V Power Supply for stepper motors. An old PC power supply works perfectly for this.
5. 1x [ULN2803](http://www.digikey.com/product-detail/en/ULN2803A/497-2356-5-ND/599591)
6. 1x [Breadboard](http://www.adafruit.com/products/64)
7. 1x Foot of rubber tubing. It should have a 3/16in inner diameter and outer diameter of about 5/16in.
8. 2x [Motor Mounts](http://www.shapeways.com/model/848459/motor-mount-r2.html)
9. Small zip ties (variety pack will cost <$10 at a local hardware store)
10. Gorilla Glue (local hardware store)
12. These [breadboard wires](http://www.adafruit.com/products/153) also work well for hooking it all up.

## Mounting Motors

1. Start by removing the white nobs from the Etch-a-Sketch. A flathead screwdriver can be used to pry them off. (picture of end result)
2. Place the motor mounts on the Etch-a-Sketch. (picture of the result)
3. Now place the motors on the mounts with the wires directed towards the screen. The poles on each mount may need to be sanded down before the motor will fit. Once everything is in place the it should look like this: (picture of end result). When you have verified the motors can be properly positioned remove them from the mounts.
5. Now cutut off two pieces of rubber tubing. Each should be 17 mm long.
6. Place Gorilla Glue on the motor shaft and slide tubing over the shaft. Use a small zip tie to ensure a tight fit with the tubing and the motor shaft. Let the glue dry for about 5 minutes. Once it is set twist the motor shaft back and forth. This breaks any glue sticking to the motor's surface. 
7. Place the motor back on the mount. The tubing should slide over the nob and connect the motor shaft to the nob. Use another zip tie to ensure a tight fit with the tubing and the nob.

## Wiring

![schematic](/schematic.jpg)

The digital out pins on the Arduino do not provide enough voltage for the stepper motors. We use the ULN2803 to switch up to the 12V required by the motors. Ensure the 12V power supply is connected to COM (positive) and GND (negative).

Once everything is wired up it should look something like this:
![all wired up](/wiredup.jpg)

## Software

1. First checkout all the source code
2. Next use the [Arduino Software](http://arduino.cc/en/Main/Software) to build and install the [SketchTheEtch.cpp](http://blah/arduino/SketchTheEtch/SketchTheEtch.cpp) on the Arduino.
3. Make sure the following python depedencies are install: Pillow (a PIL replacement) and pyserial. Both can be installed with pip:

		pip install pyserial
		pip install Pillow
		
4. Now run `python ControlScripts/control.py /dev/tty.PathToUsbDevice`. The `/dev/tty.PathToUsbDevice` will be the same path selected in the Arduino software. This script is used for positioning and testing the device. Here is a basic set of commands that can be issued at the prompt:

		d,c> d 40 #drives the head down 40 pixels
		d,c> r 20 #drives the head down 40 pixels
		d, u, l, r can all be used followed by an integer indicating the number of points to drive
		
		d,c> s #powers down the coils in the motors
		
		d,c> vtest #draws a series of shrinking circles
		
The Arduino Firmware works by receiving a vector to draw. It then draws that vector and sends a message back the the python script indicating it is ready for the next command. The `Image
# IoT Smart Meter and Smart Device Control System

This project is for a raspberry pi to control and track the usage of connected mains devices.  The project is contained within a Flask application with can be found on the localhost at port 8090 when run.

### Running the application
To run the application clone the project and run the app.py file using Python3 on the Raspberry Pi using this command:
```console
python3 app.py
```

### Prerequisites
An installation of Python3

An installation of Flask

### Hardware
1 x Raspberry Pi 3B + - To act as the microcontroller for the system.

1 x ELEGOO 4 Channel Relay Module - To connect mains devices to the Raspberry Pi.

1 x 7” Raspberry Pi LCD Display - To display the smart meter style interface.


###  Pin Numbers and Wiring Diagram
The 7 inch display should be connected via the ribon cable and the GPIO pins should be attached like so:

7 Inch Display | Raspberry Pi GPIO pin (Board number)
 --- | ---
 VCC | 2 or 4 (5V)
 GND | 6, 9, 14, 20, 25, 30, 34 or 39 (Ground)
 SDA | 3
 SCL | 5

The 4 channel relay should be wired like this:

Relay board | Raspberry Pi GPIO pin (Board number)
 --- | ---
 GND | 6, 9, 14, 20, 25, 30, 34 or 39 (Ground)
 IN1 | 22
 IN2 | 24
 IN3 | 26
 IN4 | 32
 VCC | 2 or 4 (5V)


![alt text](https://github.com/KristianTan/IoTSmartMeter/blob/master/Wiring%20Diagram.png "Wiring diagram")

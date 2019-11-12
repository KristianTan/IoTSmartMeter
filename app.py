from flask import Flask, render_template
import datetime
import RPi.GPIO as GPIO

app = Flask(__name__)

# Create a dictionary called pins to store the pin number, name, and pin state:
pins = {
    24: {'name': 'coffee maker', 'state': GPIO.LOW},
    25: {'name': 'lamp', 'state': GPIO.LOW}
}

# Set each pin as an output and make it low:
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)


@app.route("/")
def main():
    # For each pin, read the pin state and store it in the pins dictionary:
    for pin in pins:
        pins[pin]['state'] = GPIO.input(pin)
    # Put the pin dictionary into the template data dictionary:
    template_data = {
        'pins': pins
    }
    # Pass the template data into the template main.html and return it to the user
    return render_template('main.html', **template_data)


@app.route('/button')
def button():
    print("Button press")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090)

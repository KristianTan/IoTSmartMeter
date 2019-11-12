from flask import Flask, render_template
import RPi.GPIO as GPIO
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///energyUsage'
db = SQLAlchemy(app)
db.create_all()
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


# Create dictionary to store pin info
pins = {
    25: {'name': 'Light', 'state': GPIO.LOW}
}

# Setup each pin
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)


@app.route("/")
def main():
    # For each pin, read the pin state and store it in the pins dictionary:
    for pin in pins:
        pins[pin]['state'] = GPIO.input(pin)

    # Set the template data for the HTML template
    template_data = {
        'pins': pins
    }

    return render_template('main.html', **template_data)


@app.route("/<change_pin>")
def toggle_pin(change_pin):
    if change_pin == 'favicon.ico':
        pass

    change_pin = int(change_pin)
    device_name = pins[change_pin]['name']

    # Toggle the selected pin
    GPIO.output(change_pin, not GPIO.input(change_pin))

    message = "Turned " + device_name
    if GPIO.input(change_pin) == 0:
        message += " off."
    else:
        message += " on."

    for pin in pins:
        pins[pin]['state'] = GPIO.input(pin)

    template_data = {
        'message': message,
        'pins': pins
    }

    return render_template('main.html', **template_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090)

from flask import Flask, render_template
# import datetime
import RPi.GPIO as GPIO

app = Flask(__name__)
GPIO.setmode(GPIO.BCM)

# Create a dictionary called pins to store the pin number, name, and pin state:
pins = {
    25: {'name': 'Light', 'state': GPIO.LOW}
}
#
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


# The function below is executed when someone requests a URL with the pin number and action in it:
@app.route("/<change_pin>/<action>")
def action(change_pin, action):
    print("Input value before change: %s" % (GPIO.input(change_pin),))
    change_pin = int(change_pin)
    device_name = pins[change_pin]['name']

    if action == "on":
        GPIO.output(change_pin, GPIO.HIGH)
        message = "Turned " + device_name + " on."
    if action == "off":
        GPIO.output(change_pin, GPIO.LOW)
        message = "Turned " + device_name + " off."
    if action == "toggle":
        GPIO.output(change_pin, not GPIO.input(change_pin))
        message = "Toggled " + device_name + "."

    for pin in pins:
        pins[pin]['state'] = GPIO.input(pin)
    print("Input value after change: %s" % (GPIO.input(change_pin),))

    template_data = {
        'message': message,
        'pins': pins
    }

    return render_template('main.html', **template_data)


@app.route('/button')
def button():
    print("Button press")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090)

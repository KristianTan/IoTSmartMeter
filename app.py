from flask import Flask, render_template
import RPi.GPIO as GPIO
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
# from daily_usage import DailyUsage

app = Flask(__name__)
os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///energyUsage'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
# To suppress warnings
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

db = SQLAlchemy(app)


# TODO: Move this into daily_usage class file
class DailyUsage(db.Model):
    __tablename__ = 'daily_usage'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime, unique=True, nullable=False)
    hours = db.Column(db.String, unique=False)

    def __init__(self, date, hours):
        self.date = date
        self.hours = hours

    def __repr__(self):
        return '<DailyUsage %r>' % self.id


db.create_all()

# Create dictionary to store pin info
pins = {
    25: {'name': 'Light', 'state': GPIO.LOW, 'on_time': None}
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
    # TODO: change_pin is somethimes favicon.co for some reason? Fix
    if change_pin == 'favicon.ico':
        pass

    change_pin = int(change_pin)
    device_name = pins[change_pin]['name']

    # Toggle the selected pin
    GPIO.output(change_pin, not GPIO.input(change_pin))

    message = "Turned " + device_name
    if GPIO.input(change_pin) == 0:
        message += " off."
        if pins[change_pin]['on_time'] is not None:
            uptime = str(datetime.now() - pins[change_pin]['on_time'])
            print("===========")
            print("UPTIME STRING: " + uptime)
            print("===========")
            d = DailyUsage(date=pins[change_pin]['on_time'], hours=uptime)
            db.session.add(d)
            db.session.commit()
            pins[change_pin]['on_time'] = None
            print("==========")
            d = DailyUsage.query.filter_by(id=1)
            print(d)
            print("==========")
    else:
        message += " on."
        pins[change_pin]['on_time'] = datetime.now()

    for pin in pins:
        pins[pin]['state'] = GPIO.input(pin)

    template_data = {
        'message': message,
        'pins': pins
    }

    return render_template('main.html', **template_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090)

from flask import Flask, render_template
import RPi.GPIO as GPIO
from flask_sqlalchemy import SQLAlchemy

import os
from datetime import datetime, date, timedelta
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
    kwhUsed = db.Column(db.Float, unique=False)

    def __init__(self, date, kwhUsed):
        self.date = date
        self.kwhUsed = kwhUsed

    def __repr__(self):
        return '<DailyUsage %r, %r, %r>' % (self.id, self.date, self.kwhUsed)


db.create_all()

# TODO: be able to query db by date
daily_total = 0
latest_entry = db.session.query(DailyUsage).order_by(DailyUsage.id.desc()).first()
if latest_entry:
    latest_entry_date = date(latest_entry.date.year, latest_entry.date.month, latest_entry.date.day)
    if latest_entry_date == datetime.today().date():
        daily_total = format(latest_entry.kwhUsed, '.7f')

todays_cost = format(float(daily_total) * 0.1622, '0.5f')

# Create dictionary to store pin info
pins = {
    25: {'name': 'Light', 'state': GPIO.LOW, 'on_time': None, 'on_date': None, 'Wattage': 15}
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
        'pins': pins,
        'daily_total': daily_total,
        'todays_cost': todays_cost
    }

    return render_template('main.html', **template_data)


@app.route("/toggle/<change_pin>")
def toggle_pin(change_pin):
    change_pin = int(change_pin)
    device_name = pins[change_pin]['name']

    # Toggle the selected pin
    GPIO.output(change_pin, not GPIO.input(change_pin))

    if GPIO.input(change_pin) == 0:
        if pins[change_pin]['on_time'] is not None:
            create_entry(change_pin)
    else:
        pins[change_pin]['on_time'] = datetime.now()
        pins[change_pin]['on_date'] = date.today()

    for pin in pins:
        pins[pin]['state'] = GPIO.input(pin)

    latest_entry = db.session.query(DailyUsage).order_by(DailyUsage.id.desc()).first()
    if latest_entry:
        latest_entry_date = date(latest_entry.date.year, latest_entry.date.month, latest_entry.date.day)
        if latest_entry_date == datetime.today().date():
            daily_total = format(latest_entry.kwhUsed, '.7f')
    else:
        daily_total = 0

    todays_cost = format(float(daily_total) * 0.1622, '0.5f')

    template_data = {
        'pins': pins,
        'daily_total': daily_total,
        'todays_cost': todays_cost
    }

    return render_template('main.html', **template_data)


def create_entry(change_pin):
    latest_entry = db.session.query(DailyUsage).order_by(DailyUsage.id.desc()).first()
    start_time = pins[change_pin]['on_time']
    # Get the elapsed time and strip away milliseconds
    elapsed = int((datetime.now() - start_time).total_seconds())
    start_date = pins[change_pin]['on_date']

    # Formula to calculate kWh based on time and wattage
    kwh = pins[change_pin]['Wattage'] * (elapsed / 3600) / 1000

    # If there is already an entry for today, update on time
    # if latest_entry:
    if latest_entry:
        latest_entry_date = date(latest_entry.date.year, latest_entry.date.month, latest_entry.date.day)
        if latest_entry_date == start_date:
            latest_entry.kwhUsed += kwh
    else:
        # If no entry for today, make one
        entry = DailyUsage(date=start_date, kwhUsed=kwh)
        db.session.add(entry)
    db.session.commit()
    pins[change_pin]['on_time'] = None
    pins[change_pin]['on_date'] = None


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090)

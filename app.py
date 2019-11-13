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
    on_time_seconds = db.Column(db.Integer, unique=False)

    def __init__(self, date, on_time_seconds):
        self.date = date
        self.on_time = on_time_seconds

    def __repr__(self):
        return '<DailyUsage %r, %r, %r>' % (self.id, self.date, self.on_time_seconds)


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


@app.route("/toggle/<change_pin>")
def toggle_pin(change_pin):
    change_pin = int(change_pin)
    device_name = pins[change_pin]['name']

    # Toggle the selected pin
    GPIO.output(change_pin, not GPIO.input(change_pin))

    message = "Turned " + device_name
    if GPIO.input(change_pin) == 0:
        message += " off."
        if pins[change_pin]['on_time'] is not None:
            latest_entry = db.session.query(DailyUsage).order_by(DailyUsage.id.desc()).first()

            start_time = pins[change_pin]['on_time']
            # Get the elapsed time and strip away milliseconds
            elapsed = int((datetime.now() - start_time).total_seconds())

            # Format the time
            start_date_string = datetime.strftime(start_time, '%Y-%m-%d')
            # Create datetime object from formatted time
            start_date = datetime.strptime(start_date_string, '%Y-%m-%d')

            if latest_entry and latest_entry.date == start_date:
                print("SECS BEFORE UPDATE")
                print(latest_entry.on_time_seconds)
                latest_entry.on_time_seconds += elapsed
                print("SECS AFTER UPDATE")
                print(latest_entry.on_time_seconds)
            else:
                print("NEW ENTRY")
                entry = DailyUsage(date=start_date, on_time_seconds=elapsed)
                print(entry.on_time_seconds)
                db.session.add(entry)

            db.session.commit()

            print("=========")
            print(DailyUsage.query.all())
            print("=========")

            pins[change_pin]['on_time'] = None
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

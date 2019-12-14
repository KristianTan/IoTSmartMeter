from flask import Flask, render_template, request
import RPi.GPIO as GPIO
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import asc, desc
import os
from datetime import datetime, date, timedelta
from daily_usage import DailyUsage
# from daily_usage import DailyUsage

app = Flask(__name__)
os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///energyUsage'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
# To suppress warnings
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

db = SQLAlchemy(app)
os.environ['cost_per_kWh'] = '0.1622'


# TODO: Move this into daily_usage class file
# class DailyUsage(db.Model):
#     __tablename__ = 'daily_usage'
#
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     date = db.Column(db.DateTime, unique=True, nullable=False)
#     kwhUsed = db.Column(db.Float, unique=False)
#
#     def __init__(self, date, kwhUsed):
#         self.date = date
#         self.kwhUsed = kwhUsed
#
#     def __repr__(self):
#         return '<DailyUsage %r, %r, %r>' % (self.id, self.date, self.kwhUsed)


def get_todays_usage():
    latest_entry = DailyUsage.query.order_by(desc(DailyUsage.date)).first()
    # latest_entry = db.session.query(DailyUsage).order_by(DailyUsage.date.asc()).first()
    if latest_entry:
        latest_entry_date = date(latest_entry.date.year, latest_entry.date.month, latest_entry.date.day)
        if latest_entry_date == datetime.today().date():
            return format(latest_entry.kwhUsed, '.7f')
    return 0


def get_todays_cost():
    return format(float(get_todays_usage()) * float(os.environ['cost_per_kWh']), '0.5f')


def create_entry(change_pin):
    latest_entry = DailyUsage.query.order_by(desc(DailyUsage.date)).first()
    start_time = pins[change_pin]['on_time']
    elapsed = int((datetime.now() - start_time).total_seconds())
    start_date = pins[change_pin]['on_date']

    # Formula to calculate kWh based on time and wattage
    kwh = pins[change_pin]['wattage'] * (elapsed / 3600) / 1000
    # If there is already an entry for today, update on time
    if latest_entry and date(latest_entry.date.year, latest_entry.date.month, latest_entry.date.day) == start_date:
        latest_entry.kwhUsed += kwh
    else:
        # If no entry for today, make one
        entry = DailyUsage(date=start_date, kwhUsed=kwh)
        db.session.add(entry)
    db.session.commit()
    pins[change_pin]['on_time'] = None
    pins[change_pin]['on_date'] = None


def generate_graph_data():
    labels = []
    values = []
    max = 0

    # Create data for chart
    # count = 0
    records = DailyUsage.query.order_by(desc(DailyUsage.date)).limit(7).all()
    (records)
    for record in records:
        labels.append(date(record.date.year, record.date.month, record.date.day))
        values.append(record.kwhUsed)
        if record.kwhUsed > max:
            max = record.kwhUsed
        # count += 1
        # if count >= 5:
        #     break

    labels.reverse()
    values.reverse()
    return labels, values, max


db.create_all()

daily_total = get_todays_usage()
todays_cost = get_todays_cost()

# Create dictionary to store pin info
pins = {
    25: {'name': 'Light', 'state': GPIO.LOW, 'on_time': None, 'on_date': None, 'wattage': 15},
    8: {'name': None, 'state': GPIO.LOW, 'on_time': None, 'on_date': None, 'wattage': 0},
    7: {'name': None, 'state': GPIO.LOW, 'on_time': None, 'on_date': None, 'wattage': 0},
    12: {'name': None, 'state': GPIO.LOW, 'on_time': None, 'on_date': None, 'wattage': 0}
}

# Setup each pin
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

labels, values, max = generate_graph_data()


@app.route("/")
def main():
    # For each pin, read the pin state and store it in the pins dictionary:
    for pin in pins:
        pins[pin]['state'] = GPIO.input(pin)

    template_data = {
        'pins': pins,
        'daily_total': daily_total,
        'todays_cost': todays_cost,
        'cost_per_kWh': os.environ['cost_per_kWh'],
        'display_new_device_form': False,
        'display_change_kWh': False,
        'labels': labels,
        'values': values,
        'max': max
    }

    return render_template('main.html', **template_data)


@app.route("/toggle/<change_pin>")
def toggle_pin(change_pin):
    change_pin = int(change_pin)

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

    labels, values, max = generate_graph_data()
    template_data = {
        'pins': pins,
        'daily_total': get_todays_usage(),
        'todays_cost': get_todays_cost(),
        'cost_per_kWh': os.environ['cost_per_kWh'],
        'labels': labels,
        'values': values,
        'max': max
    }

    return render_template('main.html', **template_data)


@app.route('/handle_change_kWh', methods=['POST'])
def handle_change_kWh():
    new_price = request.form['kWhprice']
    os.environ['cost_per_kWh'] = str(new_price)
    template_data = {
        'pins': pins,
        'daily_total': daily_total,
        'todays_cost': todays_cost,
        'cost_per_kWh': os.environ['cost_per_kWh'],
        'labels': labels,
        'values': values,
        'max': max
    }
    return render_template('main.html', **template_data)


@app.route("/devices/add_device")
def add_new_device():
    template_data = {
        'pins': pins,
        'daily_total': daily_total,
        'todays_cost': todays_cost,
        'cost_per_kWh': os.environ['cost_per_kWh'],
        'display_new_device_form': True,
        'labels': labels,
        'values': values,
        'max': max
    }
    return render_template('main.html', **template_data)


@app.route('/handle_new_device', methods=['POST'])
def handle_new_device():
    new_name = request.form['new_device_name']
    new_wattage = float(request.form['new_device_wattage'])
    for key in pins:
        if pins[key]['name'] is None:
            pins[key]['name'] = new_name
            pins[key]['wattage'] = new_wattage
            break

    template_data = {
        'pins': pins,
        'daily_total': daily_total,
        'todays_cost': todays_cost,
        'cost_per_kWh': os.environ['cost_per_kWh'],
        'labels': labels,
        'values': values,
        'max': max
    }
    return render_template('main.html', **template_data)


@app.route('/remove/<delete_pin>')
def delete_pin(delete_pin):
    delete_pin = int(delete_pin)
    for key in pins:
        if key == delete_pin:
            pins[delete_pin]['name'] = None
            pins[delete_pin]['wattage'] = None
            break

    template_data = {
        'pins': pins,
        'daily_total': daily_total,
        'todays_cost': todays_cost,
        'cost_per_kWh': os.environ['cost_per_kWh'],
        'labels': labels,
        'values': values,
        'max': max
    }
    return render_template('main.html', **template_data)


@app.route("/update_info/kWh")
def change_kWh():
    template_data = {
        'pins': pins,
        'daily_total': daily_total,
        'todays_cost': todays_cost,
        'cost_per_kWh': os.environ['cost_per_kWh'],
        'display_change_kWh': True,
        'labels': labels,
        'values': values,
        'max': max
    }
    return render_template('main.html', **template_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090)

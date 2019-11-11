from flask import Flask, render_template
import datetime

app = Flask(__name__)


@app.route("/")
def hello():
   now = datetime.datetime.now()
   time_string = now.strftime("%Y-%m-%d %H:%M")
   template_data = {
      'title' : 'HELLO!',
      'time': time_string
      }
   return render_template('main.html', **template_data)

@app.route('/button')
def button():
    print("Button press")

    now = datetime.datetime.now()
    time_string = now.strftime("%Y-%m-%d %H:%M")
    template_data = {
        'title': 'HELLO!',
        'time': time_string
    }
    return render_template('main.html', **template_data)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090)

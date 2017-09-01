from flask import Flask, render_template
from get_live_data import get_live_prices

app = Flask(__name__)


@app.route('/')
def hello_world():
    investment_data = get_live_prices()

    return render_template('home_dash.html', shares=investment_data)


if __name__ == '__main__':
    app.run()

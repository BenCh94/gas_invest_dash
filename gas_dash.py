from flask import Flask, render_template
from get_live_data import get_live_prices
from stock_data import get_stock_data

app = Flask(__name__)


@app.route('/')
def hello_world():
    investment_data = get_live_prices()
    share_data = investment_data['stocks']
    crypto_data = investment_data['crypto']

    return render_template('home_dash.html', shares=share_data, cryptos=crypto_data)

@app.route('/shares/<share_name>')
def share_page(share_name):
    data = get_stock_data(share_name)

    return data


if __name__ == '__main__':
    app.run()

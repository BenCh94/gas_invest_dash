from flask import Flask, render_template
from flask_mongoengine import MongoEngine
from get_live_data import get_live_prices
from stock_data import get_stock_data
from flask_mongoengine.wtf import model_form
import db_models
import os


app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': os.environ.get('mongo_db'),
    'host': os.environ.get('mongo_host'),
    'port': int(os.environ.get('mongo_port')),
    'username': os.environ.get('mongo_username'),
    'password': os.environ.get('mongo_password')
}
db = MongoEngine(app)


@app.route('/')
def hello_dash():
    shares = db_models.Share.objects()
    print shares

    return render_template('home_dash.html', shares=shares)


@app.route('/add_share')
def add_share():
    ShareForm = model_form(db_models.Share)
    form = ShareForm()
    return render_template('add_share.html', form=form)


@app.route('/shares/<share_name>')
def share_page(share_name):
    data = get_stock_data(share_name)

    return data


if __name__ == '__main__':
    app.run()

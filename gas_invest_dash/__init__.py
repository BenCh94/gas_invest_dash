from flask import Flask
from flask_mongoengine import MongoEngine
# from get_live_data import get_live_price
from flask_wtf.csrf import CSRFProtect
import os


application = app = Flask(__name__)


app.config['MONGODB_SETTINGS'] = {
    'db': os.environ.get('mongo_db'),
    'host': os.environ.get('mongo_host'),
    'port': int(os.environ.get('mongo_port')),
    'username': os.environ.get('mongo_username'),
    'password': os.environ.get('mongo_password')
}

db = MongoEngine(app)
csrf = CSRFProtect(app)
app.secret_key = os.environ.get('secret_key')


import gas_invest_dash.views


if __name__ == '__main__':
    app.run()

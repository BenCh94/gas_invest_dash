from flask import Flask, render_template, request, redirect
from flask_mongoengine import MongoEngine
from get_live_data import get_live_prices
from flask_mongoengine.wtf import model_form
from flask_wtf.csrf import CSRFProtect
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
csrf = CSRFProtect(app)
app.secret_key = os.environ.get('secret_key')


@app.route('/')
def hello_dash():
    shares = db_models.Share.objects()

    return render_template('home_dash.html', shares=shares)


@app.route('/add_investment')
def add_share():
    ShareForm = model_form(db_models.Share)
    form = ShareForm()
    if request.method == 'POST' and form.validate():
        share = db_models.Share()
        share_to_add = form.populate_obj(share)
        if share_to_add.save():
            redirect('add_success.html')
    return render_template('add_share.html', form=form)


@app.route('/shares/<share_name>')
def share_page(share_name):
    name = str(share_name)
    data = db_models.Share.objects.get_or_404(name=name)

    return str(data)


@app.route('/cryptos')
def get_crypto_prices():

    return str(get_live_prices())


if __name__ == '__main__':
    app.run()

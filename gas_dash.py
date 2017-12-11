from flask import Flask, render_template, request, flash, redirect, url_for
from flask_mongoengine import MongoEngine
# from get_live_data import get_live_prices
from share_data_compiling import compile_data, historic_totals, iex_historic_totals
from flask_mongoengine.wtf import model_form
from flask_wtf.csrf import CSRFProtect
import datetime
import pandas as pd
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
def home_dash():
    shares = db_models.Share.objects()
    benchmark = db_models.Benchmark.objects(name='SandP 500').get()
    historic_data = iex_historic_totals(shares, benchmark)
    portfolio_df = historic_data['df']
    data = portfolio_df.to_json(orient='records')
    return render_template('home_dash.html', data=data, metrics=historic_data['metric'])


@app.route('/shares')
def share_dash():
    shares = db_models.Share.objects()
    # Get share objects from the DB and compile data to desired format
    data_to_view = compile_data(shares)
    return render_template('share_dash.html',
                           shares=data_to_view['col_shares'],
                           total_gain=data_to_view['total_p_l'],
                           total_percent=data_to_view['total_prcnt'])


@app.route('/add_investment/share', methods=['POST'])
def add_share():
    # Initiate form object from model
    ShareForm = model_form(db_models.Share)
    share_form = ShareForm()
    # If form validates collect data
    if share_form.validate_on_submit():
        share_to_add = db_models.Share(
            str(request.form['name']),
            float(request.form['quantity']),
            str(request.form['ticker']),
            float(request.form['amount_usd']),
            float(request.form['fees_usd']),
            str(request.form['provider']),
            str(request.form['start_date'])
        )
        print share_to_add
        # Add form data as share object to DB
        try:
            share_to_add.save()
            flash('The Investment has been added to the database!')
            return redirect(url_for('hello_dash'))
        except StandardError as e:
            flash('Uh Oh something went wrong!!' + str(e))
            return redirect(url_for('hello_dash'))


@app.route('/add_investment/crypto', methods=['POST'])
def add_crypto():
    # Collect form data and add to DB
    crypto_to_add = db_models.Crypto(
        str(request.form['name']),
        str(request.form['ticker']),
        float(request.form['amount_usd']),
        float(request.form['quantity']),
        float(request.form['fees_usd']),
        str(request.form['provider']),
    )
    try:
        result = crypto_to_add.save()
        print result
        flash('The Investment has been added to the database!')
        return redirect(url_for('hello_dash'))
    except StandardError as e:
        print str(e)
        flash('Uh Oh something went wrong!!' + str(e))
        return redirect(url_for('hello_dash'))


@app.route('/add_investment', methods=['GET', 'POST'])
def add_investment():
    ShareForm = model_form(db_models.Share)
    share_form = ShareForm()
    CryptoForm = model_form(db_models.Crypto)
    crypto_form = CryptoForm()
    return render_template('add_share.html', share_form=share_form, crypto_form=crypto_form)


@app.route('/shares/<share_name>')
def share_page(share_name):
    name = str(share_name)
    data = db_models.Share.objects.get_or_404(name=name)
    share_daily_df = pd.DataFrame(data.historical.daily_data)
    share_daily_df = share_daily_df.T
    share_daily_df['date'] = share_daily_df.index
    data = share_daily_df.to_json(orient='records')

    return render_template('share_page.html', data=data)


@app.route('/cryptos')
def get_crypto_prices():
    crypto_data = get_live_prices()

    return render_template('cryptos.html', data=crypto_data)


@app.route('/monthly_report/<report_start>/<report_end>')
def get_monthly(report_start, report_end):
    shares = db_models.Share.objects()
    benchmark = db_models.Benchmark.objects(name='SandP 500').get()
    historic_data = historic_totals(shares, benchmark)
    portfolio_df = historic_data['df']
    # Generating a monthly review example
    report_selection = (portfolio_df.index >= report_start) & (portfolio_df.index < report_end)
    report_df = portfolio_df.loc[report_selection]
    report_html = report_df.to_html()
    return report_html


if __name__ == '__main__':
    app.run()

from flask import Flask, render_template, request, flash, redirect, url_for
from flask_mongoengine import MongoEngine
# from get_live_data import get_live_prices
from share_data_compiling import compile_data, iex_historic_totals, crossfilter_portfolio
from research_data import get_details, get_key_stats, get_financials
from flask_mongoengine.wtf import model_form
from flask_wtf.csrf import CSRFProtect
from text_inserts import cv_explanation
import stock_data
import datetime
import pandas as pd
import db_models
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


@app.route('/')
def home_dash():
    shares = db_models.Share.objects()
    benchmark = db_models.Benchmark.objects(name='SandP 500').get()
    historic_data = iex_historic_totals(shares, benchmark)
    portfolio_df = historic_data['df']
    data = portfolio_df.to_json(orient='records')
    return render_template('home_dash.html', data=data, metrics=historic_data['metric'])


@app.route('/dash_v2')
def filter_dash():
    shares = db_models.Share.objects()
    benchmark = db_models.Benchmark.objects(name='SandP 500').get()
    historic_data = crossfilter_portfolio(shares, benchmark)
    totals = historic_data.loc[historic_data.index.max()]
    metrics = dict()
    metrics['portfolio_gain'] = totals['gain_loss'].sum()
    metrics['sp_gain'] = totals['sp_gain_loss'].sum()
    metrics['invested'] = totals['invested'].sum()
    metrics['pct_gain'] = (metrics['portfolio_gain']/metrics['invested'])*100
    metrics['sp_pct_gain'] = (metrics['sp_gain']/metrics['invested'])*100
    metrics['mean_gain'] = historic_data['gain_loss'].mean()
    metrics['sp_mean_gain'] = historic_data['sp_gain_loss'].mean()
    metrics['std_dev'] = historic_data['gain_loss'].std()
    metrics['sp_std_dev'] = historic_data['sp_gain_loss'].std()
    metrics['cof_var'] = (metrics['std_dev']/metrics['mean_gain'])*100
    metrics['sp_cof_var'] = (metrics['sp_std_dev']/metrics['sp_mean_gain'])*100
    metrics['value'] = totals['invested'].sum()+totals['gain_loss'].sum()
    daysin = len(historic_data['date'].unique())
    data = historic_data.to_json(orient='records')
    text = dict()
    text['cv_explanation'] = cv_explanation
    return render_template('dash_v2.html', data=data, days=daysin, metrics=metrics, text=text)


@app.route('/dash_v2/update')
def update_dash():
    stock_data.get_iex_sandp()
    for share in db_models.Share.objects:
        if share.status == 'Inactive':
            continue
        print share.name
        stock_data.iex_stock_chart(share.name)
    shares = db_models.Share.objects()
    benchmark = db_models.Benchmark.objects(name='SandP 500').get()
    historic_data = crossfilter_portfolio(shares, benchmark)
    totals = historic_data.loc[historic_data.index.max()]
    metrics = dict()
    metrics['portfolio_gain'] = totals['gain_loss'].sum()
    metrics['sp_gain'] = totals['sp_gain_loss'].sum()
    metrics['invested'] = totals['invested'].sum()
    metrics['pct_gain'] = (metrics['portfolio_gain'] / metrics['invested']) * 100
    metrics['sp_pct_gain'] = (metrics['sp_gain'] / metrics['invested']) * 100
    metrics['mean_gain'] = historic_data['gain_loss'].mean()
    metrics['sp_mean_gain'] = historic_data['sp_gain_loss'].mean()
    metrics['std_dev'] = historic_data['gain_loss'].std()
    metrics['sp_std_dev'] = historic_data['sp_gain_loss'].std()
    metrics['cof_var'] = (metrics['std_dev'] / metrics['mean_gain']) * 100
    metrics['sp_cof_var'] = (metrics['sp_std_dev'] / metrics['sp_mean_gain']) * 100
    metrics['value'] = totals['invested'].sum() + totals['gain_loss'].sum()
    daysin = len(historic_data['date'].unique())
    data = historic_data.to_json(orient='records')
    text = dict()
    text['cv_explanation'] = cv_explanation
    return render_template('dash_v2.html', data=data, days=daysin, metrics=metrics, text=text)


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
    share_form = ShareForm(request.form)
    # If form validates collect data
    # if share_form.validate_on_submit():
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
        return redirect(url_for('home_dash'))
    except StandardError as e:
        print e
        return redirect(url_for('home_dash'))


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


@app.route('/sell', methods=['POST', 'GET'])
def sell():
    shares = db_models.Share.objects()
    SellShareForm = model_form(db_models.Share)
    share_form = SellShareForm()
    return render_template('sell_share.html', shares=shares, share_form=share_form)


@app.route('/sell_share', methods=['POST'])
def sell_share():
    end_date = str(request.form['end_date'])
    stock_name = str(request.form['name'])
    out_fees = float(request.form['out_fees'])
    # Update share object in DB
    try:
        # Find share object matching details
        share_object = db_models.Share.objects(name=stock_name).get()
        # Update object with sell details
        share_object.update(status='Inactive', end_date=end_date, out_fees=out_fees)
        flash('The sell has been recorded in the database!')
        return redirect(url_for('hello_dash'))
    except StandardError as e:
        flash('Uh Oh something went wrong!!' + str(e))
        return redirect(url_for('hello_dash'))


@app.route('/cryptos')
def get_crypto_prices():
    # crypto_data = get_live_prices()

    return render_template('cryptos.html')


@app.route('/monthly_report/<report_start>/<report_end>')
def get_monthly(report_start, report_end):
    shares = db_models.Share.objects()
    benchmark = db_models.Benchmark.objects(name='SandP 500').get()
    historic_data = iex_historic_totals(shares, benchmark)
    portfolio_df = historic_data['df']
    # Generating a monthly review example
    report_selection = (portfolio_df.index >= report_start) & (portfolio_df.index < report_end)
    report_df = portfolio_df.loc[report_selection]
    report_html = report_df.to_html()
    return report_html


@app.route('/research/<ticker>')
def get_info_by_ticker(ticker):
    financials = get_financials(ticker)
    stats = get_key_stats(ticker)
    details = get_details(ticker)
    return render_template('stock_research.html', financials=financials.to_html(), stats=stats, details=details)


if __name__ == '__main__':
    app.run()

from gas_invest_dash import app
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_httpauth import HTTPBasicAuth
import gas_invest_dash.db_models as db_models
from flask_mongoengine.wtf import model_form
from flask_wtf.csrf import CSRFProtect
from text_inserts import cv_explanation
import datetime
import pandas as pd
import os
import pprint
pp = pprint.PrettyPrinter(indent=4)

import gas_invest_dash.research_data
from gas_invest_dash.share_data_compiling import crossfilter_portfolio, iex_historic_totals, compile_data
from gas_invest_dash.stock_data import *

users = {
    "Bench94": os.environ.get('BasicPass')
}

auth = HTTPBasicAuth()


@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None


@app.route('/')
def filter_dash():
    shares = db_models.Share.objects()
    last_updated = str(shares.first().historical.last_update.isoformat())
    benchmark = db_models.Benchmark.objects(name='SandP 500').get()
    historic_data = crossfilter_portfolio(shares, benchmark)
    totals = historic_data.loc[historic_data.index.max()]
    metrics = create_metrics_dict(totals, historic_data, last_updated)
    data = historic_data.to_json(orient='records')
    text = dict()
    text['cv_explanation'] = cv_explanation
    return render_template('dash_v2.html', data=data, metrics=metrics, text=text)


@app.route('/update')
def update_dash():
    get_iex_sandp()
    for share in db_models.Share.objects:
        if share.status == 'Inactive':
            continue
        iex_stock_chart(share.name)
    shares = db_models.Share.objects()
    benchmark = db_models.Benchmark.objects(name='SandP 500').get()
    historic_data = crossfilter_portfolio(shares, benchmark)
    totals = historic_data.loc[historic_data.index.max()]
    last_updated = str(db_models.Share.objects.first().historical.last_update.isoformat())
    metrics = create_metrics_dict(totals, historic_data, last_updated)
    data = historic_data.to_json(orient='records')
    text = dict()
    text['cv_explanation'] = cv_explanation
    return render_template('dash_v2.html', data=data, metrics=metrics, text=text)


@app.route('/shares')
def share_dash():
    shares = db_models.Share.objects()
    # Get share objects from the DB and compile data to desired format
    data_to_view = compile_data(shares)
    return render_template('share_dash.html',
                           shares=data_to_view['col_shares'],
                           total_gain=data_to_view['total_p_l'],
                           total_percent=data_to_view['total_prcnt'])


@app.route('/shares/<share_name>')
def share_page(share_name):
    name = str(share_name)
    share_object = db_models.Share.objects.get_or_404(name=name)
    ticker = share_object.ticker
    # Pull share data from DB
    daily_data = get_share_dailys(name)
    # Pull financials from IEX api
    fin_stats = get_share_financial(ticker)
    return render_template('share_page.html', daily_data=daily_data, fin_data=fin_stats, ticker=ticker)


@app.route('/add_investment/share', methods=['POST'])
@auth.login_required
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
    print(share_to_add)
    # Add form data as share object to DB
    try:
        share_to_add.save()
        return redirect(url_for('home_dash'))
    except StandardError as e:
        print(e)
        return redirect(url_for('home_dash'))


@app.route('/add_investment/crypto', methods=['POST'])
@auth.login_required
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
        print(result)
        flash('The Investment has been added to the database!')
        return redirect(url_for('hello_dash'))
    except StandardError as e:
        print(str(e))
        flash('Uh Oh something went wrong!!' + str(e))
        return redirect(url_for('hello_dash'))


@app.route('/add_investment', methods=['GET', 'POST'])
@auth.login_required
def add_investment():
    ShareForm = model_form(db_models.Share)
    share_form = ShareForm()
    CryptoForm = model_form(db_models.Crypto)
    crypto_form = CryptoForm()
    return render_template('add_share.html', share_form=share_form, crypto_form=crypto_form)


@app.route('/add_to_share')
def add_to_share():
    # result = stock_data.add_to_share('Disney', '2018-04-05', 1.0051, 102, 2.99)
    return 'done'


@app.route('/sell', methods=['POST', 'GET'])
@auth.login_required
def sell():
    shares = db_models.Share.objects()
    SellShareForm = model_form(db_models.Share)
    share_form = SellShareForm()
    return render_template('sell_share.html', shares=shares, share_form=share_form)


@app.route('/sell_share', methods=['POST'])
@auth.login_required
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

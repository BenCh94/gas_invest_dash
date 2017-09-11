from investment_data import current_stocks
import requests
import datetime
import pandas as pd
import os

alpha_vantage_base = "https://www.alphavantage.co/query?"
api_key = os.environ.get('alpha_api_key')


def get_stock_data(stock_name):
    call_params = dict(apikey=api_key, symbol=current_stocks[stock_name]['ticker'], function="TIME_SERIES_WEEKLY")
    url = alpha_vantage_base
    r = requests.get(url, params=call_params)
    stock_dates = r.json()
    stock_dates = stock_dates['Weekly Time Series']
    start = current_stocks[stock_name]['start_date']
    start = datetime.datetime.strptime(start, "%d/%m/%Y")
    prices = dict()
    for key in stock_dates:
        py_date = datetime.datetime.strptime(key, "%Y-%m-%d")
        if py_date > start:
            prices[py_date.strftime("%d/%m/%Y")] = stock_dates[key]

    stock_df = pd.DataFrame(prices)
    return stock_df.to_html()

from investment_data import current_stocks
from db_models import Share
import requests
import datetime
import pandas as pd
import os


# File for getting historical daily data
alpha_vantage_base = "https://www.alphavantage.co/query?"  # data source API base URL
api_key = os.environ.get('alpha_api_key')  # API Key pulled from environment variables


def clean_for_db(df):
    df.columns = ['open', 'high', 'low', 'close', 'adj_close', 'volume', 'dividend_amount', 'split_cof']
    df = df.to_dict(orient='index')
    return df


def add_data_to_db(data_object, stock):
    update_data = dict(daily_data=data_object, last_update=datetime.date.today())
    print update_data
    print stock
    for share in Share.objects:
        print share.name
    update = Share.objects(name=stock).update(set__historical=update_data)
    print update


def get_stock_data(stock_name):
    share_object = Share.objects(name=stock_name).get()  # Find the share in the database
    call_params = dict(apikey=api_key,
                       symbol=share_object.ticker,
                       function="TIME_SERIES_DAILY_ADJUSTED")  # Creating parameters for API call
    url = alpha_vantage_base
    r = requests.get(url, params=call_params)
    stock_dates = r.json()
    stock_dates = stock_dates['Time Series (Daily)']
    start = share_object.start_date  # get the start date of investment
    start = datetime.datetime.strptime(start, "%d/%m/%Y")  # Convert date string to date object
    prices = dict()  # Creating empty dictionary for results
    for key in stock_dates:  # Iterate over daily data
        py_date = datetime.datetime.strptime(key, "%Y-%m-%d")  # Convert date string to date object
        if py_date > start:  # If the date is after the investment start, capture the data
            prices[py_date.strftime("%d/%m/%Y")] = stock_dates[key]

    stock_df = pd.DataFrame(prices)  # Creating a data frame for  share prices
    stock_df = stock_df.T  # Reversing data frame so dates are rows
    stock_df.index = pd.to_datetime(stock_df.index, format="%d/%m/%Y")  # Converting dates to Irish format
    stock_df.index = stock_df.index.astype(str)
    stock_data = clean_for_db(stock_df)
    add_data_to_db(stock_data, share_object.name)




from investment_data import current_stocks
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
    print df


def get_stock_data(stock_name):
    call_params = dict(apikey=api_key,
                       symbol=current_stocks[stock_name]['ticker'],
                       function="TIME_SERIES_DAILY_ADJUSTED")  # Creating parameters for API call
    url = alpha_vantage_base
    r = requests.get(url, params=call_params)
    stock_dates = r.json()
    print r.content
    stock_dates = stock_dates['Time Series (Daily)']
    start = current_stocks[stock_name]['start_date']  # get the start date of investment
    start = datetime.datetime.strptime(start, "%d/%m/%Y")  # Convert date string to date object
    prices = dict()  # Creating empty dictionary for results
    for key in stock_dates:  # Iterate over daily data
        py_date = datetime.datetime.strptime(key, "%Y-%m-%d")  # Convert date string to date object
        if py_date > start:  # If the date is after the investment start, capture the data
            prices[py_date.strftime("%d/%m/%Y")] = stock_dates[key]

    stock_df = pd.DataFrame(prices)  # Creating a data frame for  share prices
    stock_df = stock_df.T  # Reversing data frame so dates are rows
    stock_df.index = pd.to_datetime(stock_df.index, format="%d/%m/%Y")  # Converting dates to Irish format
    stock_df = stock_df.sort_index()  # Sorting df by
    clean_for_db(stock_df)
    return stock_df.to_html()


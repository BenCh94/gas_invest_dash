from db_models import Share, Benchmark
import pandas as pd
import requests
import datetime
import os


# File for getting historical daily data
alpha_vantage_base = "https://www.alphavantage.co/query?"
# IEX Base url
iex_base = "https://api.iextrading.com/1.0"
# data source API base URL
api_key = os.environ.get('alpha_api_key')
# API Key pulled from environment variables


def clean_for_db(df):
    df.columns = ['open', 'high', 'low', 'close', 'adj_close', 'volume', 'dividend_amount', 'split_cof']
    df = df.to_dict(orient='index')
    return df


def clean_iex_data(df):
    cleaned_df = df.to_dict(orient='index')
    return cleaned_df


def add_data_to_db(data_object, stock):
    update_data = dict(daily_data=data_object, last_update=datetime.date.today())
    # Creating a dictionary of historical price data and last updated
    update = Share.objects(name=stock).update(set__historical=update_data)
    print update


def get_stock_data(stock_name):
    share_object = Share.objects(name=stock_name).get()
    # Find the share in the database
    call_params = dict(apikey=api_key,
                       symbol=share_object.ticker,
                       function="TIME_SERIES_DAILY_ADJUSTED",
                       outputsize="full")
    # Creating parameters for API call
    url = alpha_vantage_base
    r = requests.get(url, params=call_params)
    stock_dates = r.json()
    stock_dates = stock_dates['Time Series (Daily)']
    print min(stock_dates)
    start = share_object.start_date
    # get the start date of investment
    prices = dict()
    # Creating empty dictionary for results
    for key in stock_dates:
        # Iterate over daily data
        py_date = datetime.datetime.strptime(key, "%Y-%m-%d")
        # Convert date string to date object
        if py_date >= start:
            # If the date is after the investment start, capture the data
            prices[py_date.strftime("%d/%m/%Y")] = stock_dates[key]

    stock_df = pd.DataFrame(prices)
    # Creating a data frame for  share prices
    stock_df = stock_df.T
    # Reversing data frame so dates are rows
    stock_df.index = pd.to_datetime(stock_df.index, format="%d/%m/%Y")
    # Converting dates to Irish format
    stock_df.index = stock_df.index.astype(str)
    stock_data = clean_for_db(stock_df)
    add_data_to_db(stock_data, share_object.name)


def getSandP():
    sandp = Benchmark.objects(name="SandP 500").get()
    call_params = dict(apikey=api_key,
                       symbol=sandp.ticker,
                       function="TIME_SERIES_DAILY_ADJUSTED",
                       outputsize="full")
    # Creating parameters for API call
    url = alpha_vantage_base
    r = requests.get(url, params=call_params)
    stock_dates = r.json()
    print stock_dates
    stock_dates = stock_dates['Time Series (Daily)']
    start = sandp.start_date
    # get the start date of investment
    prices = dict()
    # Creating empty dictionary for results
    for key in stock_dates:
        # Iterate over daily data
        py_date = datetime.datetime.strptime(key, "%Y-%m-%d")
        # Convert date string to date object
        if py_date >= start:
            # If the date is after the investment start, capture the data
            prices[py_date.strftime("%d/%m/%Y")] = stock_dates[key]

    stock_df = pd.DataFrame(prices)
    # Creating a data frame for  share prices
    stock_df = stock_df.T
    # Reversing data frame so dates are rows
    stock_df.index = pd.to_datetime(stock_df.index, format="%d/%m/%Y")
    # Converting dates to Irish format
    stock_df.index = stock_df.index.astype(str)
    stock_data = clean_for_db(stock_df)
    update_data = dict(daily_data=stock_data, last_update=datetime.date.today())
    # Creating a dictionary of historical price data and last updated
    update = Benchmark.objects(name="SandP 500").update(set__historical=update_data)
    print update


def get_iex_sandp():
    sandp = Benchmark.objects(name="SandP 500").get()
    url = iex_base + "/stock/" + sandp.ticker + "/chart/1y"
    # Creating parameters for API call
    r = requests.get(url)
    stock_dates = r.json()
    # Convert to a dataframe
    prices_df = pd.DataFrame(stock_dates)
    # Convert date column
    prices_df['date'] = pd.to_datetime(prices_df['date'])
    print prices_df['date'].max()
    # filter results after start date
    invested_df = prices_df[prices_df['date'] >= sandp.start_date]
    invested_df.index = invested_df['date']
    invested_df.index = invested_df.index.astype(str)
    stock_data = clean_iex_data(invested_df)
    update_data = dict(daily_data=stock_data, last_update=datetime.date.today())
    # Creating a dictionary of historical price data and last updated
    update = Benchmark.objects(name="SandP 500").update(set__historical=update_data)
    print update


def iex_stock_chart(stock_name):
    share_object = Share.objects(name=stock_name).get()
    # Find the share in the database
    ticker = share_object.ticker
    # Querying IEX
    url = iex_base+"/stock/"+ticker+"/chart/1m"
    r = requests.get(url)
    # Get data from IEX
    prices_chart = r.json()
    # Convert to a dataframe
    prices_df = pd.DataFrame(prices_chart)
    # Convert date column
    prices_df['date'] = pd.to_datetime(prices_df['date'])
    print prices_df['date'].max()
    current_price_data = share_object.historical.daily_data
    price_dict = dict(current_price_data)
    dates = set(price_dict.keys())
    # filter results after start date
    invested_df = prices_df[prices_df['date'] >= share_object.start_date]
    invested_df.index = invested_df['date']
    invested_df.index = invested_df.index.astype(str)
    stock_data = clean_iex_data(invested_df)
    update_dates = set(stock_data.keys())
    new_dates = list(update_dates - dates)
    print new_dates
    for item in new_dates:
        price_dict[str(item)] = stock_data[str(item)]
    add_data_to_db(price_dict, stock_name)


getSandP()


for share in Share.objects:
    print share.name
    get_stock_data(share.name)


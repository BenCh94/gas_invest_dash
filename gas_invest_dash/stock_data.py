""" Functions for interacting with the IEX API and importing the data into the DB """
import datetime
import os
from gas_invest_dash.db_models import Share, Benchmark
import pandas as pd
import requests


# File for getting historical daily data
ALPHA_VANTAGE_BASE = "https://www.alphavantage.co/query?"
# IEX Base url
IEX_BASE = "https://api.iextrading.com/1.0"
# data source API base URL
API_KEY = os.environ.get('alpha_API_KEY')
# API Key pulled from environment variables

def clean_iex_data(iex_data):
    """Function cleans data from IEX api for DB"""
    cleaned_df = iex_data.to_dict(orient='index')
    return cleaned_df

def add_data_to_db(data_object, stock):
    """ Adds data to the database"""
    update_data = dict(daily_data=data_object, last_update=datetime.datetime.now())
    # Creating a dictionary of historical price data and last updated
    update = Share.objects(name=stock).update(set__historical=update_data)
    print update

def get_iex_sandp():
    """Function gets data for the S and P 500 benchmark"""
    sandp = Benchmark.objects(name="SandP 500").get()
    url = IEX_BASE + "/stock/" + "voo" + "/chart/5y"
    # Creating parameters for API call
    api_req = requests.get(url)
    stock_dates = api_req.json()
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
    update_data = dict(daily_data=stock_data, last_update=datetime.datetime.now())
    # Creating a dictionary of historical price data and last updated
    update = Benchmark.objects(name="SandP 500").update(set__historical=update_data)
    print update

def iex_stock_chart(stock_name):
    """Function gets share chart from IEX api"""
    share_object = Share.objects(name=stock_name).get()
    # Find the share in the database
    ticker = share_object.ticker
    # Querying IEX
    url = IEX_BASE+"/stock/"+ticker+"/chart/1m"
    api_req = requests.get(url)
    # Get data from IEX
    prices_chart = api_req.json()
    # Convert to a dataframe
    prices_df = pd.DataFrame(prices_chart)
    # Convert date column
    prices_df['date'] = pd.to_datetime(prices_df['date'])
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
        stock_data[str(item)]['quantity'] = share_object['quantity']
        stock_data[str(item)]['fees_usd'] = share_object['fees_usd']
        stock_data[str(item)]['amount_usd'] = share_object['amount_usd']
        stock_data[str(item)]['invested'] = share_object['amount_usd'] + share_object['fees_usd']
        stock_data[str(item)]['name'] = share_object['name']
        price_dict[str(item)] = stock_data[str(item)]
    add_data_to_db(price_dict, stock_name)


def insert_amount_daily(share_name):
    """Function inserts buy information into share historical data"""
    share_object = Share.objects(name=share_name).get()
    historical = share_object.historical
    days = historical['daily_data']
    quantity = share_object['quantity']
    fees = share_object['fees_usd']
    amount = share_object['amount_usd']
    new_hist = {}
    for day in days.iterkeys():
        new_hist[day] = days[day]
        new_hist[day]['quantity'] = quantity
        new_hist[day]['fees_usd'] = fees
        new_hist[day]['amount_usd'] = amount
        new_hist[day]['invested'] = new_hist[day]['amount_usd'] + new_hist[day]['fees_usd']
        new_hist[day]['name'] = share_name
    update_data = dict(daily_data=new_hist, last_update=datetime.datetime.now())
    update = Share.objects(name=share_name).update(set__historical=update_data)
    print update

def get_share_financial(ticker):
    """Function gets financials from the IEX api"""
    key_stats = "/stock/" + ticker + "/stats"
    financials = "/stock/" + ticker + "/financials"
    ticker_stats = requests.get(IEX_BASE+key_stats)
    fin_stats = requests.get(IEX_BASE+financials)
    fin_dict = fin_stats.json()
    fin_dict['financials'] = list(reversed(fin_dict['financials']))
    fin_dict['stats'] = ticker_stats.json()
    return fin_dict

def get_share_dailys(name):
    """Function returns share daily data from DB"""
    name = str(name)
    data = Share.objects.get_or_404(name=name)
    share_daily_df = pd.DataFrame(data.historical.daily_data)
    share_daily_df = share_daily_df.T
    share_daily_df['date'] = share_daily_df.index
    daily_data = share_daily_df.to_json(orient='records')
    return daily_data

def create_metrics_dict(totals, historic_data, update):
    """Creates metrics from stock data"""
    metrics = dict()
    metrics['portfolio_gain'] = round(totals['gain_loss'].sum(), 2)
    metrics['sp_gain'] = round(totals['sp_gain_loss'].sum(), 2)
    metrics['invested'] = round(totals['invested'].sum(), 2)
    metrics['pct_gain'] = round((metrics['portfolio_gain']/metrics['invested'])*100, 2)
    metrics['sp_pct_gain'] = round((metrics['sp_gain']/metrics['invested'])*100, 2)
    metrics['mean_gain'] = round(historic_data['gain_loss'].mean(), 2)
    metrics['sp_mean_gain'] = round(historic_data['sp_gain_loss'].mean(), 2)
    metrics['std_dev'] = round(historic_data['gain_loss'].std(), 2)
    metrics['sp_std_dev'] = round(historic_data['sp_gain_loss'].std(), 2)
    metrics['cof_var'] = round((metrics['std_dev']/metrics['mean_gain'])*100, 2)
    metrics['sp_cof_var'] = round((metrics['sp_std_dev']/metrics['sp_mean_gain'])*100, 2)
    metrics['value'] = round(totals['invested'].sum()+totals['gain_loss'].sum(), 2)
    metrics['days_in'] = len(historic_data['date'].unique())
    update_datetime = datetime.datetime.strptime(update, "%Y-%m-%dT%H:%M:%S.%f")
    metrics['last_update'] = datetime.datetime.strftime(update_datetime, "%d/%m/%Y, %H:%M")
    print metrics['last_update']
    return metrics

# Function is broken needs to be rewritten
# def add_to_share(share_name, date, qty, amount, fees):
#     # Do not use this function until it has been tested
#     format_date = datetime.datetime.strptime(date, "%d/%m/%Y")
#     share_object = Share.objects(name=share_name).get()
#     historical = share_object.historical
#     days = historical['daily_data']
#     for day in days.keys():
#         if datetime.datetime.strptime(day, "%Y-%m-%d") >= format_date:
#             days[day]['quantity'] = share_object['quantity'] + qty
#             days[day]['amount_usd'] = share_object['amount_usd'] + amount
#             days[day]['fees_usd'] = share_object['fees_usd'] + fees
#             days[day]['invested'] = days[day]['invested'] + fees + amount
#             print(days[day])
#             # days[day]['quantity'] = qty
#             # days[day]['amount_usd'] = amount
#             # days[day]['fees_usd'] = fees
#             # days[day]['invested'] = amount + fees
#             # print(days[day])
#     update_data = dict(daily_data=days, last_update=datetime.date.today())
#     update = Share.objects(name=share_name).update(set__historical=update_data)
#     new_qty = share_object['quantity'] + qty
#     new_amnt = share_object['amount_usd'] + amount
#     new_fees = share_object['fees_usd'] + fees
#     update_qty = Share.objects(name=share_name).update(set__quantity=new_qty)
#     update_amnt = Share.objects(name=share_name).update(set__amount_usd=new_amnt)
#     update_fees = Share.objects(name=share_name).update(set__fees_usd=new_fees)
#     print(update)
#     print(update_qty, update_amnt, update_fees)
#     return update


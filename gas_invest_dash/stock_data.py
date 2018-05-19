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

# Function formats data for the DB
def clean_for_db(df):
    df.columns = ['open', 'high', 'low', 'close', 'adj_close', 'volume', 'dividend_amount', 'split_cof']
    df = df.to_dict(orient='index')
    return df

# Function cleans data from IEX api for DB
def clean_iex_data(df):
    cleaned_df = df.to_dict(orient='index')
    return cleaned_df

# Adds data to the database
def add_data_to_db(data_object, stock):
    update_data = dict(daily_data=data_object, last_update=datetime.date.today())
    # Creating a dictionary of historical price data and last updated
    update = Share.objects(name=stock).update(set__historical=update_data)
    print(update)

# Function gets data for the S and P 500 benchmark
def get_iex_sandp():
    sandp = Benchmark.objects(name="SandP 500").get()
    url = iex_base + "/stock/" + "voo" + "/chart/5y"
    # Creating parameters for API call
    r = requests.get(url)
    stock_dates = r.json()
    # Convert to a dataframe
    prices_df = pd.DataFrame(stock_dates)
    # Convert date column
    prices_df['date'] = pd.to_datetime(prices_df['date'])
    print(prices_df['date'].max())
    # filter results after start date
    invested_df = prices_df[prices_df['date'] >= sandp.start_date]
    invested_df.index = invested_df['date']
    invested_df.index = invested_df.index.astype(str)
    stock_data = clean_iex_data(invested_df)
    update_data = dict(daily_data=stock_data, last_update=datetime.date.today())
    # Creating a dictionary of historical price data and last updated
    update = Benchmark.objects(name="SandP 500").update(set__historical=update_data)
    print(update)

# Function gets share chart from IEX api
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
    print(new_dates)
    for item in new_dates:
        stock_data[str(item)]['quantity'] = share_object['quantity']
        stock_data[str(item)]['fees_usd'] = share_object['fees_usd']
        stock_data[str(item)]['amount_usd'] = share_object['amount_usd']
        stock_data[str(item)]['invested'] = share_object['amount_usd'] + share_object['fees_usd']
        stock_data[str(item)]['name'] = share_object['name']
        price_dict[str(item)] = stock_data[str(item)]
    add_data_to_db(price_dict, stock_name)


# Function inserts buy information into share historical data
def insert_amount_daily(share_name):
    share_object = Share.objects(name=share_name).get()
    historical = share_object.historical
    days = historical['daily_data']
    quantity = share_object['quantity']
    fees = share_object['fees_usd']
    amount = share_object['amount_usd']
    new_historical = {}
    for day in days.iterkeys():
        new_historical[day] = days[day]
        new_historical[day]['quantity'] = quantity
        new_historical[day]['fees_usd'] = fees
        new_historical[day]['amount_usd'] = amount
        new_historical[day]['invested'] = new_historical[day]['amount_usd'] + new_historical[day]['fees_usd']
        new_historical[day]['name'] = share_name
    update_data = dict(daily_data=new_historical, last_update=datetime.date.today())
    update = Share.objects(name=share_name).update(set__historical=update_data)
    print(update)

# Function gets financials from the IEX api 
def get_share_financial(ticker):
    key_stats = "/stock/" + ticker + "/stats"
    financials = "/stock/" + ticker + "/financials"
    ticker_stats = requests.get(iex_base+key_stats)
    fin_stats = requests.get(iex_base+financials)
    fin_dict = fin_stats.json()
    fin_dict['financials'] = list(reversed(fin_dict['financials']))
    fin_dict['stats'] = ticker_stats.json()
    return fin_dict

# Function returns share daily data from DB
def get_share_dailys(name):
    name = str(name)
    data = Share.objects.get_or_404(name=name)
    share_daily_df = pd.DataFrame(data.historical.daily_data)
    share_daily_df = share_daily_df.T
    share_daily_df['date'] = share_daily_df.index
    daily_data = share_daily_df.to_json(orient='records')
    return daily_data


# Creates metrics from stock data
def create_metrics_dict(totals, historic_data):
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
    metrics['days_in'] = len(historic_data['date'].unique())
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


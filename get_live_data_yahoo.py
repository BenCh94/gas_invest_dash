from google_finance.client import GoogleFinanceClient
from investment_data import current_stocks


def get_live_prices():
    stock_names = []
    for investments in current_stocks:
        stock_names.append(investments['ticker'])
    live_prices = []
    share_data = GoogleFinanceClient.get_stock(tickers=stock_names)
    print share_data

    for stock in current_stocks:
        stock_live = {}
        ticker = stock['ticker']
        name = stock['name']
        live_price = share_data[ticker]['l_cur']
        stock_live['name'] = name
        stock_live['ticker'] = ticker
        stock_live['live_price'] = live_price
        live_prices.append(stock_live)

    return live_prices

from google_finance.client import GoogleFinanceClient
from coinmarketcap import Market
from investment_data import current_stocks, crypto_currencies


def get_live_prices():
    stock_names = []
    currency_names = []
    for investments in current_stocks:
        stock_names.append(investments['ticker'])
    for currency in crypto_currencies:
        cur_tick = currency['ticker']
        currency_names.append(cur_tick)
    live_prices = []
    share_data = GoogleFinanceClient.get_stock(tickers=stock_names)
    crypto_currency_data = Market()
    ether_price = crypto_currency_data.ticker(currency="Ethereum", convert="EUR")

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

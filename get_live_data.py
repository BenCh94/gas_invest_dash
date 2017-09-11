from coinmarketcap import Market


def get_live_prices():
    invest_data = {}
    crypto_currency_data = Market()
    ether_price = crypto_currency_data.ticker(currency="Ethereum", convert="EUR")

    invest_data['crypto'] = ether_price

    return invest_data

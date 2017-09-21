from coinmarketcap import Market


def get_live_prices():
    invest_data = {}
    crypto_currency_data = Market()
    ether_price = crypto_currency_data.ticker(currency="Ethereum", convert="USD")
    ripple_price = crypto_currency_data.ticker(currency="Ripple", convert="USD")

    invest_data['ether'] = ether_price
    invest_data['ripple'] = ripple_price

    return invest_data


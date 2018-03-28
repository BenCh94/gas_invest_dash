from coinmarketcap import Market
import db_models


def get_live_prices():
    invest_data = {}
    crypto_currency_data = Market()
    ether_price = crypto_currency_data.ticker(currency="Ethereum", convert="USD")
    ripple_price = crypto_currency_data.ticker(currency="Ripple", convert="USD")

    invest_data['ether'] = ether_price
    invest_data['ripple'] = ripple_price

    return invest_data


def get_cryptos_db():
    cryptos = db_models.Crypto.objects()
    return cryptos[0]['quantity']


crypto_quantity = get_cryptos_db()
crypto_live_data = get_live_prices()
eth_value = float(crypto_live_data['ether'][0]['price_usd'])*(0.45+0.29)
print eth_value
xrp_value = float(crypto_live_data['ripple'][0]['price_usd'])*154.04
print xrp_value
print eth_value+xrp_value - (243.76+7.08)


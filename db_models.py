from application import db


class HistoricalData(db.EmbeddedDocument):
    daily_data = db.DictField()
    last_update = db.DateTimeField()


class Share(db.Document):
    name = db.StringField(required=True)
    quantity = db.FloatField()
    ticker = db.StringField(required=True)
    amount_usd = db.FloatField()
    fees_usd = db.FloatField()
    out_fees = db.FloatField()
    provider = db.StringField()
    start_date = db.DateTimeField()
    status = db.StringField()
    end_date = db.DateTimeField()
    historical = db.EmbeddedDocumentField(HistoricalData)
    meta = {'collection': 'shares'}


class CryptoDaily(db.EmbeddedDocument):
    market_cap_usd = db.FloatField()
    price_usd = db.FloatField()
    volume_usd = db.FloatField()
    total_supply = db.FloatField()
    available_supply = db.FloatField()


class Crypto(db.Document):
    name = db.StringField(required=True)
    ticker = db.StringField(required=True)
    amount_usd = db.FloatField()
    quantity = db.FloatField()
    fees_usd = db.FloatField()
    provider = db.StringField()
    view = db.StringField()
    buys = db.DictField()
    daily_data = db.EmbeddedDocumentField(CryptoDaily)
    meta = {'collection': 'cryptos'}


class CryptoBuy(db.EmbeddedDocument):
    amount = db.FloatField()
    price_usd = db.FloatField()
    date = db.DateTimeField()
    fees_usd = db.FloatField()


class Benchmark(db.Document):
    name = db.StringField()
    ticker = db.StringField()
    start_date = db.DateTimeField()
    historical = db.EmbeddedDocumentField(HistoricalData)
    meta = {'collection': 'benchmarks'}


from gas_dash import db


class HistoricalData(db.EmbeddedDocument):
    daily_data = db.DictField()


class Share(db.Document):
    name = db.StringField()
    quantity = db.IntField()
    ticker = db.StringField()
    amount_usd = db.IntField()
    fees_usd = db.IntField()
    provider = db.StringField()
    start_date = db.DateTimeField()
    historical_data = db.EmbeddedDocumentField(HistoricalData)
    meta = {'collection': 'shares'}


class Crypto(db.Document):
    name = db.StringField()
    ticker = db.StringField()
    amount_usd = db.IntField()
    quantity = db.IntField()
    meta = {'collections': 'cryptos'}

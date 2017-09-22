from gas_dash import db


class HistoricalData(db.EmbeddedDocument):
    daily_data = db.DictField()
    last_update = db.DateTimeField()


class Share(db.Document):
    name = db.StringField()
    quantity = db.DecimalField()
    ticker = db.StringField()
    amount_usd = db.DecimalField()
    fees_usd = db.DecimalField()
    provider = db.StringField()
    start_date = db.DateTimeField()
    historical = db.EmbeddedDocumentField(HistoricalData)
    meta = {'collection': 'shares'}


class Crypto(db.Document):
    name = db.StringField()
    ticker = db.StringField()
    amount_usd = db.IntField()
    quantity = db.IntField()
    meta = {'collections': 'cryptos'}

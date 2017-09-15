from gas_dash import db


class HistoricalData(db.EmbeddedDocument):
    daily_data = db.DictField()


class Share(db.Document):
    name = db.StringField()
    quantity = db.IntField()
    average_price_usd = db.Intfield()
    ticker = db.StringField()
    amount_usd = db.IntField()
    fees_usd = db.IntField()
    provider = db.StringField()
    start_date = db.DateTimeField()
    historical_data = db.EmbeddedDocumentField(HistoricalData)
    meta = {'collection': 'shares'}


class Crypto(db.Document):
    name = db.StringField()
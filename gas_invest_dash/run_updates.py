"""Script used by heroku scheduler to update stocks in the DB"""
from gas_invest_dash.stock_data import get_iex_sandp, iex_stock_chart
from gas_invest_dash.db_models import Share


def update_stocks():
	"""Function to update shares from the IEX API"""
	print "INside the function"
	get_iex_sandp()
	for share in Share.objects:
		print share.name
		if share.status == 'Inactive':
			continue
		iex_stock_chart(share.name)
	return 'Complete'

update_stocks()

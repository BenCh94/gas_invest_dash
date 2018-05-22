from gas_invest_dash.stock_data import *


def update_stocks():
	"""Function to update shares from the IEX API"""
	get_iex_sandp()
	for share in db_models.Share.objects:
		if share.status == 'Inactive':
			continue
		iex_stock_chart(share.name)
	return 'Complete'
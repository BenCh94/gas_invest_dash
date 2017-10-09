import pandas as pd
import numpy as np
from datetime import datetime, date


# Function to find the latest closing price available
def get_latest_price(share):
    # Create df of price data
    price_data = pd.DataFrame(dict(share.historical.daily_data))
    # Reverse columns and rows
    price_data = price_data.T
    # return the max of datetime objects in index adjusted close column
    return price_data.loc[price_data.index.max()]['adj_close']


# Function to compile share data and calculate variables
def compile_data(shares_objects):
    # Create empty list for results
    col_shares = []
    total_p_l = 0
    total_invested = 0
    # Loop through share objects in DB
    for share in shares_objects:
        latest_price = float(get_latest_price(share))
        name = share.name
        fees = share.fees_usd
        amount = share.amount_usd
        invested = fees + amount
        total_invested += invested
        quantity = share.quantity
        # Convert date time to readable format
        last_update = share.historical.last_update.strftime("%d/%m/%Y")
        # Calculate p/l with fees
        current_gain_loss = (quantity*latest_price)-invested
        # add to totals
        total_p_l += current_gain_loss
        # Calculate p/l as %
        percentage_gain_loss = (current_gain_loss/invested)*100
        # create dictionary of share data
        share_data = dict(
            latest_price=latest_price,
            name=name,
            invested=invested,
            last_update=last_update,
            quantity=quantity,
            current_gain_loss=float("{0:.2f}".format(current_gain_loss)),
            percentage_gain_loss=float("{0:.2f}".format(percentage_gain_loss))
            )
        # add to results list
        col_shares.append(share_data)
    total_prcnt = (total_p_l/total_invested)*100
    data = dict(col_shares=col_shares, total_prcnt=total_prcnt, total_p_l=total_p_l)
    return data


def apply_sp(row, quantity_dict):
    z = 0
    sp_quantities = []
    for day in quantity_dict:
        sp_quantities.append(day['sp_quantity'])
    row_date = datetime.strptime(row['date'], '%Y-%m-%d')
    while z < len(quantity_dict):
        if z < len(quantity_dict)-1:
            next_date = datetime.strptime(quantity_dict[z + 1]['date'], '%Y-%m-%d')
        else:
            next_date = datetime.strptime('3000-01-01', '%Y-%m-%d')
        first_date = datetime.strptime(quantity_dict[z]['date'], '%Y-%m-%d')
        if next_date > row_date >= first_date and z == 0:
            return quantity_dict[z]['sp_quantity']
        elif next_date > row_date >= first_date:
            quantity = sum(sp_quantities[0:z+1])
            return quantity
        z += 1


def historic_totals(share_objects, benchmark):
    portfolio_df = pd.DataFrame([])
    portfolio_performance = {}
    for share in share_objects:
        # Create df of price data
        price_data = pd.DataFrame(dict(share.historical.daily_data))
        # Reverse columns and rows
        price_data = price_data.T
        # Convert to numeric for calculations
        price_data['adj_close'] = pd.to_numeric(price_data['adj_close'])
        # Pull variables from db objects
        fees = share.fees_usd
        amount = share.amount_usd
        quantity = share.quantity
        invested = fees + amount
        # Do calculations and add to DataFrame
        price_data['gain_loss'] = (price_data['adj_close']*quantity)-invested
        price_data['percent_gain'] = (price_data['gain_loss']/invested)*100
        price_data['invested'] = invested
        price_data['fees'] = fees
        price_data['amount'] = amount
        # Removing unused pricing data
        price_data = price_data[['gain_loss', 'percent_gain', 'invested', 'fees', 'amount']]
        # Add the individual share df to portfolio df
        portfolio_df = portfolio_df.append(price_data)
    # Sort th portfolio df by index i.e dates
    portfolio_df.sort_index(inplace=True)
    # Generate list of unique index values
    trading_days = list(portfolio_df.index.unique())
    # Loop through list of days
    for day in trading_days:
        # Create df for individual day
        day_df = portfolio_df.loc[day, ['gain_loss', 'percent_gain', 'invested', 'fees', 'amount']]
        # Create dictionary summing day values
        portfolio_performance[day] = dict(gain_loss=sum(day_df['gain_loss']),
                                          date=day,
                                          invested=sum(day_df['invested']),
                                          cuml_fees=sum(day_df['fees']),
                                          amount=sum(day_df['amount']))
    # Convert dictionary back to df and transpose
    total_performance = pd.DataFrame(portfolio_performance).T
    # Add total percentage calculation
    total_performance['percentage_gain'] = (total_performance['gain_loss'] / total_performance['invested']) * 100
    total_performance['portfolio_value'] = total_performance['gain_loss'] + total_performance['amount']
    # Adding benchmark data
    bench_data = pd.DataFrame(dict(benchmark.historical.daily_data)).T
    # Add bench close price to performance data
    total_performance['sp_close'] = bench_data['adj_close']
    # Find the dates when investment amount changed
    test = total_performance.drop_duplicates(subset='cuml_fees', keep='first')
    # Converting to numeric for calculation
    test.loc[:, 'amount'] = pd.to_numeric(test['amount'])
    test.loc[:, 'sp_close'] = pd.to_numeric(test['sp_close'])
    # Convert to dict for apply function
    sp_quant_dict = test.to_dict(orient='records')
    # Add zero starting point
    total_performance['sp_quantity'] = 0
    i = 0
    # Loop through dict and find amount of sp 500 could have purchased on day instead of investment
    while i < len(sp_quant_dict):
        if i == 0:
            sp_quant_dict[i]['period_amount'] = sp_quant_dict[i]['amount']
            sp_quant_dict[i]['sp_quantity'] = sp_quant_dict[i]['period_amount']/sp_quant_dict[i]['sp_close']
        else:
            sp_quant_dict[i]['period_amount'] = sp_quant_dict[i]['amount'] - sp_quant_dict[i-1]['amount']
            sp_quant_dict[i]['sp_quantity'] = sp_quant_dict[i]['period_amount'] / sp_quant_dict[i]['sp_close']
        i += 1
    # Apply the sp_quantity to all days in total performance
    total_performance['sp_quantity'] = total_performance.apply(lambda row: apply_sp(row, sp_quant_dict), axis=1)
    # Convert to numeric for calculations
    total_performance['sp_close'] = pd.to_numeric(total_performance['sp_close'])
    total_performance['sp_quantity'] = pd.to_numeric(total_performance['sp_quantity'])
    # Do benchmark calculations with s and p 500
    total_performance['sp_value'] = total_performance['sp_quantity'] * total_performance['sp_close']
    total_performance['sp_gain'] = total_performance['sp_value'] - total_performance['invested']
    total_performance['sp_percentage'] = (total_performance['sp_gain']/total_performance['invested'])*100
    # Printing Mean, Median and Standard Deviation for reference
    print np.mean(total_performance['percentage_gain'])
    print np.median(total_performance['percentage_gain'])
    print np.std(total_performance['percentage_gain'])
    print np.mean(total_performance['sp_percentage'])
    print np.median(total_performance['sp_percentage'])
    print np.std(total_performance['sp_percentage'])
    return total_performance

import pandas as pd
import numpy as np
from datetime import datetime, date


def iex_latest_price(share):
    # Create df of price data
    price_data = pd.DataFrame(dict(share.historical.daily_data))
    # Reverse columns and rows
    price_data = price_data.T
    # return the max of datetime objects in index adjusted close column
    return price_data.loc[price_data.index.max()]['close']


# Function to compile share data and calculate variables
def compile_data(shares_objects):
    # Create empty list for results
    col_shares = []
    total_p_l = 0
    total_invested = 0
    # Loop through share objects in DB
    for share in shares_objects:
        latest_price = float(iex_latest_price(share))
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


def iex_historic_totals(share_objects, benchmark):
    portfolio_df = pd.DataFrame([])
    portfolio_performance = {}
    for share in share_objects:
        # Create df of price data
        price_data = pd.DataFrame(dict(share.historical.daily_data))
        # Reverse columns and rows
        price_data = price_data.T
        # Convert to numeric for calculations
        price_data['close'] = pd.to_numeric(price_data['close'])
        # Pull variables from db objects
        fees = share.fees_usd
        amount = share.amount_usd
        quantity = share.quantity
        invested = fees + amount
        # Do calculations and add to DataFrame
        price_data['gain_loss'] = (price_data['close']*quantity)-invested
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
    total_performance['sp_close'] = bench_data['close']
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
    portfolio_gain = total_performance.iloc[-1]['gain_loss']
    portfolio_percentage = total_performance.iloc[-1]['percentage_gain']
    portfolio_mean = np.mean(total_performance['percentage_gain'])
    portfolio_median = np.median(total_performance['percentage_gain'])
    portfolio_std = np.std(total_performance['percentage_gain'])
    portfolio_best = max(total_performance['percentage_gain'])
    portfolio_worst = min(total_performance['percentage_gain'])
    sp_gain = total_performance.iloc[-1]['sp_gain']
    sp_percentage = total_performance.iloc[-1]['sp_percentage']
    sp_mean = np.mean(total_performance['sp_percentage'])
    sp_median = np.median(total_performance['sp_percentage'])
    sp_std = np.std(total_performance['sp_percentage'])
    sp_best = max(total_performance['sp_percentage'])
    sp_worst = min(total_performance['sp_percentage'])
    metrics_dict = dict(portfolio_gain="{0:.2f}".format(portfolio_gain),
                        portfolio_percentage="{0:.2f}".format(portfolio_percentage),
                        portfolio_mean="{0:.2f}".format(portfolio_mean),
                        portfolio_median="{0:.2f}".format(portfolio_median),
                        portfolio_best="{0:.2f}".format(portfolio_best),
                        portfolio_worst="{0:.2f}".format(portfolio_worst),
                        portfolio_std="{0:.2f}".format(portfolio_std),
                        portfolio_cv="{0:.2f}".format(abs(portfolio_std/abs(portfolio_mean))),
                        sp_gain="{0:.2f}".format(sp_gain),
                        sp_percentage="{0:.2f}".format(sp_percentage),
                        sp_mean="{0:.2f}".format(sp_mean),
                        sp_median="{0:.2f}".format(sp_median),
                        sp_std="{0:.2f}".format(sp_std),
                        sp_best="{0:.2f}".format(sp_best),
                        sp_worst="{0:.2f}".format(sp_worst),
                        sp_cv="{0:.2f}".format(abs(sp_std/abs(sp_mean))))
    print(total_performance.head())
    return dict(df=total_performance, metric=metrics_dict)


def crossfilter_portfolio(share_objects, benchmark):
    portfolio_df = pd.DataFrame([])
    for share in share_objects:
        # Create df of price data
        price_data = pd.DataFrame(dict(share.historical.daily_data))
        s_p_data = dict(benchmark.historical.daily_data)
        # Reverse columns and rows
        price_data = price_data.T
        for i, day in price_data.iterrows():
            price_data.loc[str(i), 'sp_close'] = s_p_data[str(i)]['close']
        # Convert to numeric for calculations
        price_data['close'] = pd.to_numeric(price_data['close'])
        price_data['gain_loss'] = (price_data['close']*price_data['quantity'])-price_data['invested']
        price_data['percent_gain'] = (price_data['gain_loss']/price_data['invested'])*100
        purchase_date = price_data.index.min()
        price_data['purchase_date'] = purchase_date
        # Get quantities (If more than one quantity multiple buys adding multiple sp benchmarks)
        qtys = price_data['amount_usd'].unique()
        if len(qtys) > 1:
            section_data = pd.DataFrame()
            # First quantity
            section = price_data.loc[price_data['amount_usd'] == qtys[0]]
            buy = section.index.min()
            section['sp_quantity'] = (section.loc[buy, 'amount_usd'] / section.loc[buy, 'sp_close'])
            section['sp_gain_loss'] = (section['sp_close'] * section['sp_quantity']) - section['invested']
            section['sp_percent_gain'] = (section['sp_gain_loss'] / section['invested']) * 100
            section_data = section_data.append(section)
            # Subsequent buys
            i = 1
            while i < len(qtys):
                section = price_data[price_data['amount_usd'] == qtys[i]]
                buy = section.index.min()
                last_amount = section_data.loc[section_data.index.max(), 'amount_usd']
                last_qty = section_data.loc[section_data.index.max(), 'sp_quantity']
                section['sp_quantity'] = ((section.loc[buy, 'amount_usd'] - last_amount) / section.loc[buy, 'sp_close']) + last_qty
                section['sp_gain_loss'] = (section['sp_close'] * section['sp_quantity']) - section['invested']
                section['sp_percent_gain'] = (section['sp_gain_loss'] / section['invested']) * 100
                section_data = section_data.append(section)
                i += 1
            portfolio_df = portfolio_df.append(section_data)
        # Standard add sp benchmark data to single buy share
        else:
            price_data['sp_quantity'] = (price_data.loc[purchase_date, 'amount_usd']/price_data.loc[purchase_date, 'sp_close'])
            price_data['sp_gain_loss'] = (price_data['sp_close'] * price_data['sp_quantity']) - price_data['invested']
            price_data['sp_percent_gain'] = (price_data['sp_gain_loss'] / price_data['invested']) * 100
            # Add the individual share df to portfolio df
            portfolio_df = portfolio_df.append(price_data)
    # Sort th portfolio df by index i.e dates
    portfolio_df['date'] = portfolio_df.index
    portfolio_df.sort_index(inplace=True)
    return portfolio_df

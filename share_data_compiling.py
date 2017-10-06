import pandas as pd
from datetime import datetime


# Function to find the latest closing proce available
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
    # Adding benchmark data
    bench_data = pd.DataFrame(dict(benchmark.historical.daily_data)).T
    # Add bench close price to performance data
    total_performance['sp_close'] = bench_data['adj_close']
    # Find the dates when investment amount changed
    test = total_performance.drop_duplicates(subset='cuml_fees', keep='first')
    test['amount'] = pd.to_numeric(test['amount'])
    test['sp_close'] = pd.to_numeric(test['sp_close'])
    test['sp_quantity'] = test['amount']*test['sp_close']
    print test
    print list(test['date'])
    # Add total percentage calculation
    total_performance['percentage_gain'] = (total_performance['gain_loss']/total_performance['invested'])*100
    return total_performance.to_json(orient='records')

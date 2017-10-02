import pandas as pd


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


def historic_totals(share_objects):
    for share in share_objects:
        # Create df of price data
        price_data = pd.DataFrame(dict(share.historical.daily_data))
        # Reverse columns and rows
        price_data = price_data.T
        # return the max of datetime objects in index adjusted close column
        day_one = price_data.index.min()
        fees = share.fees_usd
        amount = share.amount_usd
        invested = fees + amount

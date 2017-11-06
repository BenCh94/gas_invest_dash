import requests
import pandas as pd

iex_base = "https://api.iextrading.com/1.0"
stats_list = []


# Return a csv file containing all companies on iex exchange reference
def get_iex_company_list():
    r_companies = requests.get(iex_base + "/ref-data/symbols")
    company_list = r_companies.json()
    comps = pd.DataFrame(company_list)
    comps.to_csv('static/files/iex_comp_list.csv')


# Add a number t end of item names in list
def append_number(quarter, q):
    columns = quarter.keys()
    new_columns = [v+str(q) for v in columns]
    for i in range(0, len(columns)):
        quarter[new_columns[i]] = quarter.pop(columns[i])
    return quarter


# Create dictionary of all stock data and transform to DataFrame
def create_stock_dict(ticker_stats, fin_stats, ticker, name, index):
    stock_dict = {}
    stock_dict.update(ticker_stats.json())
    stock_dict.update(fin_stats)
    stock_dict['ticker'] = ticker
    stock_dict['name'] = name
    return stock_dict


# Find fiancials and stats and create DataFrame
def get_stats_financial(ticker, name, index):
    key_stats = "/stock/" + ticker + "/stats"
    financials = "/stock/" + ticker + "/financials"
    ticker_stats = requests.get(iex_base+key_stats)
    fin_stats = requests.get(iex_base+financials)
    finance_list = fin_stats.json()['financials']
    q = 1
    finance_dict = {}
    for item in finance_list:
        renamed_dict = append_number(item, q)
        finance_dict.update(renamed_dict)
        q += 1
    stats_list.append(create_stock_dict(ticker_stats, finance_dict, ticker, name, index))


# Create DF containing company stats and info and write to csv file
def create_quant_df():
    company_df = pd.read_csv('static/files/iex_comp_list.csv')
    company_df = company_df[company_df['type'] == 'cs']
    comp_dict = company_df.head(50).to_dict(orient='records')
    for company in comp_dict:
        print company['Unnamed: 0']
        get_stats_financial(company['symbol'], company['name'], company['Unnamed: 0'])
    quant_df = pd.DataFrame(stats_list)
    quant_df.to_csv('static/files/quant_analysis.csv')
    return quant_df


def percentile_scaled_net_assets(row):
    operating_assets = row['currentAssets1']
    operating_libilities = row['currentDebt1']
    total_assets = row['totalAssets1']
    snoa = (operating_assets - operating_libilities)/total_assets
    return snoa


def prob_fin_distress(row):
    mta = row['totalLiabilities1'] + row['marketcap']
    nimta = row['netIncome1']/mta


# quant_df = create_quant_df()
quant_df = pd.read_csv('static/files/quant_analysis.csv')


def quant_calculations(quant_df):
    quant_df['snoa'] = quant_df.apply(percentile_scaled_net_assets, axis=1)
    quant_df['p_snoa'] = quant_df['snoa'].rank(pct=True)
    quant_df['p_ebitda'] = quant_df['EBITDA'].rank(pct=True)
    print quant_df[quant_df['p_ebitda'] > 0.90]['ticker']


quant_calculations(quant_df)

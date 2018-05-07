import pandas as pd
import numpy
import requests as r

# IEX Base url
iex_base = "https://api.iextrading.com/1.0"


def get_financials(ticker):
    iex_fin_url = iex_base + "/stock/" + ticker + "/financials"
    api_call = r.get(iex_fin_url)
    fin_results = api_call.json()
    fin_df = pd.DataFrame(fin_results['financials'])
    fin_df.index = fin_df['reportDate']
    return fin_df.T


def get_key_stats(ticker):
    iex_fin_url = iex_base + "/stock/" + ticker + "/stats"
    api_call = r.get(iex_fin_url)
    stat_results = api_call.json()
    return stat_results


def get_details(ticker):
    iex_fin_url = iex_base + "/stock/" + ticker + "/company"
    api_call = r.get(iex_fin_url)
    comp_results = api_call.json()
    return comp_results


def glassdoor_results():
    glassdoor_url = "http://api.glassdoor.com/api/api.htm?v=1&format=json&t.p=120&t.k=fz6JLNDfgVs&action=employers&q=pharmaceuticals&userip=2a02:8084:4f62:a380:38f0:65e9:a481:7c18&useragent=Chrome/%2F4.0"
    glass_req = r.get(glassdoor_url)
    return glass_req


get_financials('mtch')
get_key_stats('mtch')
get_details('mtch')


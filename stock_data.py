from finpie import Fundamentals
import pandas as pd
from finpie.price_data import price_data
from dateutil import parser
from datetime import datetime
import requests
import calendar
import numpy as np


def get_company_symbol(company_name):
    resp = requests.get(
        url='https://www.macrotrends.net/assets/php/ticker_search_list.php')
    data = resp.json()

    for child in data:
        if company_name.lower() in child['n'].lower():
            return child['s']
    return None

def start_market(date):
  day = calendar.day_name[date.date().weekday()]
  if day == 'Monday':
    return 1
  else:
    return 0

def end_market(date):
  day = calendar.day_name[date.date().weekday()]
  if day == 'Friday':
    return 1
  else:
    return 0

def day_of_week(date):
  return date.dayofweek + 1

def get_data(company_name, start_date='2015-01-01', end_date='2021-03-31', freq='Q'):

    market_symbol = get_company_symbol(company_name)
    if market_symbol is None:
        print('Wrong company name !')
        return

    print('Scrapping data of ', market_symbol)
    data_price = price_data.historical_prices(market_symbol.split('/')[0])
    data_price = data_price[start_date: end_date]
    print('Prices scrapped ✅')

    data_indicators = Fundamentals(market_symbol.split('/')[0], freq=freq).ratios()
    data_indicators = data_indicators[start_date: end_date]
    print('Ratios scrapped ✅')

    for cl in data_indicators.columns.tolist():
        data_price[cl] = np.nan
    print('Merge features ✅')

    for idx1, i in enumerate(data_indicators.index):
        y = i.date().year
        m = i.date().month
        for idx2, n in enumerate(data_price.index):
            if n.date().year == y and n.date().month <= m and np.isnan(data_price['current_ratio'][idx2]):
                for cl in data_indicators.columns.tolist():
                    data_price[cl].iloc[idx2] = data_indicators[cl].iloc[idx1]
    data_price.drop(['ebitda_margin'], axis=1, inplace=True)
    print('Ratios added ✅')

    data_price['is_day_start_market'] = data_price.index.to_series().apply(start_market)
    data_price['is_day_end_market'] = data_price.index.to_series().apply(end_market)
    data_price['day_of_week'] = data_price.index.to_series().apply(day_of_week)


    return data_price


print(get_data('apple'))

from finpie import Fundamentals
import pandas as pd
from finpie.price_data import price_data
from dateutil import parser
from datetime import datetime
import requests
import datetime
import calendar
import numpy as np
import talib 
pd.options.mode.chained_assignment = None


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

def add_days_features(data):
    data['is_day_start_market'] = data.index.to_series().apply(start_market)
    data['is_day_end_market'] = data.index.to_series().apply(end_market)
    data['day_of_week'] = data.index.to_series().apply(day_of_week)
    return data

def add_technical_indicators_features(data):
    """ 
        Simple Moving Average (SMA)
        simple moving average (SMA) calculates the average of a selected range of prices,
        usually closing prices, by the number of periods in that range. 
    """
    data['SMA_5']     =   talib.SMA(data.close, timeperiod=5)
    data['SMA_10']    =   talib.SMA(data.close, timeperiod=10)
    data['SMA_20']    =   talib.SMA(data.close, timeperiod=20)
    data['SMA_50']    =   talib.SMA(data.close, timeperiod=50)

    """
        Exponential moving average (EMA)
        exponential moving average (EMA) is a weighted average of recent period's prices.
        It uses an exponentially decreasing weight from each previous price/period.
    """
    data['EMA_5']     =   talib.EMA(data.close, timeperiod=5)
    data['EMA_10']    =   talib.EMA(data.close, timeperiod=10)
    data['EMA_20']    =   talib.EMA(data.close, timeperiod=20)
    data['EMA_50']    =   talib.EMA(data.close, timeperiod=50)

    """
        Average True Range (ATR) 
        The true range indicator is taken as the greatest of the following:
        current high less the current low; the absolute value of the current
        high less the previous close; and the absolute value of the current
        low less the previous close. The ATR is then a moving average,
        generally using 14 days, of the true ranges. 
    """
    data['ATR_14']  =   talib.ATR(data.high, data.low,
                                  data.close, timeperiod=14)

    """
        Average Directional Index (ADX) 
        ADX indicates the strength of a trend in price time series.
        It is a combination of the negative and positive directional movements
        indicators computed over a period of n past days corresponding
        to the input window length (typically 14 days) 
    """

    data['ADX_14']  =   talib.ADX(data.high, data.low,
                                  data.close, timeperiod=14)
    
    """
        Commodity Channel Index (CCI)
        CCI is used to determine whether a stock is overbought or oversold.
        It assesses the relationship between an asset price,
        its moving average and deviations from that average. 
    """

    data['CCI_14']  =   talib.CCI(data.high, data.low,
                                  data.close, timeperiod=14)
    
    """
        Rate-of-change (ROC)
        ROC measures the percentage change in price between the
        current price and the price a certain number of periods ago. 
    """

    data['ROC_10']  =   talib.ROC(data.close, timeperiod=10)

    """
        Relative Strength Index (RSI)
        RSI compares the size of recent gains to recent losses,
        it is intended to reveal the strength or weakness of a price trend
        from a range of closing prices over a time period. 
    """

    data['RSI_14']  =   talib.RSI(data.close, timeperiod=14)

    return data

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
    print('Ratios added ✅')

    data_price = add_days_features(data_price)
    print('Days features added ✅')
    data_price = add_technical_indicators_features(data_price)
    print('Technical indicators added ✅')

    
    return data_price



print(get_data('apple'))

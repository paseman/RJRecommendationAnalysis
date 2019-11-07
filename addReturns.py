#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#===========================================================================================================
# Copyright (c) 2006-2018 Paseman & Associates (www.paseman.com).  All rights reserved.
#===========================================================================================================
"""
#===========================================================================================================
import pandas as pd
from pandas_datareader import data
import os
import datetime
import numpy as np
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 400)

#===========================================================================================================
#===========================================================================================================
def initPrice(row,dailyPricesDf,ticker):
  price = np.nan
  if row['has_history']:
    price = float(dailyPricesDf.loc[row["date"]][ticker])
    if 0.0 == price:
      price = np.nan
      print ticker, row["date"]
  return price

def finalPrice(row,dailyPricesDf,ticker,tradingDaysAhead):
  price = np.nan
  if row['has_history']:
    count=dailyPricesDf.shape[0]
    x = dailyPricesDf.index.get_loc(row["date"])
    if isinstance(x, slice): x = x.start
    i=min(tradingDaysAhead+x,count-1)
    price = float(dailyPricesDf.iloc[i][ticker])
  return price

#===========================================================================================================
def addReturns(recommendationFilename,recommendationsPlusReturnsFilename,historyFilename,benchmark="SPY",getDonMaurerData=False):

  # https://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_csv.html#pandas.read_csv
  recommendationDf = pd.read_csv(recommendationFilename,names=['date','ticker','price','recommendation'])
  tickers= list(set(recommendationDf['ticker'].values))+['SPY']

  if os.path.exists(historyFilename): # Don't recompute if we've done this once before.
    dailyPricesDf= pd.read_csv(historyFilename,index_col=[0],parse_dates=True)
    listed= dailyPricesDf.columns.values
    print len(listed),listed
  else:  # Download histories
    listed =[]
    delisted =[]
    dailyPricesDf = pd.DataFrame()
    now=datetime.datetime.now()
    for ticker in tickers:
      try: # Note: try/except allows us to do one pass despite "ticker not found" errors

        if getDonMaurerData:
          # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
          tempDf= pd.read_csv("stockhistory/yahoo/20181211/d/%s.txt"%ticker,
                              sep="\t",index_col=[0],parse_dates=True,usecols=[0,7])
          dailyPricesDf[ticker]=tempDf['CloseAdjustYahoo']
        else:  # Pull from yahoo
          tempDf= data.DataReader([ticker], 
                   start='2010-01-04', 
                   end=now.strftime("%Y-%m-%d"), 
                   data_source='yahoo')['Adj Close']

          dailyPricesDf[ticker]=tempDf[ticker]

        listed.append(ticker)
      except Exception as e:
        print e
        delisted.append(ticker)
    print "Found (Listed)",len(listed),listed
    print "Not Found (Delisted?)",len(delisted),delisted
    dailyPricesDf.to_csv(historyFilename)

  # note if ticker has (or does not have) a history in yahoo
  recommendationDf['has_history'] = recommendationDf.apply (lambda row: row['ticker'] in listed,axis=1)

  # Record price of ticker and benchmark at the point I received the email recommendation
  # prevent some weird pandas error
  recommendationDf["tickerInitPrice"]=0.0 
  recommendationDf["benchmarkInitPrice"]=0.0 
  recommendationDf["tickerInitPrice"]=recommendationDf.apply (lambda row: initPrice(row,dailyPricesDf,row["ticker"]),axis=1)
  recommendationDf["benchmarkInitPrice"]=recommendationDf.apply (lambda row: initPrice(row,dailyPricesDf,benchmark),axis=1)

  # Record price of ticker and benchmark at the point I received the email recommendation
  for tradingDaysAhead in [63,126,189,253]:
    # Record price of ticker and how much it changed 63,126,189,253 days after the recommendation
    tfp = "ticker%dFinalPrice"%tradingDaysAhead
    tpc = "ticker%dPercentChange"%tradingDaysAhead
    # prevent some weird pandas error
    recommendationDf[tfp]=0.0 
    recommendationDf[tpc]=0.0 
    recommendationDf[tfp]=recommendationDf.apply (lambda row: finalPrice(row,dailyPricesDf,row["ticker"],tradingDaysAhead),axis=1)
    recommendationDf[tpc]=recommendationDf.apply (lambda row: (row[tfp]-row["tickerInitPrice"])/row["tickerInitPrice"],axis=1)

    # Record price of benchmark and how much it changed 63,126,189,253 days after the recommendation
    bfp = "benchmark%dFinalPrice"%tradingDaysAhead
    bpc = "benchmark%dPercentChange"%tradingDaysAhead
    # prevent some weird pandas error
    recommendationDf[bfp]=0.0 
    recommendationDf[bpc]=0.0 
    recommendationDf[bfp]=recommendationDf.apply (lambda row: finalPrice(row,dailyPricesDf,benchmark,tradingDaysAhead),axis=1)
    recommendationDf[bpc]=recommendationDf.apply (lambda row: (row[bfp]-row["benchmarkInitPrice"])/row["benchmarkInitPrice"],axis=1)
    
    # Record percent difference between ticker price and benchmark price 63,126,189,253 days after the recommendation
    recommendationDf["benchmark%dAdjustedPercentChange"%tradingDaysAhead]=recommendationDf[tpc]-recommendationDf[bpc]

  recommendationDf.to_csv(recommendationsPlusReturnsFilename)
      
  return recommendationDf
#===========================================================================================================
import time

if __name__ == '__main__':
  start_time = time.time()
  # Step1: Download pdf Files (in "downloadAttachments.py")
  # read_email_from_gmail(''myFinance/PattyDewey'')  
  # Step 2: Extract Recommendations from files (in "extractRecommendations.py")
  # extractRecommendations("myFinance/PattyDewey/*.pdf","20190909recommendations.csv")
  # Step 3: Annotate Recommendations file with Returns (in "addReturns.py")
  addReturns("logs/20191105recommendations.csv","logs/RecommendationsPlusReturnsYahoo.csv","logs/20190911 Yahoo history.csv")
  addReturns("logs/20191105recommendations.csv","logs/RecommendationsPlusReturnsDonMaurer.csv","logs/20191105_1109 DonMaurer history.csv",benchmark="SPY",getDonMaurerData=True)
  # Note:  This step creates history.csv as a side effect, and reuses it on subsequent runs

  print("Finished in --- %s seconds ---" % (time.time() - start_time))

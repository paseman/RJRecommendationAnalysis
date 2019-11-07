#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#===========================================================================================================
# Copyright (c) 2006-2019 Paseman & Associates (www.paseman.com).  All rights reserved.
#===========================================================================================================
"""
#===========================================================================================================
import numpy as np
import pandas as pd
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 400)
from collections import Counter
from scipy import stats
import matplotlib.pyplot as plt

#===========================================================================================================
#===========================================================================================================
Grecommendations = ['outperform','strong buy','market perform','underperform']
Gtdas=[63,126,189,253]
#===========================================================================================================
def getSelectedColumnValues(df,recommendationLabel,columnLabel):
  a= df[(df['recommendation'] == recommendationLabel)] [columnLabel].values
  return a[~np.isnan(a)]

#===========================================================================================================
def plotReturnsOverTimeByRecommendation(recommendationDf,tickerSource,columnPattern):
  global Grecommendations, Gtdas
  ret=[]
  fig=plt.figure()
  for recommendation in Grecommendations:
    for tradingDaysAhead in Gtdas:
      pRets=getSelectedColumnValues(recommendationDf,recommendation,columnPattern%tradingDaysAhead)
      p = dict(zip(["ticker source","column","Alabel","days","AMu","Astd","Acnt"],(tickerSource,columnPattern,recommendation,tradingDaysAhead,pRets.mean(),pRets.std(),len(pRets))))
      ret.append(p)
    #print ret[-4:]
    ys = [e["AMu"] for e in ret[-4:]]
    plt.plot([0]+Gtdas,[0.0]+ys,label=recommendation)

  plt.xlabel('Days')
  plt.ylabel('Return')
  plt.title(tickerSource+" "+columnPattern)
  plt.legend()
  plt.grid(True)
  fig.savefig("imgs/%s-%s.png"%(tickerSource,columnPattern))
  return ret

#===========================================================================================================
def returnsOverTimeByRecommendation(recommendationDf,tickerSource):
  ret1=plotReturnsOverTimeByRecommendation(recommendationDf,tickerSource,'benchmark%dAdjustedPercentChange')
  ret2=plotReturnsOverTimeByRecommendation(recommendationDf,tickerSource,'benchmark%dPercentChange')
  ret3=plotReturnsOverTimeByRecommendation(recommendationDf,tickerSource,'ticker%dPercentChange')
  return ret1+ret2+ret3

#===========================================================================================================
def basicAnalysis(recommendationDf,tickerSource,printTickerLists=False):
  print "\n","*"*30,"\n",tickerSource

  rc=Counter(recommendationDf['recommendation'])
  print "\n%d recommendations"%sum(rc.values())
  print rc
  if printTickerLists: print pformat(sorted(rc.items())),"\n"

  tc=Counter(recommendationDf['ticker'])
  print "\n%d recommendations for %d tickers"%(sum((tc.values())),len(tc.keys()))
  if printTickerLists: print sorted(tc.items(),reverse=True,key= lambda x: x[1])

  c= Counter(recommendationDf.query("has_history")['ticker'])
  print "\n%d Recommendations for %d tickers with has_history"%(sum(c.values()),len(c.keys()))
  if printTickerLists: print c,"\n"

  c= Counter(recommendationDf.query("ticker253PercentChange.isnull()")['ticker'])
  print "\n%d Recommendations for %d tickers with no prices one year later (acquired or out of business)"%(sum(c.values()),len(c.keys()))
  if printTickerLists: print c,"\n"

  c= Counter(recommendationDf.query("ticker63PercentChange.isnull()")['ticker'])
  print "\n%d Recommendations for %d tickers with no prices 63 days later (acquired or out of business)"%(sum(c.values()),len(c.keys()))
  if printTickerLists: print c,"\n"

  # Find recommendations that are significantly different from the benchmark
  for recommendation in Grecommendations:
    for tda in Gtdas:
      tRets= getSelectedColumnValues(recommendationDf,recommendation,"ticker%dPercentChange"%tda)
      bRets= getSelectedColumnValues(recommendationDf,recommendation,"benchmark%dPercentChange"%tda)
      ttest=stats.ttest_ind(bRets,tRets)
      if ttest.statistic > 3.64:
        #print recommendation,tda,tRets.mean(),tRets.std(),len(tRets),bRets.mean(),bRets.std(),len(bRets),tRets.mean()-bRets.mean(),ttest.statistic,ttest.pvalue
        print "%-15s %3d %+5.3f %+5.3f"%(recommendation, tda, tRets.mean()*100, bRets.mean()*100)
  
  # Find recommendations that are significantly different from each other
  for i,Lrecommendation in enumerate(Grecommendations):
    for j,Rrecommendation in enumerate(Grecommendations):
      if i<j:
        for tda in Gtdas:
          lRets= getSelectedColumnValues(recommendationDf,Lrecommendation,"ticker%dPercentChange"%tda)
          rRets= getSelectedColumnValues(recommendationDf,Rrecommendation,"ticker%dPercentChange"%tda)
          ttest=stats.ttest_ind(lRets,rRets)
          if ttest.statistic > 3.64:
            #print recommendation,tda,tRets.mean(),tRets.std(),len(tRets),bRets.mean(),bRets.std(),len(bRets),tRets.mean()-bRets.mean(),ttest.statistic,ttest.pvalue
            print "%-15s %-15s %3d %+5.3f %+5.3f %+5.3f %+5.3f"%(Lrecommendation,Rrecommendation, tda, lRets.mean()*100, rRets.mean()*100,ttest.statistic,ttest.pvalue)
  
#===========================================================================================================
def deltas(df1,df2,aQuery):
  ts1=df1.query(aQuery)['ticker'].values
  ts2=df2.query(aQuery)['ticker'].values
  d1s = set(ts1).difference(set(ts2))
  d2s = set(ts2).difference(set(ts1))
  print "\n",aQuery,len(ts1),len(ts2)
  print "Y-M",len(d1s),d1s
  print "M-Y",len(d2s),d2s
  #for d1 in d1s: print df1[(df1['ticker'] == d1)]
  #for d2 in d2s: print df2[(df2['ticker'] == d2)]

#===========================================================================================================
def topNreturns(df,recommendation='underperform',returnColumn="ticker63PercentChange",n=20):
  #returns = np.array(sorted(getSelectedColumnValues(df2,'underperform',"ticker126PercentChange")))
  #print returns.mean(), returns
  select= df[(df['recommendation'] == recommendation)].sort_values([returnColumn,"ticker"], ascending=[0,0])
  #return select[["date","recommendation","ticker","tickerInitPrice","ticker63FinalPrice","ticker63PercentChange"]]
  return select[["date","ticker","tickerInitPrice",returnColumn]][:n]
#===========================================================================================================
import time
from pprint import pprint,pformat

if __name__ == '__main__':
  print np.__version__
  print pd.__version__
  start_time = time.time()
  # Step1: Download pdf Files (in "downloadAttachments.py")
  # read_email_from_gmail(''myFinance/PattyDewey'')  
  # Step 2: Extract Recommendations from files (in "extractRecommendations.py")
  # extractRecommendations("myFinance/PattyDewey/*.pdf","20190909recommendations.csv")
  # Step 3: Annotate Recommendations file with Returns (in "addReturns.py")
  # addReturns("logs/20191105recommendations.csv","logs/RecommendationsPlusReturnsYahoo.csv","logs/20190911 Yahoo history.csv")
  # addReturns("logs/20191105recommendations.csv","logs/RecommendationsPlusReturnsDonMaurer.csv","logs/20191105_1109 DonMaurer history.csv",benchmark="SPY",getDonMaurerData=True)
  # Note:  This step creates history.csv as a side effect, and reuses it on subsequent runs
  # Step 4 - See how the recommendations did (in "analyzeRecommendations.py")

  df1=pd.read_csv("logs/RecommendationsPlusReturnsYahoo.csv")
  ds1="Yahoo tickers"
  df2=pd.read_csv("logs/RecommendationsPlusReturnsDonMaurer.csv")
  ds2="Don tickers"

  basicAnalysis(df1,ds1)
  basicAnalysis(df2,ds2)
  deltas(df1,df2,"has_history")    
  deltas(df1,df2,"not has_history")    
  deltas(df1,df2,"ticker63PercentChange.isnull()")    
  deltas(df1,df2,"ticker253PercentChange.isnull()")
  #print topNreturns(df1)
  #print topNreturns(df2)
  #print pd.DataFrame(returnsOverTimeByRecommendation(df1,ds1)+returnsOverTimeByRecommendation(df2,ds2))

  
  print("Finished in --- %s seconds ---" % (time.time() - start_time))

  #plt.show()

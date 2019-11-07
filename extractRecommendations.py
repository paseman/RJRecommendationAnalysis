#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#===========================================================================================================
# Copyright (c) 2006-2018 Paseman & Associates (www.paseman.com).  All rights reserved.
#===========================================================================================================
"""
#===========================================================================================================
import PyPDF2
import re
#https://stackoverflow.com/questions/34837707/how-to-extract-text-from-a-pdf-file
def extract_pdf(filename):
  pdfReader = PyPDF2.PdfFileReader(open(filename, 'rb'))
  # NOTE: extractText may not work for all pdf files
  return "".join([pdfReader.getPage(i).extractText() for i in range(pdfReader.numPages)])

#===========================================================================================================
#filename='PattyDewey/Energy/2010_09_03_iEne090310b_061648.pdf'
#extract_pdf(filename)
#===========================================================================================================
from glob import glob
ratings = ['Not Covered','Underperform','Market Perform','Market Perf','Outperform','Outperfrom','Strong Buy']
def extractRecommendations(inputPath,outputFile="recommendations.csv"):
  filenames = sorted(glob(inputPath))
  tickers = set([]);  prices = set([]);  ratings = set([]);
  with open(outputFile,'w') as of:
    for filename in filenames:
      s=extract_pdf(filename)
      print s
      pos=filename.rfind("/")+1
      date = filename[pos:pos+10].replace("_","-")
      # https://stackoverflow.com/questions/38999344/extract-string-within-parentheses-python
      #Heuristic to exract recommendation strings.
      ticker_price_ratings = [ss.replace("\n","") for ss in re.findall('\(([^)]+)', s) if 2==ss.count("/") and "/$" in ss and 1==ss.count("$") and len(ss) < 25]
      for ticker_price_rating in ticker_price_ratings:
        ticker,price,rating = ticker_price_rating.split("/")
        if "$" in rating and "$" not in price: temp=price; price=rating; rating=temp
        ticker=ticker.strip();price=price.strip();rating=rating.strip().lower()
        if rating=='outperfrom': rating = 'outperform'
        tickers.add(ticker);prices.add(price);ratings.add(rating);
        of.write("%s,%s,%s,%s\n"%(date,ticker,price,rating))
      print date, ticker_price_ratings
      
  print "\n",tickers
  print "\n",ratings
  print "\n",prices
#===========================================================================================================
import time
if __name__ == '__main__':
  start_time = time.time()
  # Step1: Download pdf Files (in "downloadAttachments.py")
  # read_email_from_gmail(''myFinance/PattyDewey'')  
  # Step 2: Extract Recommendations from files (in "extractRecommendations.py")
  extractRecommendations("myFinance/20190909 PattyDewey/*.pdf","logs/20191106recommendations.csv")
  # Finished in --- 23509.6650581 seconds --- 6.5 hours
  print("Finished in --- %s seconds ---" % (time.time() - start_time))

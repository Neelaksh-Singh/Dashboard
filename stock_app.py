import streamlit as st
import pandas as pd
import numpy as np
import requests
from dotenv import load_dotenv
import os
import finnhub
from datetime import date,timedelta
import warnings
warnings.filterwarnings('ignore')

load_dotenv()
api_key = os.getenv('api_key')

finnhub_client = finnhub.Client(api_key=api_key)


import yfinance as yf
from yahoo_fin.stock_info import get_data
import yahoo_fin.stock_info as si
from yahoo_fin import news
import time

import plotly.graph_objects as go
from plotly.subplots import make_subplots

def to_human_readable(num):
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    
    return '%.2f%s' % (num, ['', 'K', 'M', 'B', 'T', 'P'][magnitude])

# ''' Dashboard Sidebar '''
st.sidebar.title('Choices')
options = st.sidebar.selectbox('What are you looking for ? ',
['Charts', 'General View', 'Trends'],0,help='Choose from the Following Options')


# ''' Getting Data '''

# Getting Data from Major US Stock Exchanges 
d1 = pd.DataFrame(si.tickers_sp500())
d2 = pd.DataFrame(si.tickers_nasdaq())
d3 = pd.DataFrame(si.tickers_dow())
d4 = pd.DataFrame(si.tickers_nifty50())
d5 = pd.DataFrame(si.tickers_other())

# Gathering Symbols

s1 = set(symbol for symbol in d1[0].values.tolist())
s2 = set(symbol for symbol in d2[0].values.tolist())
s3 = set(symbol for symbol in d3[0].values.tolist())
s4 = set(symbol for symbol in d4[0].values.tolist())
s5 = set(symbol for symbol in d4[0].values.tolist())

temp_symbols = set.union(s1,s2,s3,s4,s5)

# ''' Few of these stocks are undesirable, thus can be ignored.

#     We ignore stocks with following Suffixes:

#         W means there are outstanding warrants
#         R means there is some kind of “rights” issue
#         P means “First Preferred Issue”
#         Q means bankruptcy

# '''
blacklist = ['W', 'R', 'P', 'Q']

symbols = set()

for symbol in temp_symbols:
    if len(symbol)> 4 and symbol[-1] in blacklist:
        pass
    else:
        symbols.add(symbol)

symbols = sorted(symbols)

#print(symbols)

#''' Dashboards '''


### Discussion View

if options=='Trends':
    symbol = st.sidebar.selectbox('Stock Symbol', symbols,index=23,help='Enter Valid Stock Ticker Symbol')
    st.header('Lastest Discussion on '+ symbol + ' over the past 10 Days')
    
    # Querying Data
    curr_day = date.today()
    past_30_days = date.today() - timedelta(days=10)
    query = finnhub_client.company_news(symbol=symbol, _from=past_30_days, to=curr_day)

    # Displaying logic
    
    if len(query)==0:
        st.write(f'{symbol} not available!')
    
    else:
        #st.write('Showing 30 most recent talks shared on {symbol}.')
        st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

        for data in query:
            if data['source'] == 'CNBC':
                continue
            col1, col2 = st.columns([10,20])

            with col1:
                image_link = data['image']
                if len(image_link)==0:
                    st.image('no-image-found.png')
                else:
                    st.image(image_link)
            with col2:
                st.write(data['source'])

                st.write('Headlines - ' + data['headline'])
                st.write(f"[Full details]({data['url']})")

            st.write(data['summary'])
            st.markdown("""<hr style="height:2px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
            

### Charts View

if options=='Charts':
    
    symbol = st.sidebar.selectbox('Stock Symbol', symbols,index=23,help='Enter Valid Stock Ticker Symbol')
    st.header('Chart Dashboard for - '+symbol)
    st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

    stock = yf.Ticker(symbol)
    try:
        
        st.markdown("""<hr style="height:5px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
        try:
            yearly_income_statement = si.get_income_statement(symbol)
            st.subheader('Yearly Income Statement of '+ str(symbol))
            st.write(yearly_income_statement)

            
            # get quarterly income statement data
            quarterly_income_statement = si.get_income_statement(symbol, yearly = False)
            st.subheader('Quarterly Income Statement of '+ str(symbol))
            st.write(quarterly_income_statement)


            cashflow = si.get_cash_flow(symbol)
            st.subheader('Cash Flow Statement of '+ str(symbol))
            st.write(cashflow)
        except:
            pass
        st.markdown("""<hr style="height:5px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
        try:
            st.subheader('Yahoo Finance News for '+ str(symbol))
            stock_news = news.get_yf_rss(symbol)
            
            st.markdown("""<hr style="height:2px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
            count = 1 
            for message in stock_news:
                st.write(str(count)+'. '+message['title'])
                st.write('Published '+message['published'])
                st.write(message['summary'])
                #st.write('_______________________________________________________________')
                st.markdown("""<hr style="height:2px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
                count+=1
        except:
            pass
    except:
        st.error('Please enter a valid stock ticker')

    


### General View

if options=='General View':
    st.header('General Dashboard')
    st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
    
    st.subheader('Table of the top 100 undervalued large caps')
    large_cap_table = si.get_undervalued_large_caps()
    st.write(large_cap_table)

    st.subheader('Table of S&P 500')
    tickers = si.tickers_sp500(include_company_data = True)
    st.write(tickers)

    st.subheader('Table of Nasdaq')
    tickers = si.tickers_nasdaq(include_company_data = True)
    st.write(tickers)

    st.subheader('Table of Nifty 50')
    tickers = si.tickers_nifty50(include_company_data = True)
    st.write(tickers)

    st.subheader('Table of Dow Jones')
    tickers = si.tickers_dow(include_company_data = True)
    st.write(tickers)

    st.subheader('Table of FTSE 100 Index')
    tickers = si.tickers_ftse100(include_company_data = True)
    st.write(tickers)

    




    
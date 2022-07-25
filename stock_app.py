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
    magnitude = 0
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

    
    st.header('Stock Chart Dashboard - '+symbol)
    st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
    
    stock = yf.Ticker(symbol)
    
    try: 
        st.subheader(symbol.upper()+' : '+stock.info['shortName'])
    
        col1, col2, col3 = st.columns(3)
        col4, col5, col6 = st.columns(3)
        col7, col8, col9 = st.columns(3)
        mkt_status = si.get_market_status()
        
        col1.metric('Market Status',mkt_status)
        
        period_name = st.sidebar.selectbox('Last Period', ['yesterday','1 day', '5 day', '1 month', '3 months','6 months', '1 year', '2 years', '5 years', '10 years', 'max'],index=5,help='select period of stock')
        
        interval_list = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
        interval_dict = {'yesterday':(0,9), 
                        '1 day':(0,9), 
                        '5 day':(0,10), 
                        '1 month':(1,12), 
                        '3 months':(7,13), 
                        '6 months':(7,13), 
                        '1 year':(7,13), 
                        '2 years':(7,13), 
                        '5 years':(8,13), 
                        '10 years':(8,13), 
                        'max':(8,13)
                        }
        
        interval = st.sidebar.selectbox('Interval', interval_list[interval_dict[period_name][0]:interval_dict[period_name][1]],index=1,help='select time interval of stock')
        
        period_dict = {'1 day':'1d', 
        '5 day':'5d', 
        'yesterday':'ytd', 
        '1 month':'1mo', 
        '3 months':'3mo', 
        '6 months':'6mo', 
        '1 year':'1y', 
        '2 years':'2y', 
        '5 years':'5y', 
        '10 years':'10y', 
        'max':'max'}

                 
        
        quote_data = si.get_quote_data(symbol)
        quote_table = si.get_quote_table(symbol)
        

        live_price = si.get_live_price(symbol)
        col2.metric('Current Market Price',round(live_price,2),delta=str(round(quote_data['regularMarketChange'],2))+' ('+str(round(quote_data['regularMarketChangePercent'],2))+'%)')

        if 'postMarketPrice' in quote_data:
            col3.metric('Post Market Price',round(quote_data['postMarketPrice'],2),delta=str(round(quote_data['postMarketChange'],2))+' ('+str(round(quote_data['postMarketChangePercent'],2))+'%)')

        if 'forwardPE' in quote_data:
            col4.metric('Forward P/E',str(round(quote_data['forwardPE'],2)))
        if 'priceToBook' in quote_data:
            col5.metric('Price to Book',str(round(quote_data['priceToBook'],2)))
        if 'averageAnalystRating' in quote_data:
            col6.metric('Analyst Rating - '+quote_data['averageAnalystRating'].split('-')[1],str(quote_data['averageAnalystRating'].split('-')[0]) + '/ 5.0',
                    delta=None, delta_color="off")

        if 'marketCap' in quote_data:
            mkt_cap_value = quote_data['marketCap']
            
            col7.metric('Market Cap',str(to_human_readable(mkt_cap_value)),
                    delta=None, delta_color="off")

        if 'EPS (TTM)' in quote_table:
            col8.metric('EPS (TTM)',quote_table['EPS (TTM)'],
                    delta=None, delta_color="off")
        if 'Forward Dividend & Yield' in quote_table:
            col9.metric('Forward Dividend & Yield',quote_table['Forward Dividend & Yield'],
                    delta=None, delta_color="off")
        	
        
        st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
        
        # get historical market 
        data = stock.history(period=period_dict[period_name],interval=interval)
        


        st.subheader(symbol.upper()+ ' Chart - '+period_name)
         
        fig = make_subplots(rows=2, cols=1, row_heights=[0.8, 0.2], 
                            vertical_spacing=0,shared_xaxes=True,
                            
        ) 

        
        fig.add_trace(go.Candlestick(x=data.index,open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
                                name=symbol), row=1, col=1)

        fig.add_trace(go.Scatter(x=data.index,y=data['Volume'], marker_color='#fae823', name='VOL', hovertemplate=[]), row=2, col=1)

        
        fig.update_layout({'plot_bgcolor': "#21201f", 'paper_bgcolor': "#21201f", 'legend_orientation': "h"},
                    legend=dict(y=1, x=0),
                    font=dict(color='#dedddc'), dragmode='pan', hovermode='x unified',
                    margin=dict(b=20, t=0, l=0, r=40))

        fig.update_yaxes(showgrid=False, zeroline=False, showticklabels=True,
                    showspikes=True, spikemode='across', spikesnap='cursor', showline=False, spikedash='solid')

        
        fig.update_xaxes(showgrid=False,type='category',zeroline=False,
        showspikes=True, spikemode='across', spikesnap='cursor', showline=False, spikedash='solid' )

        fig.update_layout(title=symbol.upper()+' Price - '+period_name,
                        yaxis_title='Price',
                        xaxis_rangeslider_visible=False,
                        height=700) 
                
        
        st.plotly_chart(fig, use_container_width=True)

        
        data['MA50'] = data['Open'].rolling(50).mean()
        data['MA200'] = data['Open'].rolling(200).mean()
        
        st.line_chart(data=data[['Close','Open','MA50','MA200']],use_container_width=True)

        

        st.image(f"https://finviz.com/chart.ashx?t={symbol}",caption=symbol+' stock chart retrieved from finviz')
        try:
            
            # get yearly income statement data
            income_statement_yearly = si.get_income_statement(symbol)
            st.subheader('Yearly Income Statement of '+ str(symbol))
            st.write(income_statement_yearly)

            
            # get quarterly income statement data
            income_statement_quarterly = si.get_income_statement(symbol, yearly = False)
            st.subheader('Quarterly Income Statement of '+ str(symbol))
            st.write(income_statement_quarterly)


            cashflow = si.get_cash_flow(symbol)
            st.subheader('Cash Flow Statement of '+ str(symbol))
            st.write(cashflow)


        except:
            pass

        try:
            st.subheader('Yahoo Finance News of '+ str(symbol))
            stock_news = news.get_yf_rss(symbol)
            st.write('Displaying '+str(len(stock_news))+f' most recent yahoo finance news of {symbol}.')

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
        #st.write(stock_news)
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

    




    
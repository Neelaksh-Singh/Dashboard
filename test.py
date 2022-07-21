from dotenv import load_dotenv
import os
import finnhub
from datetime import date,timedelta

load_dotenv()
api_key = os.getenv('api_key')

finnhub_client = finnhub.Client(api_key=api_key)

curr_day = date.today()
past_30_days = date.today() - timedelta(days=30)
# print(past_30_days)
query = finnhub_client.company_news('AAON', _from=past_30_days, to=curr_day)
# print(len(query))
# print(date.today())
for data in query:
        print(data['image'])
        print(data['source'])
        print(data['url'])
        print(data['summary'])
        print('########################')
            
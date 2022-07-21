import requests #https://realpython.com/python-requests/#:~:text=The%20requests%20library%20is%20the,consuming%20data%20in%20your%20application.
from glob import glob #for editing files in system
from bs4 import BeautifulSoup #https://www.crummy.com/software/BeautifulSoup/bs4/doc/#name
import pandas as pd
from datetime import datetime
from time import sleep

HEADERS = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})

def search_prd_info(interval_count = 1, interval_hours = 1):
  """
  The function loads a csv file containing all the items from amazon named: Tracker_PRODUCTS.csv
  with headers - [link, code, buy_below]

  It requires a file called SEARCH_HISTORY.xlsx to start saving the results. 
  An empty file can be used on the first time using the script

  Parameters:
  1 - interval_count(optional): Default = 1, the no. of iterations you want the script to run a search
  on the full list

  2 - interval_hours(optional): Default is 6

  Return:
  New .xlsx file with previous search history and results from current search

  """
  track = pd.read_csv("/content/drive/My Drive/Tracker_PRODUCTS.csv", sep=",")
  track_URLS = track.link
  track_log = pd.DataFrame()
  #helps to know when the website is scraped for each product
  now = datetime.now().strftime('%Y-%m-%d-%Hh%Mm') #strftime - used to convert data&time to their string representation
  interval = 0

  while interval < interval_count:
    for i, url in enumerate(track_URLS):
      page = requests.get(url, headers = HEADERS)
      if page.status_code != 200:
        print('Not Found.')
        continue
      soup = BeautifulSoup(page.content, features="lxml")
      #product title
      title = soup.find(id='productTitle').get_text().strip()

      #to prevent script from crashing when there is no price provided
      try:
        price = soup.find("span", {"class": "a-offscreen"}).get_text().strip() #for .ae site we need to use class: a-offscreen
      except:
        price = ''
      
      #review score
      try:
        review_score = soup.find("span",{"class": "a-icon-alt"}).get_text().replace(" out of ",'/').replace('stars','').strip()
      except:
        review_score = 'None'

      #no of reviews
      try:
        # review_count = soup.find(id = "acrCustomerReviewText").get_text().replace(' ratings','').strip()
        review_count = int(soup.select(id = "acrCustomerReviewText")[0].get_text().split(' ')[0].replace(".",''))
      except:
        review_count = 'None'

      #availability
      try:
        stock = soup.find(id = "availability").get_text().strip().replace('.','')
      except:
        stock = 'No Stock'
      log = pd.DataFrame({'Date': now.replace('h',':').replace('m',''),
                          'Code': track.code[i],
                          'URL': url,
                          'Title': title,
                          'Buy_below': track.buy_below[i],
                          'Price': price,
                          'Stock': stock,
                          'Review_score': review_score,
                          'Review_count': review_count}, index=[i])
      try:
        #can enter email alert here
        if price<track.buy_below[i]:
          print('ALERT!! Buy now '+track.code[i])
      except:
        pass #when we don't get price from the website
      
      track_log = track_log.append(log)  
      print('appended '+ track.code[i] + '\n' + title + '\n\n')
      sleep(5)

    interval+=1
    sleep(interval_hours*1*1) #not sure why extra '*1'
    print('End of interval '+str(interval))
#after the run, the search history record is checked and appends this result to it, saving a new file
#the first file should have all the headers to append to
# wb = gc.open_by_url('https://docs.google.com/spreadsheets/d/1u7A0cmK5JhV2JCIscAG0O7Z8-dftg8g6FIqfoLJAu74/edit#gid=0')
# sheet = wb.sheet1
# set_with_dataframe(sheet, track_log)

    print(track_log)

# last_search = glob('file path')[-1]
# search_hist = pd.read_excel(last_search)
# final_df = search_hist.append(track_log, sort = False)

# final_df.to_excel('/content/drive/My Drive/Amazon_items.xlsx'.format(now), index=False)
search_prd_info()
print('End of search')
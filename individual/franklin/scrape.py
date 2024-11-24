import requests
import pandas as pd 
from datetime import datetime
from zipfile import ZipFile
import os
from io import StringIO
from requests.auth import HTTPBasicAuth
import json
from bs4 import BeautifulSoup


def scrape_feed_key():

    current_date = datetime.today()

    year = current_date.year
    month = current_date.month - 2

    # GTFS is always atleast 2 months ahead. We need to add a 3 month buffer. So we need to get 3 months past the current date. If today is october, we are looking for July data. 

    # GTFS for TTC
    url = 'https://www.transit.land/feeds/f-dpz8-ttc'

    response = requests.get(url)

    # Parse the data using an html parser
    soup = BeautifulSoup(response.content, "html.parser")

    # The data containing all the feed versions we need is wrapped in tr element
    for tr in soup.find_all('tr'):

        for td in tr.find_all('td'):
            if f"{year}-{str(month).zfill(2)}" in td.text:
                # print(tr)
                # Find the first <a> tag with an href attribute
                a_tag = tr.find('a', href=True)  
                if a_tag:
                    feed_key = a_tag['href'].split("versions/")[-1]
                    # return the first instance because the first instance will be the data in the earliest date show true column
                    return feed_key

def retrieve_gtfs_dates(feed_onestop_id):
   
    # gtfs = 'http://opendata.toronto.ca/toronto.transit.commission/ttc-routes-and-schedules/OpenData_TTC_Schedules.zip'
    dates = 'https://transit.land/api/v2/rest/feed_versions/{feed_onestop_id}?apikey={api_key}'
    gtfs_zip = "https://transit.land/api/v2/rest/feed_versions/{feed_version_key}/download?apikey={api_key}"
    api_key = 'JcYL2svv0eB7Fo2ETqwUnaEP4B4c762w'
    
    try:

        dates_url = dates.format(feed_onestop_id = feed_onestop_id, api_key = api_key)
        # print(test_url)

        # file may be large
        response = requests.get(url=dates_url, headers={'apikey': api_key}, stream=True)
        
        # Raise an error if bad status code
        response.raise_for_status() 

        data = response.json()
        
        feed_version = data.get("feed_versions", [{}])[0] # 

         # Extract dates
        earliest_start_date = feed_version.get("earliest_calendar_date")
        latest_end_date = feed_version.get("latest_calendar_date")
        
        # Convert dates to datetime objects
        if earliest_start_date:
            earliest_start_date = datetime.strptime(earliest_start_date, "%Y-%m-%d")
        if latest_end_date:
            latest_end_date = datetime.strptime(latest_end_date, "%Y-%m-%d")

        # Download the actual zip file associated with the feed_onestop_id (SHA1)
        gtfs_zip_url = gtfs_zip.format(feed_version_key=feed_onestop_id, api_key = api_key)
        response = requests.get(url=gtfs_zip_url, headers={'apikey': api_key}, stream=True)
        response.raise_for_status() 

        # Write the chunks and download the zip file
        with open('GTFS{date1}to{date2}.zip'.format(date1=earliest_start_date.date(), date2=latest_end_date.date()), "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

            
        # file = "{feed_onestop_id}.zip"
        # location = "./individual/franklin/"
        # path = location + file.format(feed_onestop_id = feed_onestop_id)
        
        # with open(path, "wb") as file:
        #     for chunk in response.iter_content(chunk_size=8192):
        #         file.write(chunk)

        # # opening the zip file in READ mode 
        # with ZipFile(path, 'r') as zip: 
        #     # printing all the contents of the zip file 
        #     zip.printdir() 
        
        #     # TODO: GTFS is like months ahead of the COT data
        #     # Extract only calendar.txt file
        #     zip.extract('calendar.txt', path = location)
    
        #     # type bytes
        #     calendar = zip.read('calendar.txt')
            
        #     # Decode the bytes and convert into a df
        #     data_str = calendar.decode('utf-8')
        #     df = pd.read_csv(StringIO(data_str))
            
        #     # The format we are receiving the date data
        #     date_format = '%Y%m%d'
            
        #     start_date = datetime.strptime(str(df['start_date'][0]), date_format)
        #     end_date = datetime.strptime(str(df['end_date'][0]), date_format)
            
        
        # # Remove the files we downloaded
        # os.remove(path)    
        # os.remove(location + 'calendar.txt')

        return [earliest_start_date, latest_end_date]
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        
def retrieve_corresponding_cot(dates):
    year = dates[0].year
    
    # Start month and day
    start_month = dates[0].month
    start_day = dates[0].day
    
    # End month and day
    end_month = dates[1].month
    end_dau = dates[1].day


    # City of toronto API ("really just the download button link") to download their dataset
    cot = 'https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/e271cdae-8788-4980-96ce-6a5c95bc6618/resource/7823b829-9952-4e4c-ac8f-0fe2ef53901c/download/ttc-bus-delay-data-{}.xlsx'

    # Obtain the request at the link
    response = requests.get(cot.format(year), stream=True)
    
    # Raise an error if bad status code
    response.raise_for_status() 
    
    file = 'temp.xlsx'
    location = "./individual/franklin/"
    path = location + file

    # Write to an excel file
    with open(path, 'wb') as f:
        f.write(response.content)

    # Convert to a df
    df = pd.read_excel(path) 

    # Convert the whole column to datetime object for comparison
    df['Date'] = pd.to_datetime(df['Date']).dt.date

    # print(dates)
    df2 = df.loc[df["Date"].between(dates[0].date(), dates[1].date())]
    df2.to_csv('COT{date1}to{date2}'.format(date1=dates[0].date(), date2=dates[1].date()), index=False)

    os.remove(path)
    
if __name__ == '__main__':
    feed_key = scrape_feed_key()
    gtf_dates = retrieve_gtfs_dates(feed_key)
    retrieve_corresponding_cot(gtf_dates)

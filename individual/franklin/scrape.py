import requests
import pandas as pd 
from datetime import datetime
from zipfile import ZipFile
import os
from io import StringIO

def scrape_feed_key():
    

def retrieve_gtfs_dates():
   
    gtfs = 'http://opendata.toronto.ca/toronto.transit.commission/ttc-routes-and-schedules/OpenData_TTC_Schedules.zip'
    test = 'https://transit.land/api/v2/rest/api/v2/rest/feed_versions/{feed_version_key}'
    
    try:
        
        
        # file may be large
        response = requests.get(gtfs, stream=True)
        
        # Raise an error if bad status code
        response.raise_for_status() 
        file = "OpenData_TTC_Schedules.zip"
        location = "./individual/franklin/"
        path = location + file
        
        with open(path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        # opening the zip file in READ mode 
        with ZipFile(path, 'r') as zip: 
            # printing all the contents of the zip file 
            zip.printdir() 
        
            # TODO: GTFS is like months ahead of the COT data
            # Extract only calendar.txt file
            zip.extract('calendar.txt', path = location)
    
            # type bytes
            calendar = zip.read('calendar.txt')
            
            # Decode the bytes and convert into a df
            data_str = calendar.decode('utf-8')
            df = pd.read_csv(StringIO(data_str))
            
            # The format we are receiving the date data
            date_format = '%Y%m%d'
            
            start_date = datetime.strptime(str(df['start_date'][0]), date_format)
            end_date = datetime.strptime(str(df['end_date'][0]), date_format)
            
        
        # Remove the files we downloaded
        os.remove(path)    
        os.remove(location + 'calendar.txt')
        return [start_date, end_date]
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        os.remove(path)
        

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
    
    df2 = df.loc[df["Date"].between(dates[0].date(), dates[1].date())]
    print("After selecting the rows between the two dates:\n", df2)
    
    os.remove(path)
    
    # september_dates = df[df['Date'].dt.month == 9]
    # print(september_dates)

    # os.remove("test.xlsx")
    # filtered_df = read_file.query('')



    # read_file.to_csv ("Test.csv",  index = None, header=True) 

    # Convert to a pandas df
    # df = pd.DataFrame(pd.read_csv("Test.csv")) 

    # print(df)

retrieve_corresponding_cot(retrieve_gtfs_dates())

# import requests

# # Toronto Open Data is stored in a CKAN instance. It's APIs are documented here:
# # https://docs.ckan.org/en/latest/api/

# # To hit our API, you'll be making requests to:
# base_url = "https://ckan0.cf.opendata.inter.prod-toronto.ca"

# # Datasets are called "packages". Each package can contain many "resources"
# # To retrieve the metadata for this package and its resources, use the package name in this page's URL:
# url = base_url + "/api/3/action/package_show"
# params = { "id": "ttc-bus-delay-data"}
# package = requests.get(url, params = params).json()
# print(package)

# # To get resource data:
# for idx, resource in enumerate(package["result"]["resources"]):

#        # To get metadata for non datastore_active resources:
#        if not resource["datastore_active"]:
#            url = base_url + "/api/3/action/resource_show?id=" + resource["id"]
#            resource_metadata = requests.get(url).json()
#            print(resource_metadata)
#            # From here, you can use the "url" attribute to download this file




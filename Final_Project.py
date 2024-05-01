#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 27 15:00:20 2024

@author: jing
"""

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

from bs4 import BeautifulSoup
import requests
from io import StringIO #see html-string as file

import pprint


#%%
#THIS PART IS CSV DATA

def read_clean_csv(filename = 'nasdaq_AZNCF.csv'):

    nasdaq_df = pd.read_csv(filename)
    
    nasdaq_df = nasdaq_df.iloc[14:219+1] #206*6
    nasdaq_df['Date'] = pd.to_datetime(nasdaq_df['Date'])
    nasdaq_df.set_index('Date', inplace=True)
    nasdaq_df['Close/Last'] = nasdaq_df['Close/Last'].str.replace('$', '').astype(float).round(1)
    nasdaq_df['Open'] = nasdaq_df['Open'].str.replace('$', '').astype(float).round(1)
    nasdaq_df['High'] = nasdaq_df['High'].str.replace('$', '').astype(float).round(2)
    nasdaq_df['Low'] = nasdaq_df['Low'].str.replace('$', '').astype(float).round(2)
    
    return nasdaq_df

def weekly_csv(input_data):
    weekly_data = input_data.resample('W').agg({
        'Volume': 'sum',  # Sum volume per week
        'Close/Last': ['mean'],  # Average closing price per week #['mean', 'median', np.std]
        'Open': ['mean'],  # Average closing price per week
        'High': 'max',   # Maximum high price per week
        'Low': 'min'     # Minimum low price per week
    })

    new_index = ['Week_' + str(n) for n in range(len(weekly_data))]
    weekly_data.index = new_index

    csv_weekly_data = weekly_data
    new_columnname = ['sum', 'close_mean', 'open_mean', 'max', 'min']
    csv_weekly_data.columns = [new_columnname]
    csv_weekly_data.columns = [col[0] for col in csv_weekly_data.columns]
    return csv_weekly_data

#%%
#THIS PART IS SCRAPE DATA 
#web scraping data website
#https://www.cdc.gov/flu/weekly/pastreports.htm
debug_print = False
def urls_in_singleyaer (single_year) -> list:
    """
    Collect weekly urls from target year, return a list of urls

    Parameters
    ----------
    single_year : TYPE
        target year.

    Returns
    -------
    list
        list of urls.

    """
    urls = []
    week_num = 1
    for single_week in single_year:
        if single_week == '\n':
            continue
        
        a_tag = single_week.find('a')
        this_week_url = a_tag['href'] if a_tag else 'No link found'
        
        if debug_print:
            #print(single_week)
            #print(type(single_week))
            print('---------')
            print('URL: ',this_week_url)
            #print(repr(single_week))
            print('###')
            print(f'This week might be week {week_num}')
            week_num += 1
        
        urls.append(this_week_url)
    return urls

def clinical_lab_data(soup, Week_num):
    print("----")
    specific_strong_tags = soup.find_all('strong', string='No. of specimens tested')

    # Assuming we want the first match and its parent table
    if specific_strong_tags:
        parent_table = specific_strong_tags[0].find_parent('table')
        if parent_table:
            #print(parent_table)
            
            parent_table = str(parent_table)
            df = pd.read_html(StringIO(parent_table))[0]

            # need dynamic colmun header
            df.columns = ['Metric', f'Week_{Week_num}' , f'Week_{Week_num} Cumulative']
            df.drop(index=df[df['Metric'].isnull()].index, inplace=True)  # Remove rows where 'Metric' is NaN
            
            # print('return clinical df')
        else:
            print('Table not found for the specified <strong> tag.')
    else:
        print('No <strong> tags with the specified text found.')
        
        
    return df

def public_lab_data(soup, Week_num):
    def normalize(text):
        return ' '.join(text.split()).strip()


    print("---")
    # Search for the element containing the specific formatted text
    found = None
    for strong_tag in soup.find_all('strong'):
        if "Subtyping not performed" in normalize(strong_tag.get_text()):
            found = strong_tag
            break
    
    if found:
        parent_table = found.find_parent('table')
        parent_table = str(parent_table)

        df = pd.read_html(StringIO(parent_table))[0]
        
        # need dynamic header
        df.columns = ['Metric', f'Week_{Week_num}' , f'Week_{Week_num} Cumulative']
        df.replace({r'^\s*$': None}, regex=True, inplace=True)  # Replace empty strings with None
        
        # print('return public df')
        
    else:
        print("No <strong> tags with the specified text found.")
        
    return df


def get_weekly_clinical_data(weekly_url, Week_num):
    """
    returns target data from each week

    Parameters
    ----------
    weekly_url : TYPE
        target week.

    Returns
    -------
    list
        target data from that week.

    """
    #8 data from Clinical Lab:
    #num of specimens tested, num of positive, influenza A, influenza B; Data accumulated since last year Oct 2
    #22 Data from Public Health Laboratory:
    #num of specimens tested, num of positive, influenza A, influenza B; Accumulated data
    #   Influenza A: H1N1, H3N2, H3N2v, subtyping not performed
    #   Influenza B: Yamagata Linage, Victoria Linage, Linage not performed
    
    r = requests.get(weekly_url)
    soup = BeautifulSoup(r.content, 'lxml')#lxml is the underlying parser
    
    clinic_week_df = clinical_lab_data(soup, Week_num)
    
    return clinic_week_df #this is actually both week and cumulative data
    pass

def get_weekly_public_data(weekly_url, Week_num):
    r = requests.get(weekly_url)
    soup = BeautifulSoup(r.content, 'lxml')#lxml is the underlying parser
    
    public_week_df = public_lab_data(soup, Week_num)
    
    return public_week_df #this is actually both week and cumulative data
    pass

def concat_week_df(clinical_df, public_df, temp_url):
    concat_df = pd.concat([clinical_df, public_df], axis=0)

    columns = concat_df.columns

    new_firstrow = pd.DataFrame([temp_url, None, None])
    new_firstrow = new_firstrow.T
    
    new_firstrow.columns = concat_df.columns

    week_df = pd.concat([new_firstrow, concat_df], axis = 0, ignore_index=True)
    print('-------')
    print('return week_df')
    return week_df

def concat_year_df(urls):
    year_df = pd.DataFrame()
    Week_num = 0

    for url in urls:
        print("------------------------------")
        print("------------------------------")
        print(f'Weeknum: {Week_num}')
        clinical_df = get_weekly_clinical_data(url, Week_num)
        public_df = get_weekly_public_data(url, Week_num) 
        Week_df = concat_week_df(clinical_df, public_df, url)
        
        #add to right side of df
        year_df = pd.concat([year_df, Week_df], axis = 1)
        Week_num +=1
        pass
    return year_df
############################################################################
# #this part gathers all information for a single week
# temp_url = 'https://www.cdc.gov/flu/weekly/weeklyarchives2022-2023/week39.htm'
# clinical_df = get_weekly_clinical_data(temp_url)

# public_df = get_weekly_public_data(temp_url) 

# week_df = concat_week_df(clinical_df, public_df, temp_url)
url = "https://www.cdc.gov/flu/weekly/pastreports.htm"
r = requests.get(url)
soup = BeautifulSoup(r.content, 'lxml')#lxml is the underlying parser
all_years_link = soup.find_all('ul', class_="mb-0 cc-md-2 lsp-out block-list") 
#print(all_years_link)

#line 1 is current weekly report
#in my scraping, a single_year stars with "weekly"
#then starts with week 39 of the year, counting down and then to week 52 of the prev year, 
#until week 40 of prev year
num = 1
skip_2024 = True #only get one year data atm
RESCRAPE_DATA = False

if RESCRAPE_DATA:
        
    for single_year in all_years_link:
        if skip_2024:
            skip_2024 = None
            continue
        
        
        print("---------------------")
        print(f'Year {num}:')
        #print(single_year)
        
        urls = urls_in_singleyaer(single_year)
        urls = urls[1:]
        #pprint.pprint(urls)
        print('Got the urls')
        
        num +=1
        break
    year_df = concat_year_df(urls)

def convert_to_float(s):
    # Remove commas
    s = s.replace(',', '')
    # Extract the number before the space
    s = s.split('(')[0]
    s = s.rstrip()
    return float(s)

def go_through_each_column_and_conver_to_float(df):
    for column in df.columns:
        if isinstance(df[column][0], str):
                df[column] = df[column].apply(convert_to_float)               
        else:
            pass
    return df

#%%
if RESCRAPE_DATA:
    #DATA CLEANING PART
    metric = year_df['Metric'].iloc[:, 0] #0,3,8 is empty
    
    #clean data
    columns_to_drop = [col for col in year_df.columns if 'Metric' in col]
    
    year_df_clean = year_df.drop(columns=columns_to_drop)
    
    columns_cumulative = [col for col in year_df.columns if 'Cumulative' in col]
    year_df_cumulative = year_df[columns_cumulative]
    #reverse
    year_df_cumulative_transposed = year_df_cumulative.T
    # Reversing the values in each column while keeping the index
    for column in year_df_cumulative_transposed:
        year_df_cumulative_transposed[column] = year_df_cumulative_transposed[column].iloc[::-1].values
    #print(year_df_cumulative_transposed)
    
    columns_in_b = year_df_cumulative.columns
    #preserving order
    filtered_columns = [col for col in year_df_clean.columns if col not in columns_in_b]
    # Index the DataFrame using the filtered list of columns
    year_df_singleweek = year_df_clean[filtered_columns]
    
    #reverse
    year_df_singleweek_transposed = year_df_singleweek.T
    # Reversing the values in each column while keeping the index
    for column in year_df_singleweek_transposed:
        year_df_singleweek_transposed[column] = year_df_singleweek_transposed[column].iloc[::-1].values
    
    year_df_cumulative_transposed.to_csv('cumulative.csv', index=False)
    year_df_singleweek_transposed.to_csv('singleweek.csv', index=False)
    metric.to_csv('year_metric.csv', index=False)
    pass
#%%
#THIS PART IS API
api_key = '0cd8f3adb3ed73bfb7bd643d94419d3d'
lat = '34.0536'
lon = '-118.2427'
start = '1685257200'
weeks = 43
cnt = 24*7 #169 is the max, 7 day is 168
REREQUEST_DATA = False
url = f'https://history.openweathermap.org/data/2.5/history/city?lat={lat}&lon={lon}&type=hour&start={start}&cnt={cnt}&appid={api_key}'

response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    print('Got the DATA!')
    print(len(data['list']))
else:
    print("Failed to retrieve data", response.status_code)
#################################################
def get_data_list(data):
    data_list = data['list']
    return data_list

def get_datapoint(data_list, num = 0):
    print(num)
    main_dict = data_list[num]['main'] #also have cloud, weather, wind. May be of use.
    return main_dict

def dict_to_df(main_dict):
    df = pd.DataFrame(list(main_dict.items()), columns=['Label', 'Value'])
    print(df)
    return df

def df_to_betterdf(df):
    labels = df.iloc[:,0]
    new_df = pd.DataFrame(columns = labels)
    df = df.iloc[:, 1:].T
    df.columns = new_df.columns
    new_df = pd.concat([new_df, df])
    new_df.reset_index(drop=True, inplace=True)
    
    return new_df

def build_df():
    pass

#%%
if REREQUEST_DATA:
    api_weekly_data = pd.DataFrame(columns=['temp', 'feels_like', 'pressure', 'humidity', 'temp_min', 'temp_max'])
    start = '1685257200'
    epoch_secs = 604800
    weeks = 43
    cnt = 24*7
    current_UTX = 0
    
    weeks = 43
    
    for week_num in range(weeks):
        current_UTX = int(start) + week_num * epoch_secs
        current_week_df = pd.DataFrame(columns=['temp', 'feels_like', 'pressure', 'humidity', 'temp_min', 'temp_max'])
        #index = 'Week_' + str(week_num)
        
        url = f'https://history.openweathermap.org/data/2.5/history/city?lat={lat}&lon={lon}&type=hour&start={current_UTX}&cnt={cnt}&appid={api_key}'
        
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print('Got the DATA!')
            print(len(data['list']))
            pass
        else:
            print("Failed to retrieve data", response.status_code)
            pass
        
        
        data_list = get_data_list(data)
        result = pd.DataFrame()
    
        for num in range(int(cnt)):
            main_dict = get_datapoint(data_list, num)
            df = dict_to_df(main_dict)
            if num == 0:
                result = pd.concat([result, df], axis = 1)
                print(result)
                pass
            
            else:
                result = pd.concat([result, df['Value']], axis = 1)
                pass
            
            pass
        API_df = df_to_betterdf(result)
        mean_df = API_df.mean()
        api_weekly_data = pd.concat([api_weekly_data, pd.DataFrame([mean_df])], ignore_index = True)
        pass
    new_index = ['Week_' + str(n) for n in range(len(api_weekly_data))]
    api_weekly_data.index = new_index
    
    api_weekly_data.to_csv('API.csv')
    pass
#%%
api_weekly_data = pd.read_csv('API.csv') #43
nasdaq_df = read_clean_csv('nasdaq_AZNCF.csv')
csv_weekly_data = weekly_csv(nasdaq_df) #43
metric = pd.read_csv('year_metric.csv')
clinical_columnname = [' ', 'Specimens tested', 'Positive specimens',
                  ' ', 'Influ. A', 'Influ. B']
public_lab_columnname = ['Specimens tested', 'Positive specimens',
                         ' ', 'Influ. A', 'H1N1', 'H3N2', 'H3N2v',
                         'Subtype Null', 'Influ. B', 'Yamagata', 'Victoria', 'Lineage Null']
year_df_cumulative_transposed = pd.read_csv('cumulative.csv') #52
cumulative_df = go_through_each_column_and_conver_to_float(year_df_cumulative_transposed)

year_df_singleweek_transposed = pd.read_csv('singleweek.csv')
singleweek_df = go_through_each_column_and_conver_to_float(year_df_singleweek_transposed)
#singleweek_df.columns = metric




#%%

df = pd.DataFrame(csv_weekly_data)
# Line plot for me
df.plot()
plt.title('Line Plot')
plt.xlabel('Index')
plt.ylabel('Values')
plt.show()

# Create a plot using Matplotlib for streamlit
fig, ax = plt.subplots()
df.plot(ax=ax)  # Ensure df.plot() is attached to the Matplotlib Axes object
ax.set_title('Line Plot')
ax.set_xlabel('Index')
ax.set_ylabel('Values')

# all except sum
fig2, ax2 = plt.subplots()
ax2.plot(df['close_mean'], label='close_mean')
ax2.plot(df['open_mean'], label='open_mean', color='green')
ax2.plot(df['max'], label='max', color='red')
ax2.plot(df['min'], label='min', color='blue')
ax2.set_title('Mean Line Plot')
ax2.set_xlabel('Index')
ax2.set_ylabel('Mean Values')
ax2.legend()

##
# df = pd.DataFrame(year_df_cumulative_transposed[:])
# df = df[1]
# df = pd.to_numeric(df)
# fig3, ax3 = plt.subplots()
# df.plot(ax=ax)  # Ensure df.plot() is attached to the Matplotlib Axes object
# ax3.plot(df[:], label='CUMULATIVE')
# ax3.set_title('Line Plot')
# ax3.set_xlabel('Index')
# ax3.set_ylabel('Values')

#%%
#streamlit format/connection
import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd


st.write("### WELCOME!!!")
st.write('<-- Please proceed to the main page on the left')
# st.dataframe(csv_weekly_data)
# # Display the plot in Streamlit
# st.write("## My Matplotlib Plot")
# st.pyplot(fig)
# st.write("## My Matplotlib Plot")
# st.pyplot(fig2)
# #st.write("## My Matplotlib Plot")
# #st.pyplot(fig3)
# st.write("## My Dataframe")
# data = year_df_singleweek_transposed
# st.dataframe(data= data)
# st.write("## My Dataframe")
# data = api_weekly_data
# st.dataframe(data= data)
# st.sidebar.image("pic/cat4.gif")
    
    
    
    
    

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 15:47:13 2024

@author: jing
"""

import requests
import pprint
import pandas as pd

#%%
#1704096000
#1704182400
#2023/05/28 : 	1685257200
#cnt = 24*7*43
#1 Week: 604,800 seconds.

api_key = '0cd8f3adb3ed73bfb7bd643d94419d3d'

#https://history.openweathermap.org/data/2.5/history/city?
#lat={lat}&lon={lon}&type=hour&start={start}&cnt={cnt}&appid={API key}

lat = '34.0536'
lon = '-118.2427'
#start = '1704096000' #jan 1 2024, at most i can go up to a year. This may need to be dynamic.
#cnt = 24*5 #every 24 is a day
start = '1685257200'
# cnt = 24*7*43 #7224
weeks = 43
cnt = 24*7 #169 is the max, 7 day is 168


url = f'https://history.openweathermap.org/data/2.5/history/city?lat={lat}&lon={lon}&type=hour&start={start}&cnt={cnt}&appid={api_key}'

response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    print('Got the DATA!')
    print(len(data['list']))
else:
    print("Failed to retrieve data", response.status_code)
    

#%%
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


# #%%
# data_list = get_data_list(data)
# result = pd.DataFrame()

# for num in range(int(cnt)):
#     main_dict = get_datapoint(data_list, num)
#     df = dict_to_df(main_dict)
#     if num == 0:
#         result = pd.concat([result, df], axis = 1)
#         print(result)
#         pass
    
#     else:
#         result = pd.concat([result, df['Value']], axis = 1)
#         pass
    
#     pass


# API_df = df_to_betterdf(result)



#%%
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
#%%
#save to csv


#api_weekly_data = pd.read_csv('API.csv')
test = pd.read_csv('API.csv')

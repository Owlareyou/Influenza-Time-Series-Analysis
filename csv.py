#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 08:42:09 2024

@author: jing
"""

import pandas as pd
import numpy as np
import os

nasdaq_df = pd.read_csv('nasdaq_AZNCF.csv')

nasdaq_df.head()

nasdaq_df = nasdaq_df.iloc[14:219+1] #206*6
nasdaq_df['Date'] = pd.to_datetime(nasdaq_df['Date'])
nasdaq_df.set_index('Date', inplace=True)
nasdaq_df['Close/Last'] = nasdaq_df['Close/Last'].str.replace('$', '').astype(float).round(1)
nasdaq_df['Open'] = nasdaq_df['Open'].str.replace('$', '').astype(float).round(1)
nasdaq_df['High'] = nasdaq_df['High'].str.replace('$', '').astype(float).round(2)
nasdaq_df['Low'] = nasdaq_df['Low'].str.replace('$', '').astype(float).round(2)



#%%
#2023 5/28 weekend; 5/29 memorial; 5/30 index = 219
#2024 3/23 weekedn; 3/22 index = 14

weekly_data = nasdaq_df.resample('W').agg({
    'Volume': 'sum',  # Sum volume per week
    'Close/Last': ['mean'],  # Average closing price per week #['mean', 'median', np.std]
    'Open': ['mean'],  # Average closing price per week
    'High': 'max',   # Maximum high price per week
    'Low': 'min'     # Minimum low price per week
})

new_index = ['Week_' + str(n) for n in range(len(weekly_data))]
weekly_data.index = new_index

csv_weekly_data = weekly_data
print(csv_weekly_data)

#%%
experiment_df = pd.concat([api_weekly_data, csv_weekly_data], ignore_index= False, axis = 1)

csv_weekly_data.to_csv('nasdaq_csv.csv')
experiment_df.to_csv('API+nasdaq.csv')
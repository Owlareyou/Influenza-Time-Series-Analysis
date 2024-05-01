#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 15:35:03 2024

@author: jing
"""

import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
#%%
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
#1. split single week and accumulative
single_week_clinical_df = singleweek_df.iloc[:,0:6]
single_week_public_df = singleweek_df.iloc[:,6:]
#2. give column name
single_week_clinical_df.columns = clinical_columnname
single_week_public_df.columns = public_lab_columnname
#singleweek_df.columns = metric
#%%


tab1, tab2 = st.tabs(["Interactive Page", "Plots and Charts"])
with tab1:    

    st.sidebar.markdown('## Select Your Datasets')
    data_sets = st.sidebar.multiselect("Datasets", ['Weather', 'Nasdaq', 'CDC'], default=['Weather', 'Nasdaq', 'CDC'])
    st.sidebar.write("""_ps. the code will not work if you select features but not its corresponding dataset_ <br>
                     _pps. don't try it_""", unsafe_allow_html=True )

    
    filtered_list = [item for item in api_weekly_data.columns if item != 'Unnamed: 0']
    st.sidebar.write('-------------')
    st.sidebar.markdown('## Select Your Features')
    api_features = st.sidebar.multiselect('Weather Features:', filtered_list, default=['temp'])
    csv_features = st.sidebar.multiselect('Nasdaq Features:', csv_weekly_data.columns.unique(), default=['max', 'min'])
    filtered_list = [item for item in clinical_columnname if item != ' ']
    week_features = st.sidebar.multiselect('CDC Features:', filtered_list, default = ['Influ. B'])
    
    st.sidebar.write('-------------')
    st.sidebar.markdown('## Select Target Week')
    target_week = st.sidebar.slider("Weeks:", 0, 42, (42))
    # # Calculate Pearson correlation
    # correlation = single_week_clinical_df['Positive specimens'].corr(csv_weekly_data['open_mean'])
    # st.write("Correlation coefficient:", correlation)

    if st.sidebar.button("Submit"):
        if 'Weather' in data_sets:
            filtered_api = api_weekly_data[api_features]
            filtered_api = filtered_api[0:target_week]
        if 'Nasdaq' in data_sets:
            filtered_csv = csv_weekly_data[csv_features]
            filtered_csv = filtered_csv[0:target_week]
        if 'CDC' in data_sets:
            filtered_cdc = single_week_clinical_df[week_features]
            filtered_cdc = filtered_cdc[0:target_week]
            pass

        #plot
        fig, ax = plt.subplots()
        # Setting custom x-axis ticks and labels
        week_labels = [f"{i}" for i in range(0,target_week)]
        tick_positions = range(0, len(week_labels), 2)  # Start at 0, up to number_of_weeks, step by 2
        # Corresponding labels for every other week
        tick_labels = [week_labels[i] for i in tick_positions]
        # Set ticks at every other week
        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels)
        
        try:
            ax.plot(filtered_api, label=api_features, linestyle = '--')
            ax.plot(filtered_csv, label=csv_features, linestyle = ':')
            ax.plot(filtered_cdc, label= week_features, linestyle = '-')
            ax.set_title('Comparison Plot Between Selected Features')
            ax.set_xlabel('Week Number')
            ax.set_ylabel('')
            ax.grid(True)
            fig.set_size_inches(10, 6)
            ax.legend(loc = 'upper left')
            st.pyplot(fig)
        except:
            st.write('### YOU DID NOT SELECT THE CORRECT DATASET!!!')
            st.write("`I don't really know how to fix this so this is now a feature, not a bug`")
            st.image("./pic/cat2.gif")


        
    
    
    
with tab2:
    
    week_labels = [f"{i}" for i in range(42)]
    tick_positions = range(0, len(week_labels), 10)  # Start at 0, up to number_of_weeks, step by 2
    # Corresponding labels for every other week
    tick_labels = [week_labels[i] for i in tick_positions]

    #st.write("Nasdaq Data")
    df = pd.DataFrame(csv_weekly_data)
    # all except sum
    fig_csv, ax_csv = plt.subplots()
    ax_csv.plot(df['close_mean'], label='close_avg', color = '#1f77b4', linestyle='--')
    ax_csv.plot(df['open_mean'], label='open_avg', color='#ff7f0e', linestyle='--')
    ax_csv.plot(df['max'], label='max', color='#2ca02c', linewidth=2)
    ax_csv.plot(df['min'], label='min', color='#d62728', linewidth=2)
    ax_csv.set_title('Astrazeneca plc (AZNCF) Historical Quotes')
    ax_csv.set_xlabel('Week Number')
    ax_csv.set_ylabel('Dollars (USD)')
    
    ax_csv.grid(True)
    fig_csv.set_size_inches(10, 6)
    ax_csv.set_xticks(tick_positions)
    ax_csv.set_xticklabels(tick_labels)
    ax_csv.legend()
    
    #st.write('Weather DATA") #without pressure and humidity
    df = pd.DataFrame(api_weekly_data)
    # Create a plot using Matplotlib for streamlit
    fig_api, ax_api = plt.subplots()
    #df.plot(ax=ax_api)  # Ensure df.plot() is attached to the Matplotlib Axes object
    ax_api.plot(df['temp'], label = 'temp', color = '#ff7f0e', linewidth =2.5)
    ax_api.plot(df['feels_like'], label = 'feels_like', color='#2ca02c', linestyle='--')
    ax_api.plot(df['temp_min'], label = 'temp_min', color = '#1f77b4', linewidth =0.7)
    ax_api.plot(df['temp_max'], label = 'temp_max', color='#d62728', linewidth =0.7)
    #HUMIDITY!!!!!!! linestyle = 'densely dashdotted', color= '#808080'
    ax_api.set_title('Weekly Temperature Trends in Los Angeles')
    ax_api.set_xlabel('Week Number')
    ax_api.set_ylabel('Degrees (Fahrenheit) ')
    
    ax_api.grid(True)
    fig_api.set_size_inches(10, 6)
    ax_api.set_xticks(tick_positions)
    ax_api.set_xticklabels(tick_labels)
    
    ax2 = ax_api.twinx()  # Create a second y-axis
    ax2.set_ylabel('Humidity (g.kg-1)')
    ax2.plot(df['humidity'], label = 'Humidity', color= '#808080', linestyle = ':', alpha = 0.5)
    ax2.set_xticks(tick_positions)
    ax2.set_xticklabels(tick_labels)
    ax2.legend()
    ax_api.legend()

    # ##
    # clinical_columnname = [' ', 'Specimens tested', 'Positive specimens',
    #                   ' ', 'Influ. A', 'Influ. B']
    df = pd.DataFrame(singleweek_df[:])
    # df = df[1]
    # df = pd.to_numeric(df)
    fig_week, ax_week = plt.subplots()
    #df.plot(ax=ax)  # Ensure df.plot() is attached to the Matplotlib Axes object
    #ax_week.plot(df[:], label=clinical_columnname+public_lab_columnname)
    ax_week.plot(df.iloc[:,1] /1000, label='Specimens tested', color = '#1f77b4', linewidth = 2)
    ax_week.plot(df.iloc[:,2] /1000, label='Positive specimens', color='#d62728', linewidth = 1.2)
    # ax_week.plot(df.iloc[:,4], label='Influ. A')
    # ax_week.plot(df.iloc[:,5], label='Influ. B')
    ax_week.set_title('Weekly CDC Influenza Surveillance Overview')
    ax_week.set_xlabel('Week Number')
    ax_week.set_ylabel("Specimen Count (thousands)")
    
    ax_week.grid(True)
    fig_week.set_size_inches(10, 6)
    ax_week.set_xticks(tick_positions)
    ax_week.set_xticklabels(tick_labels)
    
    
    ax_week2 = ax_week.twinx()  # Create a second y-axis
    max_y2 = max(df.iloc[:,4]/100)
    new_upper_limit = max_y2 * 2  # Makes the max value appear halfway
    ax_week2.set_ylim(0, new_upper_limit)
    ax_week2.set_ylabel('Specimen Count (hundreds)')
    ax_week2.plot(df.iloc[:,4] /100, label='Influenza A', alpha = 0.7, linestyle = (0, (5, 1)))
    ax_week2.plot(df.iloc[:,5] /100, label='Influenza B', alpha = 0.7, linestyle = (0, (5, 1)))
    ax_week2.set_xticks(tick_positions)
    ax_week2.set_xticklabels(tick_labels)

    ax_week.legend()
    ax_week2.legend(loc = 'lower right')
    
    
    ##
    df = pd.DataFrame(cumulative_df[:])
    # df = df[1]
    # df = pd.to_numeric(df)
    fig_cumu, ax_cumu = plt.subplots()
    #df.plot(ax=ax)  # Ensure df.plot() is attached to the Matplotlib Axes object
    #ax_week.plot(df[:], label=clinical_columnname+public_lab_columnname)
    ax_cumu.plot(df.iloc[:,1] /1000, label='Specimens tested', color = '#1f77b4', linewidth = 2)
    ax_cumu.plot(df.iloc[:,2] /1000, label='Positive specimens', color='#d62728', linewidth = 1.2)
    # ax_week.plot(df.iloc[:,4], label='Influ. A')
    # ax_week.plot(df.iloc[:,5], label='Influ. B')
    ax_cumu.set_title('Cumulative CDC Influenza Surveillance Overview')
    ax_cumu.set_xlabel('Week Number')
    ax_cumu.set_ylabel("Specimen Count (thousands)")
    
    ax_cumu.grid(True)
    fig_cumu.set_size_inches(10, 6)
    ax_cumu.set_xticks(tick_positions)
    ax_cumu.set_xticklabels(tick_labels)
    
    
    ax_cumu2 = ax_cumu.twinx()  # Create a second y-axis
    max_y2 = max(df.iloc[:,4]/100)
    new_upper_limit = max_y2 * 2  # Makes the max value appear halfway
    ax_cumu2.set_ylim(0, new_upper_limit)
    ax_cumu2.set_ylabel('Specimen Count (hundreds)')
    ax_cumu2.plot(df.iloc[:,4] /100, label='Influenza A', alpha = 0.7, linestyle = (0, (5, 1)))
    ax_cumu2.plot(df.iloc[:,5] /100, label='Influenza B', alpha = 0.7, linestyle = (0, (5, 1)))
    ax_cumu2.set_xticks(tick_positions)
    ax_cumu2.set_xticklabels(tick_labels)

    ax_cumu.legend()
    ax_cumu2.legend(loc = 'lower right')
    #%%
    #streamlit format/connection
    # st.dataframe(csv_weekly_data)
    # Display the plot in Streamlit
    # st.write("## My Matplotlib Plot") #this one has SUM, don't run it
    # st.pyplot(fig)

    st.write("## Plot (1): Nasdaq Data")
    st.pyplot(fig_csv)
    
    st.write("## Plot (2): Weather Data")
    st.pyplot(fig_api)
    
    st.write("## Plot (3): CDC Weekly Data")
    st.pyplot(fig_week)
    
    st.write("## Plot (4): CDC Cumulative Data")
    st.pyplot(fig_cumu)
    

    # st.write("## My Dataframe")
    # data = year_df_singleweek_transposed
    # st.dataframe(data= data)
    # st.write("## My Dataframe")
    # data = api_weekly_data
    # st.dataframe(data= data)
    # st.sidebar.image("pic/cat4.gif")
    st.markdown("""
                - **Plots/Charts**: <br>
                The visual aids are under the "Plots and Charts" tab of the "Data Exploration page"
                    - _Plot (1): Nasdaq Data_ <br>
                    This visualization presents the weekly CSV data obtained from the 
                    Nasdaq stock market for AstraZeneca plc (AZNCF). In alignment with our 
                    project's goal to analyze weekly data from Influenza reports, the dataset 
                    includes calculated weekly averages. Specifically, it comprises four key parameters: 
                        1. Average Opening Price, 2. Average Closing Price, 3. Maximum Dollar per Share, and 4. Minimum Dollar per Share.
                    - _Plot (2): Weather Data_ <br>
                    This visualization displays weather data for Los Angeles, sourced from the OpenWeatherMap 
                    API. The API provides hourly updates, which we have compiled into weekly averages to better 
                    assess temporal variations in weather conditions. The data includes several key parameters: 
                        1. Temperature, 2. Feels-like Temperature, 3. Maximum Temperature, 4. Minimum Temperature, 5. Humidity, and 6. Pressure.
                    - _Plot (3): CDC Data (Single Week)(Clinical Lab Data)_ <br>
                    This visualization presents the Clinical Lab Data from the CDC's influenza report, specifically focusing on single-week statistics. The dataset includes four key parameters: 1. Total Specimens, 2. Positive Specimens, 3. Influenza A Counts, and 4. Influenza B Counts.
                    
                    - _Plot (4): CDC Data (Cumulative)(Clinical Lab Data)_ <br>
                    This visualization presents the Clinical Lab Data from the CDC's influenza report, specifically focusing on cumulative statistics. The dataset includes four key parameters: 1. Total Specimens, 2. Positive Specimens, 3. Influenza A Counts, and 4. Influenza B Counts.
                    >
                    """, unsafe_allow_html=True)
        
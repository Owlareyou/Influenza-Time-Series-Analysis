#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 12:52:24 2024

@author: jing
"""



import streamlit as st


tab1, tab2 = st.tabs(["Main Page", "Dataset Description"])
with tab1:    
    st.markdown("""
                ## Name: Ching (Jing) Chuang
                ## How to Use This Webapp
                - **Interactivity**: <br>
                    - There are four pages in this web app:
                        - **The Welcome page** : Under the hood, this page is where all the API calling and scraping code is located.
                        I dedicated a specific page for them is because there seems to be a minor lag when I refreshes this page
                        in perticular. So leaving these heavy code on the side by making it into a welcome page is my way of enhancing user 
                        experience when exploring other pages.
                        - **The Main page** :
                            This page is for all the important informations, my name, project conclusion ..etc. On the second tab 
                            of this page is also a designated area about my data sources and some brief explaination about them.
                        - **Project Analysis page** : 
                            A seperate page to answer some reflection problems for our final project.
                        - **Data Exploration page** :
                            The page where users can select parameters from three distinct datasets
                            through an interactive sidebar. The webpage then dynamically generates a plot, visualizing 
                            potential correlations between the selected data points. <br>
                            On the second tab of this page, different plots are displayed to visualize each 
                            dataset separately. This provides visual aid and enhances user understanding of the data sets involved in the project.
                        
                    >
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
                - **Conclusions**: <br>
                The analysis of the correlation among three distinct datasets—CDC influenza reports, 
                weather data, and stock market data of AstraZeneca, an influenza vaccine manufacturer revealed little to no 
                significant correlation. Despite the intuitive anticipation that external factors such as weather 
                conditions and economic performance might influence or reflect trends in influenza data, the findings 
                suggest that these variables operate independently with respect to weekly tested and positive influenza 
                specimens.
                
                ## Major Gotchas
                - **Issue 1**: With limitation on our weather API, despite having data points that goes as far back as 
                ten years ago from CDC reports 
                and the stock market, the scope of the project is limited to within the year (52 weeks). 
                - **Issue 2**: One of the major challenges encountered during this project was managing the complexity 
                of the CDC data. Each week's influenza report includes both single-week statistics and cumulative 
                statistics for the year, further divided into data from clinical and public labs with various types 
                of specimen testing. The diversity of data types made it difficult to integrate all this information 
                into the project coherently. In the future, this problem could be mitigated by more thorough 
                planning and implementing a more refined data scraping approach to ensure cleaner and more structured 
                data integration.
                """, unsafe_allow_html=True)
                
    #st.image("./pic/cat2.gif")
    
with tab2:
    
    st.markdown("""
    # Data Sources Overview
    
    ## DATA SOURCE 1
    **URL for webscraping**: [CDC Weekly Influenza Reports](https://www.cdc.gov/flu/weekly/pastreports.htm)
    
    **Brief Description of Data/API**:
    This is the Centers For Disease Control and Prevention webpage that contains weekly Influenza reports from the past decades.
    Through this URL, I can go through the weeks one by one and obtain information regarding the number of specimens tested, what percentage are positive, and number of positive specimens by type.
    
    ## DATA SOURCE 2
    **URL for API**: [OpenWeatherMap](https://openweathermap.org/)  
    **Link to API Docs**: [API Documentation](https://openweathermap.org/history)
    
    **Brief Description of Data/API**:
    This website provides hourly historical weather data based on longitude and latitude. This helps me pinpoint weather data of Los Angeles County for future analysis.
    With a student's account, we can make History API calls for free. This will provide information regarding the temperature, feels_like temp, humidity, temp_min, temp_max from the past year.
    Additional information such as clouds, wind, and rain are also possible indicators that we can use.
    
    
    ## DATA SOURCE 3
    **URL for CSV Download**: [Nasdaq Market Activity for AstraZeneca](https://www.nasdaq.com/market-activity/stocks/azncf/historical)
    
    **Brief Description of Data/API**:
    This is the Nasdaq market activity for the Influenza vaccine manufacturer "AstraZeneca".
    With daily/weekly market reports, it contains information about how much was traded, opening value, closing value, highs, and lows.
    This CSV file contains data that goes as far back as 5 years ago.
    """, unsafe_allow_html=True)
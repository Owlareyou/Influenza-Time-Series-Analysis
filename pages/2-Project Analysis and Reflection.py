#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 13:13:39 2024

@author: jing
"""

import streamlit as st
import time

# # Set default values for session state if not already present
# if 'time_started' not in st.session_state:
#     st.session_state['key'] = 'value'

# st.session_state.setdefault('time_started', time.time())
# st.session_state.setdefault('display_gif', True)

# # Calculate elapsed time
# elapsed_time = time.time() - st.session_state['time_started']

# # Display GIF in sidebar if less than 10 seconds have elapsed
# if elapsed_time < 10:
#     st.sidebar.image("pic/cat4.gif")
# else:
#     # Once 10 seconds have passed, update display_gif to False
#     st.session_state['display_gif'] = False
#     # You could also remove the GIF here or display alternative content
#     st.sidebar.write("GIF display period has ended.")
#st.sidebar.image("pic/cat4.gif")

# Page Title
st.title('Project Analysis and Reflection')

# What did you set out to study?
st.markdown("""
### What did you set out to study?
The original plan for this project was simple. Does the amount of positive Influenza cases 
have any corelations with 1. the tempreture of the year and 2. the stock market performance
of Influenza vaccine manufactoring company. <br>
Using the weekly Influenza reports as a base line, we compare and contrast different 
features between all three datasets. To achive this comparison, the other two 
datasets must also be a time series data as well. <br>
The plan is to plot out a graph, with weeks bring out x axis and the amount being 
our y axis, it would be obviouse if there is a strong corelation between those features.
""", unsafe_allow_html=True)

# What did you discover/what were your conclusions?
st.markdown("""
### What did you Discover/what were your conclusions
The first hypothesis was if the weather gets cold, the amount of Influenza cases might rises as well
due to bad weather. The second hypothesis was if there is a rise of Influenza cases, a rising demand 
for Influenza vaccine might causes a rise of stock market evaluation for vaccine manufacturing 
company. <br>
Unfortunatly, after graphing our features together, it does not look there are any direct corelations 
between the datasets. Although this is a very crude conclusion base solely on the final graph alone. 
There are analytical methods for time series data that should be applied in the future.


""", unsafe_allow_html=True)

# What difficulties did you have in completing the project?
st.markdown("""
### What difficulties did you have in completing the project?
1. The API in OpenWeather website only supplies free data to as far back as one year prior. This is a major bottleneck
since it would meant in order to match all three datasets together, there will be lost of data to compensate for this API's
limitation.

2. Another problem with the API is that it requires a specific city as input. This is a problem since 
we will be comparing a city's weather report to a nation wide Influenza report. This is a lack of planning on 
my problem statement. Conceptually it does not make sense to compare a city's local weather and expect it to have
a huge corelation with a nations's clinical record.

3. When dealing with the data from Nasdaq exchange and Weather API, it became apparent that using a weekly report
as a baseline is also a bit problematic. The weather API provides a detailed hourly update, which means 
in order to make a comparison with CDC's data, I would have to average 7*24 points of data to provide a
consistent comparing unit. The same goes for Nasdaq exchange, when averaging stock exchange data points, I am sacraficing 
4 different sets of data points in order fit our weekly frequency. This is limits the resolution of our analysis drastically.

4. Scraping data from CDC's website is also a difficult task. Within the weekly report, there are single week statistics and 
cumulative statistics of each types of Influenza cases; furthermore, tests that was taken in clinical lab are kept seperate 
with public labs. The amount of complexity and cleaning this data needs is more then I expected. 

5. Since my original plan was to make a comparison on a single plot, I had faced another obsticle. There are too many features
each with drastically unit of measurments. It had became difficult to plot all the information onto a single chart.
Even with an addition of the second y axis, the output is often all over the place and confusing at the same time.

""", unsafe_allow_html=True)

# What skills did you wish you had while you were doing the project?
st.markdown("""
### What skills did you wish you had while you were doing the project?

- The data cleanign process and trying to match up all the dimension is what took the most effor. I belive 
the difficulty is mainly due to my unfamilarity
with working with dataframes. This includes the data manipulation process, as well as the data visualization process. I wish I
had more knoweldge on how to build a coherent visual plot that can help users understand the data in a neat and quick way.
""", unsafe_allow_html=True)

# What would you do “next” to expand or augment the project?
st.markdown("""
### What would you do “next” to expand or augment the project?
- A simple next step could be calculate the pearson coefficient value between the parameters, this is a much more
analitcal way to show corelations between features.
- Figure out a sophisticated way to intigrate all of the datas from CDC's influenza report is also a valuable next step. 
As of now, the interactive interface of the webpage only allows 1/4 of the original data set to be accessed.
- A few methods could be applied to do further analysis on my data. Normalizing the datas could remedy the 
problems about different units among different features.
""", unsafe_allow_html=True)
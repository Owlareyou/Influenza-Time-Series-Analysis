#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  6 17:11:04 2024

@author: jing
"""


from bs4 import BeautifulSoup
import requests
import pprint
import pandas as pd
import matplotlib.pyplot as plt

from io import StringIO #see html-string as file
#%%
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

# #%%
# #this part gathers all information for a single week
# temp_url = 'https://www.cdc.gov/flu/weekly/weeklyarchives2022-2023/week39.htm'
# clinical_df = get_weekly_clinical_data(temp_url)

# public_df = get_weekly_public_data(temp_url) 

# week_df = concat_week_df(clinical_df, public_df, temp_url)

#%%
#web scraping data website
#https://www.cdc.gov/flu/weekly/pastreports.htm

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
#%%
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





#%%
df = pd.DataFrame(year_df_singleweek_transposed[:])
#df = pd.to_numeric(df, errors='coerce')
print(type(df[1]))
print(df[1])
df = df[1]
df = pd.to_numeric(df)
# Line plot for me
df.plot()

plt.title('Line Plotssss')
plt.xlabel('Index')
plt.ylabel('Values')
plt.show()



#%%
#my project's timeline end at 2024, March 23- Week 12 (3/17~3/23)
#starts from 2023, June 3 - Week 22 (5/28~6/3)
#total of 31+12 = 43 weeks

#%%
#save as csv
year_df.to_csv('scrape_CDC.csv', index=False)














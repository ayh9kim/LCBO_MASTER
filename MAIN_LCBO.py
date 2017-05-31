# -*- coding: utf-8 -*-
"""
Created on Mon May 22 18:45:06 2017

@author: ayh9k
"""

import pandas as pd
import numpy as np
import datetime
from plotly.offline import download_plotlyjs, init_notebook_mode, iplot # pip install plotly on Anaconda Prompt
from plotly.graph_objs import *
init_notebook_mode()

alc_one_shot = 45 * .4
dataFileLoc = 'products.csv'
df = pd.read_csv(dataFileLoc)

### Proprocess
# Only include current, non-seasonal products, inventory >0
df_current = df[df['is_dead'] == 'f']
df_current = df_current[df_current['is_discontinued'] == 'f']
df_current = df_current[df_current['inventory_count'] != 0]
df_current = df_current.loc[df_current['primary_category'].isin(['Wine', 'Spirits', 'Ready-to-Drink/Coolers', 'Beer', 'Ciders'])] 

# Select attributes
lstCol = ['id', 'name', 'regular_price_in_cents', 'stock_type', 'primary_category', 'secondary_category', 
          'tertiary_category', 'alcohol_content', 'volume_in_milliliters', 'sugar_in_grams_per_liter', 'released_on',
          'is_vqa', 'is_kosher', 'origin', 'is_seasonal', 'inventory_count']

lstColNam = {'id': 'id', 'name': 'Name', 'regular_price_in_cents': 'Regular Price (CAD $)', 'stock_type': 'Stock Type',
             'primary_category': 'Primary Category', 'secondary_category': 'Secondary Category', 'tertiary_category': 'Tertiary Category',
             'alcohol_content': 'Alcohol Content (mL)', 'inventory_count': 'Inventory Count',
             'is_vqa': 'is_vqa', 'is_kosher': 'is_kosher', 'origin': 'origin', 'is_seasonal': 'is_seasonal',
             'volume_in_milliliters': 'Volume (mL)', 'sugar_in_grams_per_liter': 'Sugar (g/L)', 'released_on': 'Release Date'}

df_main = df_current[lstCol]
df_main = df_main.rename(index=str, columns=lstColNam)

# Create & change attributes
df_main['Regular Price (CAD $)'] = df_main['Regular Price (CAD $)']/100
df_main['Alcohol Content (mL)'] = df_main['Alcohol Content (mL)']*df_main['Volume (mL)']/10000
df_main['Release Date'] = pd.to_datetime(df_main['Release Date'])
        
df_main['Price-to-Alcohol'] = df_main['Regular Price (CAD $)']/df_main['Alcohol Content (mL)']
df_main['Alcohol-to-Sugar'] = df_main['Alcohol Content (mL)']/df_main['Sugar (g/L)']/1000*100
   
# Released recently
start_date = datetime.datetime(2017, 1, 1)
df_recent = df_main[df_main['Release Date'].notnull()]
df_recent = df_main[df_main['Release Date'] >= start_date]

# Only a few stocks available
df_main['Price-per-10-shots'] = (df_main['Regular Price (CAD $)']/df_main['Alcohol Content (mL)'])*alc_one_shot*10
df_main=df_main.sort(['Price-per-10-shots'])

# Kosher drinks

# Sake
sake_name = 'Sake/Rice Wine'
df_sake = df_main[df_main['Tertiary Category'] == sake_name]

# Beer
df_beer = df_main[df_main['Primary Category'] == 'Beer']
df_beer = df_beer[df_beer['Secondary Category'] != 'Specialty']

# Seasonal drinks
df_seasonal = df_main[df_main['is_seasonal'] == 't']


### Analysis

## Comparison

# Distribution
trace1 = Histogram(x=df_beer['Price-per-10-shots'], opacity=0.75)
trace2 = Histogram(x=df_sake['Price-per-10-shots'], opacity=0.75)

data = [trace1, trace2]
layout = Layout(barmode='overlay')

fig = dict(data=data, layout=layout)

plotly.offline.plot(fig, filename='Beer vs. Sake')

# Primary Category



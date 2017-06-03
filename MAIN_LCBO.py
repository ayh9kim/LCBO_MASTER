"""
Created on Mon May 22 18:45:06 2017
@author: ayh9k
"""

import pandas as pd
import numpy as np
import datetime
import plotly
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
df_main['Alcohol%'] = df_main['Alcohol Content (mL)']/df_main['Volume (mL)']
df_main['Country'] = pd.DataFrame(pd.Series(df_main['origin']).str.split(',').str[0])
df_main['Region'] =  pd.DataFrame(pd.Series(df_main['origin']).str.split(',').str[1])     
   
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
# Gin
df_gin = df_main[df_main['Secondary Category'] == 'Gin']
# Tequila
df_tequila = df_main[df_main['Secondary Category'] == 'Tequila']
# Champagne
df_champagne = df_main[(df_main['Secondary Category'] == 'Champagne' )| (df_main['Secondary Category'] == 'Sparkling Wine' )]
df_seasonal = df_main[df_main['is_seasonal'] == 't']


### Analysis

## Comparison

# Distribution. Manny - Makes more sense to use prob. density?
trace1 = Histogram(x=df_beer['Price-per-10-shots'],histnorm='probability density', opacity=0.75,name='Beer')
trace2 = Histogram(x=df_sake['Price-per-10-shots'],histnorm='probability density', opacity=0.75,name='Sake')
trace3 = Histogram(x=df_gin['Price-per-10-shots'],histnorm='probability density', opacity=0.75,name='Gin')
trace4 = Histogram(x=df_tequila['Price-per-10-shots'],histnorm='probability density', opacity=0.75,name='Tequila')
data = [trace1, trace2, trace3, trace4]
layout = Layout(barmode='overlay',
                title='Cost of Alcohol Converting to 10 Vodka Shots Equivalent',
                xaxis=dict(
                title='Price per 10 shots (in CAD$)',
                titlefont=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                    )
                ),
            yaxis=dict(
                title='Frequency',
                titlefont=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                    )
                )
            )    

fig = dict(data=data, layout=layout)

plotly.offline.plot(fig, filename='Beer vs. Sake')

'''Here we want to create a World Map that has number of distinct alcohol count that's in LCBO'''
''' I dont like the colour scheme of the map, please change - Manny'''
#Load country code for Geo Map
CountryCodeLoc = 'CountryCode.csv'
df_CountryCode = pd.read_csv(CountryCodeLoc)
#Save the country code to a dictionary
CountryCode_dict = {}
for i in range(len(df_CountryCode)):
    CountryCode_dict[df_CountryCode['COUNTRY'][i]] = df_CountryCode['CODE'][i]
#Map each LCBO Country to a country code, and count no. of alcohol produce from the country
df_Country = pd.DataFrame(data=(df_main['Country'].unique()), columns = ['Country'])
df_Country['AreaCode'] = ""
df_Country['AlcoholCount'] = ""
for i in range(len(df_Country)):
    
    if df_Country['Country'][i] in CountryCode_dict:
        df_Country['AreaCode'][i] = CountryCode_dict[df_Country['Country'][i]]
    elif df_Country['Country'][i] =='South Korea':
        df_Country['AreaCode'][i] = 'KOR'
    elif df_Country['Country'][i] =='Republic of Macedonia':
        df_Country['AreaCode'][i] = 'MKD'
    elif df_Country['Country'][i] =='Caribbean':    #Captain Morgan 
        df_Country['AreaCode'][i] = 'PRI'
    elif df_Country['Country'][i] =='USA':    #Captain Morgan 
        df_Country['AreaCode'][i] = 'USA'        
    else:
        print(df_Country['Country'][i]," has no area code!!!")   
        
    df_Country['AlcoholCount'][i] = (df_main['Country']==df_Country['Country'][i]).sum() #just summing up all the distinct alcohol from country[i]


data = [ dict(
        type = 'choropleth',
        locations = df_Country['AreaCode'],
        z = df_Country['AlcoholCount'],
        text = df_Country['Country'],
        #colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
        #    [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
        colorscale = 'Earth',
        autocolorscale = False,
        reversescale = True,
        marker = dict(
            line = dict (
                color = 'rgb(180,180,180)',
                width = 0.5
            ) ),
        colorbar = dict(
            autotick = False,
            tickprefix = '$',
            title = 'Number of Distinct Alcohol in LCBO'),
      ) ]

layout = dict(
    title = 'Number of Distinct Alcohol in LCBO',
    geo = dict(
        showframe = False,
        showcoastlines = False,
        projection = dict(
            type = 'Mercator'
        )
    )
)

fig = dict( data=data, layout=layout )
plotly.offline.plot( fig, validate=False, filename='d3-world-map' )




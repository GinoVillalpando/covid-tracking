#   Map that tracks the daily COVID-19 positive cases by each state in the USA
#   author: @Gino Villalpando GinoVillalpandoWork@gmail.com in collaboration with Kyla Bendt kylabendt@gmail.com

import folium
import pandas as pd
import os
import geopandas
import branca.colormap as cm
import schedule
import json
import numpy as np

from bs4 import BeautifulSoup
from datetime import date, timedelta

# creates a variable with yesterday's date
yesterday = date.today() - timedelta(days=1)
yesterday = yesterday.strftime('%Y%m%d')

def covid():
    states = os.path.join('us-states.json')
    geostate = geopandas.read_file(states, driver='GeoJSON')
    url = 'https://covidtracking.com/api/v1/states'
    covid_data = pd.read_csv(f'{url}/current.csv', index_col=None, na_values=['NA'],
sep=',',low_memory=False)
    daily_covid = pd.read_csv(f'{url}/daily.csv', index_col=None, na_values=['NA'],
sep=',',low_memory=False)

    # create new dataframe with just the rows with the date as yesterday
    yesterday_data = daily_covid[daily_covid.date == int(yesterday)]

    # set index for both dataframes
    geostates = geostate.set_index('id')
    covid_data_indexed = covid_data.set_index('state')
    yesterday_data_indexed = yesterday_data.set_index('state')

    # combine both state and covid data dataframes
    Yesterday_State_Data = pd.concat(
        [geostates, yesterday_data_indexed], axis=1, join='inner')
    Geo_State_Data = pd.concat(
        [geostates, covid_data_indexed], axis=1, join='inner')

    # quantiles that the colormap uses for color legend
    quantiles = [0, 0.8, 0.85, 0.90, 0.97, 1]
    bins = list(Geo_State_Data['positive'].quantile(quantiles))

    # create the colormap with given hex colors
    Legend_Colors = cm.LinearColormap(
        colors=['#A2EFFF', '#7C00FF'], vmin=0, vmax=1)

    # colormap returns 8 character values but only accepts 6 characters
    colors = [Legend_Colors(quantile)[0:-2] for quantile in quantiles]

    # change NY to a specific purple because it's so much worse than everywhere else
    colors = colors[0:-1] + ['#8d3f9c']

    # creates legend colormap
    colormap = cm.LinearColormap(colors=colors,
                                 vmin=Geo_State_Data.positive.min(),
                                 vmax=Geo_State_Data.positive.max(),
                                 caption="Positive COVID-19 Tests".upper())

    # Create a dictionary of colors because 'id' is the only property of the feature available when styling
    colordict = Geo_State_Data['positive'].apply(colormap)

    # variables for loops to evaluate
    Pop_result = []
    Total_result = []
    Increase_result_percent = []
    Death_result = []
    Increase_result = []

    Us_Population = 328239523

    # for loop that takes the value in positive test results and evaluates the percentage of total population in the USA
    for value in Geo_State_Data['positive'] / Us_Population:
        Pop_result.append("{0:.4f}".format(value * 100) + '%')

    Geo_State_Data["Percentile of USA"] = Pop_result

    # for loop that divides positive and total tests and evaluates the result to a percentage for all state values
    for value in Geo_State_Data['positive'] / Geo_State_Data['total']:
        Total_result.append("{0:.2f}".format(value * 100) + '%')

    Geo_State_Data['total percentage'] = Total_result

    # for loop that evaluates the percentage increase of positive tests from yesterday's positive results
    for value in (Geo_State_Data['positive'] - Yesterday_State_Data['positive']) / Yesterday_State_Data['positive']:
        Increase_result_percent.append("{0:.2f}".format(value * 100) + '%')

    Geo_State_Data['increase percent'] = Increase_result_percent

    # for loop that gets the increase number
    for value in (Geo_State_Data['positive'] - Yesterday_State_Data['positive']):
        Increase_result.append(value)

    Geo_State_Data['increase number'] = Increase_result

    # for loop that gets death rate percentage
    for value in Geo_State_Data['death'] / Geo_State_Data['positive'] * 100:
        Death_result.append("{0:.2f}".format(value) + '%')

    Geo_State_Data['death percent'] = Death_result
    
    Geo_State_Data['date'] = date.today().strftime('%m/%d/%Y')


    # create the map at given location with a current value for zoom using folium
    MyMap = folium.Map(location=[48, -102],
                       zoom_start=3,
                       min_zoom=2,
                       max_zoom=5,
                       max_lon=-41.949395,
                       max_bounds=True,
                       tiles='CartoDB dark_matter',
                       prefer_canvas=True)

    # map layer that shows the colors correlating to positive results
    Positive_Layer = folium.GeoJson(
        Geo_State_Data,
        name='Positive Tests',
        style_function=lambda feature: {
            'fillColor': colordict[feature['id']],
            'fillOpacity': 0.7,
            'color': 'black',
            'weight': 1,
        }
    ).add_to(MyMap)

    # map layer that will show tooltips based on the state you hover
    State_Layer = folium.GeoJson(
        Geo_State_Data,
        name='States',
        style_function=lambda feature: {
            'fillColor': 'white',
            'fillOpacity': 0.1,
            'color': 'black',
            'weight': 1,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['name', 'positive', 'increase number','total percentage',
                    'negative', 'total', 'death', 'death percent', 'date'],
            aliases=['<div class="item-div">'+item+'</div>' for item in ['State', 'Positive Tests', 'Postive Test Increase Today',
                                                                          'Positive of Total Tests %', 'Negative Tests', 'Total Tests', 'Deaths', 'Death Rate', 'Results As Of']],
            localize=True
        ),
        highlight_function=lambda feature: {
            'fillColor': 'white',
            'fillOpacity': 0.5,
            'color': 'white',
            'weight': 4,
        }
    ).add_to(MyMap)

    # folium.TileLayer(tiles='OpenStreetMap', name='OpenStreetMap', min_zoom=3, max_zoom=5).add_to(MyMap)

    # add legend to the map
    MyMap.add_child(colormap)

    # create the maps and insert into a html file
    MyMap.save('index.html')

    # creates and imports css and meta tags on html generation
    with open('index.html', 'r') as file:
        html = file.read()
        soup = BeautifulSoup(html, features="html.parser")
        script = soup.find('script')
        meta = soup.find('meta')
        meta_tag = soup.new_tag('meta')
        title = soup.new_tag('title')
        ico = soup.new_tag('link')
        css = soup.new_tag('link')
        title.string = "Darker COVID-19 Tracker"
        meta_tag['name'] = "description"
        meta_tag['content'] = "Coronavirus Tracker - COVID-19 Tracking"
        ico['rel'] = "icon"
        ico['href'] = "Images/hospital.ico"
        css['rel'] = "stylesheet"
        css['href'] = "styles.css"
        script.insert_after(css, ico)
        meta.insert_after(meta_tag, title)
    with open('index.html', 'w') as file:
        file.write(str(soup))


# execute the script
covid()

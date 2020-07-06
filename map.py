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

yesterday = date.today() - timedelta(days=1)
yesterday = yesterday.strftime('%Y%m%d')
# print(yesterday)


def covid():
    states = os.path.join('us-states.json')
    geostate = geopandas.read_file(states, driver='GeoJSON')
    url = 'https://covidtracking.com/api/v1/states' 
    covid_data = pd.read_csv(f'{url}/current.csv')
    daily_covid = pd.read_csv(f'{url}/daily.csv')

    # set index for both dataframes 
    geostates = geostate.set_index('id')
    covid_data_indexed = covid_data.set_index('state')
    daily_covid_indexed = daily_covid.set_index('date')

    # combine both state and covid data dataframes 
    Geo_State_Data = pd.concat([geostates, covid_data_indexed], axis=1, join='inner')

    # quantiles that the colormap uses for color legend
    quantiles = [0, 0.8, 0.85, 0.90, 0.97, 1]
    bins = list(Geo_State_Data['positive'].quantile(quantiles))

    # create the colormap with given hex colors
    Legend_Colors = cm.LinearColormap(colors=['#A2EFFF', '#7C00FF'], vmin=0, vmax=1)

    #colormap returns 8 character values but only accepts 6 characters
    colors = [Legend_Colors(quantile)[0:-2] for quantile in quantiles]

    #change NY to a specific purple because it's so much worse than everywhere else
    colors = colors[0:-1] + ['#8d3f9c']


    colormap = cm.LinearColormap(colors=colors,
                                 vmin=Geo_State_Data.positive.min(),
                                 vmax=Geo_State_Data.positive.max(),
                                 caption="Positive COVID-19 Tests".upper())


    # Create a dictionary of colors because 'id' is the only property of the feature available when styling
    colordict = Geo_State_Data['positive'].apply(colormap)

    
    # for loop that takes the value in positive test results and evaluates the percentage of total population in the USA
    result = []
    Us_Population = 328239523
    for value in Geo_State_Data['positive'] / Us_Population:
        result.append("{0:.4f}".format(value * 100) + '%')
     
    Geo_State_Data["Percentile of USA"] = result

    result2 = []
    for value in Geo_State_Data['positive'] / Geo_State_Data['total']:
        result2.append("{0:.2f}".format(value * 100) + '%')

    Geo_State_Data['total percentage'] = result2           

    # create the map at given location with a current value for zoom using folium
    MyMap = folium.Map( location=[48, -102], 
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
            fields=['name', 'Percentile of USA', 'positive', 'total percentage', 'negative', 'total', 'death'], 
            aliases=['<div class="item-div">'+item.upper()+'</div>' for item in ['State', '% Positive of US Pop.', 'Positive Tests', '% Positive of Total Tests', 'Negative Tests', 'Total Tests', 'Deaths']],
            localize=True,
            direction="left",
            offset=(-15, 0)
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
 
# execute the script
covid()

# MyMap.add_child(folium.CssLink('./styles.css'))
# soup = BeautifulSoup(open('index.html'), features="html.parser")
# script = soup.find('script')
# css = soup.new_tag('link')
# css['rel'] = "stylesheet"
# css['href'] = "styles.css"
# script.insert_after(css)

# with open("index.html") as file:
#     file.write("index.html")


# execute the script everyday
# schedule.every(10).seconds.do(covid)
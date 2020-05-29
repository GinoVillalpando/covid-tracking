#   Map that tracks the daily COVID-19 positive cases by each state in the USA 
#   author: @Gino Villalpando GinoVillalpandoWork@gmail.com in collaboration with Kyla Bendt kylabendt@gmail.com
 
import folium
import pandas as pd
import os
import geopandas
import branca.colormap as cm 
import schedule

def covid():
    states = 'https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/us-states.json'
    geostate = geopandas.read_file(states, driver='GeoJSON')
    url = 'https://covidtracking.com/api/v1/states' 
    covid_data = pd.read_csv(f'{url}/current.csv')

    # set index for both dataframes 
    geostates = geostate.set_index('id')
    covid_data_indexed = covid_data.set_index('state')

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
        vmax=Geo_State_Data.positive.max())


    # Create a dictionary of colors because 'id' is the only property of the feature available when styling
    colordict = Geo_State_Data['positive'].apply(colormap)

    # name of legend
    colormap.caption = "Positive Covid Tests"

    # create the map at given location with a current value for zoom using folium
    MyMap = folium.Map(location=[48, -102], zoom_start=3, min_zoom=3, max_zoom=10, tiles='CartoDB dark_matter', prefer_canvas=True)

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
            'fillColor': 'black',
            'fillOpacity': 0,
            'color': 'black',
            'weight': 1,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['name','positive', 'negative', 'total', 'death'],
            aliases=['State','Positive Tests', 'Negative Tests', 'Total Tests', 'Deaths'],
            localize=True),
        highlight_function=lambda feature: {
            'fillColor': 'white',
            'fillOpacity': 0.5,
            'color': 'white',
            'weight': 4,
        }
    ).add_to(MyMap)

    folium.TileLayer(tiles='OpenStreetMap', name='OpenStreetMap').add_to(MyMap)

    # add colormap to the map 
    MyMap.add_child(colormap)

    # add layercontrol that will disable/enable choropleth or tooltips
    folium.LayerControl().add_to(MyMap)

    # create the maps and insert into a html file
    MyMap.save('index.html')

# execute the script
covid()

# execute the script everyday
# schedule.every(10).seconds.do(covid)
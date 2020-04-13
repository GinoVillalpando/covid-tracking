
#   Map that tracks the daily COVID-19 positive cases by each state in the USA 
#   author: @Gino Villalpando GinoVillalpandoWork@gmail.com
 
import folium
import pandas as pd
import os

states = os.path.join('data', 'states.json')
url = 'https://covidtracking.com/api/v1/states'
covid_data = pd.read_csv(f'{url}/current.csv')

# create the map at given location with a current value for zoom using folium
MyMap = folium.Map(location=[48, -102], zoom_start=3)

# create the Choropleth map with the given data in ../data/states.json
folium.Choropleth(
    geo_data=states,
    name='choropleth',
    data=covid_data,
    columns=['state', 'positive'],
    threshold_scale=[0, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000, 200000],
    key_on='feature.id',
    fill_color='BuPu',
    fill_opacity=0.8,
    line_opacity=0.4,
    legend_name='Positive COVID-19 Results as of today #',
    reset=True
).add_to(MyMap)

# add layercontrol that will disable/enable choropleth 
folium.LayerControl().add_to(MyMap)

# create the maps and insert into a html file
MyMap.save('map.html')
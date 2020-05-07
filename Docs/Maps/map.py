
#   Map that tracks the daily COVID-19 positive cases by each state in the USA 
#   author: @Gino Villalpando GinoVillalpandoWork@gmail.com
 
import folium
import pandas as pd
import os
import geopandas

states = os.path.join('data', 'states.json')
geostate = geopandas.read_file(states, driver='GeoJSON')
url = 'https://covidtracking.com/api/v1/states' 
covid_data = pd.read_csv(f'{url}/current.csv')

geostate.rename(columns={'id': 'state'}, inplace=True)

bins = list(covid_data['positive'].quantile([0, 0.25, 0.8, 0.97, 0.98, 0.985, 0.99, 0.995, 1]))

# create the map at given location with a current value for zoom using folium
MyMap = folium.Map(location=[48, -102], zoom_start=3)

# create the Choropleth map with the given data in ../data/states.json
Choropleth = folium.Choropleth(
    geo_data=states,
    name='choropleth',
    data=covid_data,
    columns=['state', 'positive'],
    key_on='feature.id',
    fill_color='BuPu',
    fill_opacity=0.8,
    line_opacity=0.4,
    legend_name='Positive COVID-19 Results as of today',
    highlight=True,
    bins=bins,
    reset=True
).add_to(MyMap)

for cases in range(len(covid_data)):
    print(geostate)
    if geostate['state'] == covid_data['state']:
        Choropleth.add_child(folium.Popup(
        '{}: {} Positive cases'.format(covid_data['state'][cases], covid_data['positive'][cases])    
))

# add layercontrol that will disable/enable choropleth 
folium.LayerControl().add_to(MyMap)

# create the maps and insert into a html file
MyMap.save('map.html')
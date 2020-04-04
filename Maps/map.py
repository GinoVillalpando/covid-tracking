
#   Map that tracks the daily COVID-19 positive cases by each state in the USA 
#   author: Gino Villalpando GinoVillalpandoWork@gmail.com
 
import folium
import requests
import pandas as pd
import os

states = os.path.join('data', 'states.json')
url = 'https://covidtracking.com/api/v1/states'
covid_data = f'{url}/daily.csv'

# this block of code was checking the API for what was stored in the data
# api = requests.get(f'{url}')

# data = api.json()

# for results in data:
#     print(results['state'])
#     print(results['positive'])

MyMap = folium.Map(location=[48, -102], zoom_start=3.5)

folium.Choropleth(
    geo_data=states,
    name='choropleth',
    data=pd.read_csv(covid_data),
    columns=['state', 'positive'],
    key_on='feature.id',
    fill_color='OrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Positive Covid Results #'
)

folium.LayerControl().add_to(MyMap)


MyMap.save('map.html')
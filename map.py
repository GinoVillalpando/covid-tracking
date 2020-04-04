import folium
import requests
import pandas as pd
import os

states = os.path.join('data', 'states.json')
url = 'https://covidtracking.com/api/states'
covid_data = pd.read_csv(f'{url}/daily.csv')

api = requests.get(f'{url}')


data = api.json()

for results in data:
    print(results['state'])
    print(results['positive'])

m = folium.Map(location=[48, -102], zoom_start=3.5)

m.choropleth(
    geo_data=states,
    name='choropleth',
    data=covid_data,
    columns=['state', 'postive'],
    key_on='feature.id',
    fill_color='YlGn',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Positive Covid Results #'
).add_to(m)

folium.LayerControl().add_to(m)


m.save('map.html')
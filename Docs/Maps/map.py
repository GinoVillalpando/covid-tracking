
#   Map that tracks the daily COVID-19 positive cases by each state in the USA 
#   author: Gino Villalpando GinoVillalpandoWork@gmail.com
 
import folium
import pandas as pd
import os

states = os.path.join('data', 'states.json')
url = 'https://covidtracking.com/api/v1/states'
covid_data = pd.read_csv(f'{url}/daily.csv')

bins = list(covid_data['positive'].quantile([0, 0.1, 0.2, 0.3, 0.4, 0.45]))

# this block of code was checking the API for what was stored in the data
# api = requests.get(f'{url}')

# data = api.json()

# for results in data:
#     print(results['state'])
#     print(results['positive'])

MyMap = folium.Map(location=[48, -102], zoom_start=3)

folium.Choropleth(
    geo_data=states,
    name='choropleth',
    data=covid_data,
    columns=['state', 'positive'],
    key_on='feature.id',
    fill_color='OrRd',
    fill_opacity=0.8,
    line_opacity=0.4,
    legend_name='Positive COVID-19 Results as of today #',
    bins=bins,
    reset=True
).add_to(MyMap)

folium.LayerControl().add_to(MyMap)

MyMap.save('map.html')
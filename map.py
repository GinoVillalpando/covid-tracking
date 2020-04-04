import folium
import requests

url = 'https://covidtracking.com/api/states'

api = requests.get(f'{url}')


data = api.json()

for results in data:
    print(results['state'])
    print(results['positive'])

m = folium.Map(location=[48, -102], zoom_start=3.5)

m.choropleth(
    geo_data=states
)


m.save('map.html')
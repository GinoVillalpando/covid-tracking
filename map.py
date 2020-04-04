import folium
import requests

api1 = requests.get("https://randomuser.me/api/?results=10")

data = api1.json()

for user in data['results']:
    print(user['name']['first'])

m = folium.Map(location=[35.0844, -106.6504], zoom_start=12)

m.save('map.html')
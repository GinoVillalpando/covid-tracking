
#   Map that tracks the daily COVID-19 positive cases by each state in the USA 
#   author: @Gino Villalpando GinoVillalpandoWork@gmail.com
 
import folium
import pandas as pd
import os
import geopandas
import branca.colormap as cm 

states = os.path.join('data', 'states.json')
geostate = geopandas.read_file(states, driver='GeoJSON')
url = 'https://covidtracking.com/api/v1/states' 
covid_data = pd.read_csv(f'{url}/current.csv')

geostate = geostate.set_index('id')
covid_data_indexed = covid_data.set_index('state')

covid_data_indexed.drop_duplicates(inplace=True)

print(covid_data_indexed)


geostatedata = pd.concat([geostate, covid_data_indexed], axis=1, join='inner')


quantiles = [0, 0.25, 0.5, 0.75, 0.98, 1]
bins = list(geostatedata['positive'].quantile(quantiles))

colormap1 = cm.LinearColormap(colors=['Blue', 'Purple'], vmin=0, vmax=1)
colormap1

#colormap returns 8 character values buy only accepts 6 characters
colors = [colormap1(quantile)[0:-2] for quantile in quantiles]

#change NY to black because it's so much worse than everywhere else
colors = colors[0:-1] + ['#000000']

colormap = cm.LinearColormap(colors=colors, index=bins,
    vmin=geostatedata.positive.min(),
    vmax=geostatedata.positive.max())


#Create a dictionay of colors because 'id' is the only property of the feature available when styling
colordict = geostatedata['positive'].apply(colormap)


colormap.caption = "Positive Covid Tests"

# create the map at given location with a current value for zoom using folium
MyMap = folium.Map(location=[48, -102], zoom_start=3)

State_Layer = folium.GeoJson(
    geostatedata,
    name='States',
    style_function = lambda feature: {
        'fillColor': 'white',
        'fillOpacity': 0,
        'color': 'black',
        'weight': 1,
    },
    tooltip=folium.GeoJsonTooltip(
        fields=['name', 'positive'],
        aliases=['State', 'Positive Tests'],
        localize=True
    )
).add_to(MyMap)

Positive_Layer = folium.GeoJson(
    geostatedata,
    name='Positive Tests',
    style_function=lambda feature: {
        'fillColor': colordict[feature['id']],
        'fillOpacity': 0.5,
        'color': 'black',
        'weight': 1,
    }
).add_to(MyMap)

MyMap.add_child(colormap)

# add layercontrol that will disable/enable choropleth 
folium.LayerControl().add_to(MyMap)

# create the maps and insert into a html file
MyMap.save('map.html')
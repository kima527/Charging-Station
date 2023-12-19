import warnings
import geopandas as gpd
import osmnx as osm
import pandas as pd
import networkx as nx
from matplotlib import pyplot as plt

warnings.filterwarnings("ignore", category=DeprecationWarning)

munich = osm.geocode_to_gdf({
    'city': 'München',
    'state': 'Bayern',
    'Country': 'Deutschland'
})

munich.plot()
plt.xlabel("longitude")
plt.ylabel("latitude")
plt.show()

containers = osm.geometries_from_place('München, Bayern', {'amenity': 'recycling'})
print(len(containers))
containers.head(10)
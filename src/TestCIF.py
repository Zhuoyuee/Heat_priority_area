import geopandas as gpd
from city_metrix.layers import TreeCover
import boto3
from city_metrix.layers import OpenStreetMap, OpenStreetMapClass
import geemap

# load boundary
boundary_path = 'https://cities-indicators.s3.eu-west-3.amazonaws.com/data/boundaries/boundary-BRA-Salvador-ADM4union.geojson'
city_gdf = gpd.read_file(boundary_path, driver='GeoJSON')

# Load data layer and save to a file
city_TreeCover = TreeCover().get_data(city_gdf.total_bounds)
city_TreeCover.rio.to_raster("city_TreeCover.tif")

city_TreeCover = TreeCover().write(city_gdf.total_bounds, 'data/city_TreeCover')

city_osm = OpenStreetMap(osm_class=OpenStreetMapClass.ROAD).get_data(city_gdf.total_bounds)
city_osm.head()

#View on a map
Map = geemap.Map()
Map.plot_raster(city_TreeCover, layer_name='city_TreeCover')
Map.zoom_to_bounds(city_gdf.total_bounds)
Map
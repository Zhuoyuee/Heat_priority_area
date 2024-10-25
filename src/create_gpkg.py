import geopandas as gpd
from shapely.geometry import box
import os


def create_gpkg_from_bbox(xmin, ymin, xmax, ymax, output_folder, output_filename, layer_name='bbox_layer'):
    # Define the bounding box
    bbox = box(xmin, ymin, xmax, ymax)

    # Create a GeoDataFrame
    gdf = gpd.GeoDataFrame({'geometry': [bbox]}, crs='EPSG:28992')

    # Construct full output path
    output_path = os.path.join(output_folder, output_filename)

    # Write to GeoPackage
    gdf.to_file(output_path, layer=layer_name, driver="GPKG")


# Parameters for the bounding box
xmin = 1603940.0007625178
ymin = 8477385.865001518
xmax = 1605940.0007625178
ymax = 8479385.865001518

# xmin = 1605940.0007625178
# ymin = 8479385.865001518
# xmax = 1607940.0007625178
# ymax = 8481385.865001518
output_folder = '../data'  # Relative path from the /src folder to the /data folder
output_filename = 'AOI2_bbx.gpkg'

# {'top_left': (1603940.0007625178, 8477385.865001518), 'bottom_right': (1605940.0007625178, 8479385.865001518)},
#1605940.0007625178, 8479385.865001518), 'bottom_right': (1607940.0007625178, 8481385.865001518)
# Create the GeoPackage
create_gpkg_from_bbox(xmin, ymin, xmax, ymax, output_folder, output_filename)

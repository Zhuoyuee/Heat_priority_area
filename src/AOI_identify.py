import rasterio
import numpy as np
from rasterio import mask

# Function to normalize raster values between 0 and 1
def normalize(array):
    return (array - np.nanmin(array)) / (np.nanmax(array) - np.nanmin(array))

def identify_AOI(lst_path, ndvi_path, height_path, window_size=100):
    # Open the raster files
    with rasterio.open(lst_path) as lst_raster, rasterio.open(ndvi_path) as ndvi_raster, rasterio.open(height_path) as height_raster:
        lst = lst_raster.read(1)  # Land Surface Temperature
        ndvi = ndvi_raster.read(1)  # NDVI
        height = height_raster.read(1)  # Tree height

        # Normalize the rasters layers
        lst_norm = normalize(lst)
        ndvi_norm = normalize(ndvi)
        height_norm = normalize(height)

        # Apply criteria for severe urban heat: High LST, Low NDVI, Low Vegetation
        heat_score = lst_norm + (1 - ndvi_norm) + (1 - height_norm)

        # Find the location of the maximum heat score
        max_x, max_y = np.unravel_index(np.nanargmax(heat_score), heat_score.shape)
        window = np.s_[max_x:max_x+window_size, max_y:max_y+window_size]

        # Calculate the bounding box in map coordinates
        top_left = lst_raster.transform * (window[1].start, window[0].start)
        bottom_right = lst_raster.transform * (window[1].stop, window[0].stop)

        bbox = {
            "top_left": top_left,
            "bottom_right": bottom_right
        }

    return bbox

def cropping(ahn4las, bbx):
    # Define the bounding box
    min_x, max_x = 181437.246002, 181937.246002
    min_y, max_y = 318805.419006, 319305.419006

    mask = ((las.x >= min_x) & (las.x <= max_x) & (las.y >= min_y) & (las.y <= max_y))

    # Filter points based on the bounding box
    cropped = laspy.create(point_format=las.header.point_format, file_version=las.header.version)
    cropped.header = las.header  # Copy header information
    cropped.points = las.points[mask]
    print('Points from cropped data:', len(cropped.points))

    # Write the cropped LAS file
    cropped.write(out_las_file_path)
    
    return 0



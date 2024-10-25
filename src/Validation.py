import geopandas as gpd
import rasterio
from shapely.geometry import Point, box
from rtree import index
import numpy as np

'''
The CRS is EPSG:28992 for better results locally (for Amsterdam), the unit in this CRS is meter.
'''
# Define the Stats class to store statistics for each building

# Define the Stats class to store statistics
class Stats:
    def __init__(self, max_val, min_val, avg_val, stddev_val, num_points, avg_diff):
        self.max_val = max_val
        self.min_val = min_val
        self.avg_val = avg_val
        self.stddev_val = stddev_val
        self.num_points = num_points
        self.avg_diff = avg_diff  # Difference between average cell height and building height

    def __str__(self):
        return (f"Max: {self.max_val}, Min: {self.min_val}, Avg: {self.avg_val}, "
                f"Stddev: {self.stddev_val}, Points: {self.num_points}, Avg Diff: {self.avg_diff}")

# Function to create a 2km bounding box given a center point in EPSG:28992
def create_2km_bbox(center_x, center_y):
    half_size = 1000  # 1km in each direction for a 2km x 2km bounding box
    xmin = center_x - half_size
    xmax = center_x + half_size
    ymin = center_y - half_size
    ymax = center_y + half_size
    return box(xmin, ymin, xmax, ymax)

# Function to calculate statistics for cell heights inside a polygon
def calculate_height_stats(cell_heights, building_height):
    avg_height = np.mean(cell_heights)
    stats = Stats(
        max_val=np.max(cell_heights),
        min_val=np.min(cell_heights),
        avg_val=avg_height,
        stddev_val=np.std(cell_heights),
        num_points=len(cell_heights),
        avg_diff=avg_height - building_height  # Difference between avg height of cells and building height
    )
    return stats

# generate the center points and height values of each raster cell
def generate_cell_centers_and_heights(raster_path):
    # Open the raster file
    with rasterio.open(raster_path) as src:
        transform = src.transform
        raster_width, raster_height = src.width, src.height
        raster_data = src.read(1)  # Read the first band for height data (assuming DSM or CHM)
        cell_centers_and_heights = []

        # Loop over the rows and columns of the raster to get the center points and heights
        for row in range(raster_height):
            for col in range(raster_width):
                x, y = rasterio.transform.xy(transform, row, col, offset='center')
                height = raster_data[row, col]  # Get the height value from the raster
                cell_centers_and_heights.append((Point(x, y), height))  # Store center point and height

    return cell_centers_and_heights

# Function to build an R-tree spatial index for fast lookups
def build_spatial_index(cell_centers_and_heights):
    idx = index.Index()
    for i, (point, height) in enumerate(cell_centers_and_heights):
        idx.insert(i, (point.x, point.y, point.x, point.y))  # Insert point's bounding box into the index
    return idx

# Function to find points inside a polygon using R-tree spatial index
def points_in_polygon(polygon, cell_centers_and_heights, spatial_idx):
    candidates = list(spatial_idx.intersection(polygon.bounds))  # Get candidate points by bounding box
    points_within_polygon = [(cell_centers_and_heights[i][0], cell_centers_and_heights[i][1]) for i in candidates if polygon.contains(cell_centers_and_heights[i][0])]  # Exact check
    return points_within_polygon

# Function to process each building and calculate statistics for points inside the polygon
def process_buildings(raster_path, vector_path, bbox):
    # Load the vector data (building footprints) from geopackage
    buildings_gdf = gpd.read_file(vector_path, bbox=bbox)

    # Generate cell centers and heights from the raster
    cell_centers_and_heights = generate_cell_centers_and_heights(raster_path)

    # Build the spatial index for all cell centers
    spatial_idx = build_spatial_index(cell_centers_and_heights)

    # Store building stats in a dictionary
    building_stats = {}

    # Lists to store differences for overall performance
    all_diffs = []

    # Loop through each building polygon in the vector file
    for idx, building in buildings_gdf.iterrows():
        building_polygon = building.geometry
        building_height = building['height']  # Assuming 'height' is the column name

        # Find the cell centers inside the building polygon
        points_in_poly = points_in_polygon(building_polygon, cell_centers_and_heights, spatial_idx)

        # Collect heights for the points within the polygon
        cell_heights = [height for point, height in points_in_poly]

        # Calculate stats if there are any points in the polygon
        if cell_heights:
            stats = calculate_height_stats(cell_heights, building_height)
            building_stats[building['id']] = stats  # Use building ID as key

            # Append the difference to the overall performance list
            all_diffs.append(stats.avg_diff)

    # Calculate overall performance
    avg_diff = np.mean(all_diffs) if all_diffs else 0
    stddev_diff = np.std(all_diffs) if all_diffs else 0

    return building_stats, avg_diff, stddev_diff

# Example usage
raster_path = 'path_to_raster_file_on_local_machine_or_server'
vector_path = 'path_to_geopackage.gpkg'

# Example center point for bounding box (in EPSG:28992)
center_x, center_y = 155000, 463000
bbox = create_2km_bbox(center_x, center_y)

# Process the buildings and get the stats for each footprint along with overall performance
building_stats, avg_diff, stddev_diff = process_buildings(raster_path, vector_path, bbox)

# Output the stats for each building
for building_id, stats in building_stats.items():
    print(f"Building ID: {building_id}, Stats: {stats}")

# Print overall performance summary
print(f"\nOverall Average Height Difference: {avg_diff}")
print(f"Overall Stddev of Height Differences: {stddev_diff}")
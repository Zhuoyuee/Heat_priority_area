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


min_x, min_y, max_x, max_y = 181437.246002, 318805.419006, 181937.246002, 319305.419006
cell_size = 1

# Grid dimensions
x_coords = np.arange(min_x, max_x, cell_size)
y_coords = np.arange(min_y, max_y, cell_size)
grid_width = len(x_coords)
grid_height = len(y_coords)

def generate_points_around(center_x, center_y, center_z, radius, num_points=10):
    angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
    return [(center_x + radius * np.cos(angle), center_y + radius * np.sin(angle), center_z) for angle in angles]

# densifying the point cloud
radius = 0.20
densified_points = []
for x, y, z in zip(filtered_points.x, filtered_points.y, filtered_points.z):
    points_around = generate_points_around(x, y, z, radius)
    densified_points.extend(points_around)


heights = np.full((grid_height, grid_width), fill_value=np.nan, dtype=np.float64)
for x, y, z in densified_points:
    x_idx = int((x - min_x) / cell_size)
    y_idx = int((max_y - y) / cell_size)
    if 0 <= x_idx < grid_width and 0 <= y_idx < grid_height:
        if np.isnan(heights[y_idx][x_idx]) or heights[y_idx, x_idx] < z:
            heights[y_idx][x_idx] = z


# Geospatial transform
transform = from_origin(min_x, max_y, cell_size, cell_size)

# Write to a TIFF file
output_file_path = input("Enter the output file path for the vegetation raster: ")

with rasterio.open(
    output_file_path,  # Use the user-provided file path
    'w',
    driver='GTiff',
    height=heights.shape[0],
    width=heights.shape[1],
    count=1,
    dtype=heights.dtype,
    crs='EPSG:7415',  # Setting the CRS to RDNAP
    transform=transform
) as dst:
    dst.write(heights, 1)

print(f"vegetation raster saved to: {output_file_path}")
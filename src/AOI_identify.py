import rasterio
import numpy as np
from skimage.util import view_as_windows
# Function to normalize raster values between 0 and 1
def normalize(array):
    return (array - np.nanmin(array)) / (np.nanmax(array) - np.nanmin(array))


def sliding_window_aggregate(array, window_size):
    """
    Apply a memory-efficient sliding window aggregation (mean) over the array.

    Args:
    - array: Input numpy array.
    - window_size: Size of the sliding window (in pixels).

    Returns:
    - Aggregated numpy array of mean values.
    """
    rows, cols = array.shape
    aggregated_result = np.zeros((rows - window_size + 1, cols - window_size + 1), dtype=np.float32)

    # Loop through each window in a memory-efficient way
    for i in range(0, rows - window_size + 1):
        for j in range(0, cols - window_size + 1):
            # Extract the window and compute the mean
            window = array[i:i + window_size, j:j + window_size]
            aggregated_result[i, j] = np.nanmean(window)

    return aggregated_result


def identify_AOI(lst, ndvi, height, metadata, target_km=2):
    """
    Identifies a 2km x 2km area with high LST, low NDVI, and low tree height using in-memory arrays.

    Args:
    - lst: NumPy array of LST (land surface temperature).
    - ndvi: NumPy array of NDVI (vegetation index).
    - height: NumPy array of tree height.
    - metadata: Metadata dictionary containing the transform, resolution, crs, etc.
    - target_km: The size of the AOI in kilometers (default is 2km x 2km).

    Returns:
    - bbox: A dictionary containing the top-left and bottom-right coordinates of the AOI.
    """
    # Extract metadata
    transform = metadata['transform']
    pixel_size_x, pixel_size_y = transform[0], abs(transform[4])  # Extract pixel size from transform

    # Calculate the window size in pixels for a 2km x 2km area
    window_size_x = int(target_km * 1000 / pixel_size_x)
    window_size_y = int(target_km * 1000 / pixel_size_y)
    window_size = min(window_size_x, window_size_y)  # Ensure square window

    # Normalize the raster layers
    lst_norm = normalize(lst)
    ndvi_norm = normalize(ndvi)
    height_norm = normalize(height)

    # Apply criteria for severe urban heat: High LST, Low NDVI, Low Vegetation
    heat_score = lst_norm + (1 - ndvi_norm) + (1 - height_norm)

    # Apply a sliding window to compute the mean heat score over each 2km x 2km block
    heat_aggregated = sliding_window_aggregate(heat_score, window_size)

    # Find the window with the maximum aggregated heat score
    max_window_x, max_window_y = np.unravel_index(np.nanargmax(heat_aggregated), heat_aggregated.shape)

    # Convert the windowed indices back to the original raster coordinate space
    min_x = max_window_x * window_size
    min_y = max_window_y * window_size
    max_x = min_x + window_size
    max_y = min_y + window_size

    # Calculate the bounding box in map coordinates using the affine transform
    top_left = transform * (min_y, min_x)
    bottom_right = transform * (max_y, max_x)

    bbox = {
        "top_left": top_left,
        "bottom_right": bottom_right
    }

    print(bbox)
    return bbox





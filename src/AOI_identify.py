import numpy as np
import rasterio
from skimage.util import view_as_windows


def normalize(array):
    return (array - np.nanmin(array)) / (np.nanmax(array) - np.nanmin(array))


def sliding_window_aggregate(array, window_size):
    """
    Apply a memory-efficient sliding window aggregation (mean) over the array.
    """
    rows, cols = array.shape
    aggregated_result = np.zeros((rows - window_size + 1, cols - window_size + 1), dtype=np.float32)

    for i in range(0, rows - window_size + 1):
        for j in range(0, cols - window_size + 1):
            window = array[i:i + window_size, j:j + window_size]
            aggregated_result[i, j] = np.nanmean(window)

    return aggregated_result


def identify_top_AOIs(lst, ndvi, height, metadata, top_n=3, target_km=2):
    """
    Identifies the top non-overlapping 2km x 2km AOIs based on criteria.
    """
    transform = metadata['transform']
    pixel_size_x, pixel_size_y = transform[0], abs(transform[4])
    window_size_x = int(target_km * 1000 / pixel_size_x)
    window_size_y = int(target_km * 1000 / pixel_size_y)
    window_size = min(window_size_x, window_size_y)

    # Normalize and compute the criteria
    lst_norm = normalize(lst)
    ndvi_norm = normalize(ndvi)
    height_norm = normalize(height)
    heat_score = lst_norm + (1 - ndvi_norm) + (1 - height_norm)

    # Compute aggregated heat score
    heat_aggregated = sliding_window_aggregate(heat_score, window_size)

    top_AOIs = []
    for _ in range(top_n):
        max_idx = np.nanargmax(heat_aggregated)
        max_window_x, max_window_y = np.unravel_index(max_idx, heat_aggregated.shape)
        min_x = max_window_x * window_size
        min_y = max_window_y * window_size
        max_x = min_x + window_size
        max_y = min_y + window_size

        # Convert to map coordinates
        top_left = transform * (min_y, min_x)
        bottom_right = transform * (max_y, max_x)
        top_AOIs.append({"top_left": top_left, "bottom_right": bottom_right})

        # Set the identified window to nan to avoid overlap
        heat_aggregated[max_window_x:max_window_x + window_size, max_window_y:max_window_y + window_size] = np.nan

    print(top_AOIs)
    return top_AOIs



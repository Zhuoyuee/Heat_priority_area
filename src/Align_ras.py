import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import numpy as np

def align_rasters(lst_raster_path, ndvi_raster_path, tree_height_raster_path, target_crs='EPSG:28992', output_resolution=(10, 10)):
    """
    Aligns LST, NDVI, and Tree Height rasters to have the same CRS, bounding box, and resolution.

    Args:
    - lst_raster_path: Path to the LST raster file.
    - ndvi_raster_path: Path to the NDVI raster file.
    - tree_height_raster_path: Path to the tree height raster file.
    - target_crs: The target coordinate reference system, default 'EPSG:28992'.
    - output_resolution: Tuple for resolution in meters (default is 10m x 10m).

    Returns:
    - lst_aligned, ndvi_aligned, tree_height_aligned: Aligned raster arrays.
    - meta: Metadata of the aligned rasters.
    """
    # Open the rasters
    with rasterio.open(lst_raster_path) as lst, rasterio.open(ndvi_raster_path) as ndvi, rasterio.open(tree_height_raster_path) as tree:
        # Check and reproject to target CRS if needed
        lst_data, ndvi_data, tree_data = lst.read(1, out_shape=(lst.height, lst.width), resampling=Resampling.bilinear), \
                                         ndvi.read(1, out_shape=(ndvi.height, ndvi.width), resampling=Resampling.bilinear), \
                                         tree.read(1, out_shape=(tree.height, tree.width), resampling=Resampling.bilinear)

        lst_transform, ndvi_transform, tree_transform = lst.transform, ndvi.transform, tree.transform
        lst_crs, ndvi_crs, tree_crs = lst.crs, ndvi.crs, tree.crs

        # Reproject if CRS do not match
        if lst_crs != target_crs:
            lst_data, lst_transform = reproject_array(lst_data, lst.transform, lst.crs, target_crs, lst.width, lst.height)
        if ndvi_crs != target_crs:
            ndvi_data, ndvi_transform = reproject_array(ndvi_data, ndvi.transform, ndvi.crs, target_crs, ndvi.width, ndvi.height)
        if tree_crs != target_crs:
            tree_data, tree_transform = reproject_array(tree_data, tree.transform, tree.crs, target_crs, tree.width, tree.height)

        # Calculate the intersection of the bounding boxes
        min_x = max(lst_transform[2], ndvi_transform[2], tree_transform[2])
        max_x = min(lst_transform[2] + lst.width * lst_transform[0],
                    ndvi_transform[2] + ndvi.width * ndvi_transform[0],
                    tree_transform[2] + tree.width * tree_transform[0])

        min_y = max(lst_transform[5] + lst.height * lst_transform[4],
                    ndvi_transform[5] + ndvi.height * ndvi_transform[4],
                    tree_transform[5] + tree.height * tree_transform[4])

        max_y = min(lst_transform[5], ndvi_transform[5], tree_transform[5])

        # Calculate new dimensions and transform
        new_width = int((max_x - min_x) / output_resolution[0])
        new_height = int((max_y - min_y) / output_resolution[1])
        new_transform = rasterio.transform.from_origin(min_x, max_y, output_resolution[0], output_resolution[1])

        # Prepare metadata for aligned rasters
        meta = lst.meta.copy()
        meta.update({
            'driver': 'GTiff',
            'height': new_height,
            'width': new_width,
            'transform': new_transform,
            'crs': target_crs
        })

        # Reproject and resample each raster to match the new resolution and bounding box
        lst_aligned = np.empty((new_height, new_width), dtype='float32')
        ndvi_aligned = np.empty((new_height, new_width), dtype='float32')
        tree_aligned = np.empty((new_height, new_width), dtype='float32')

        reproject(source=lst_data, destination=lst_aligned, src_transform=lst_transform, src_crs=target_crs, dst_transform=new_transform, dst_crs=target_crs, resampling=Resampling.bilinear)
        reproject(source=ndvi_data, destination=ndvi_aligned, src_transform=ndvi_transform, src_crs=target_crs, dst_transform=new_transform, dst_crs=target_crs, resampling=Resampling.bilinear)
        reproject(source=tree_data, destination=tree_aligned, src_transform=tree_transform, src_crs=target_crs, dst_transform=new_transform, dst_crs=target_crs, resampling=Resampling.bilinear)

    return lst_aligned, ndvi_aligned, tree_aligned, meta

def reproject_array(data, src_transform, src_crs, dst_crs, width, height):
    """
    Helper function to reproject array to a new CRS.

    Args:
    - data: The source data array.
    - src_transform: Source affine transformation.
    - src_crs: Source coordinate reference system.
    - dst_crs: Destination coordinate reference system.
    - width: Width of the source data.
    - height: Height of the source data.

    Returns:
    - data: Reprojected data array.
    - transform: New affine transformation.
    """
    # Ensure CRS is properly parsed
    src_crs = rasterio.crs.CRS.from_user_input(src_crs)
    dst_crs = rasterio.crs.CRS.from_user_input(dst_crs)

    # Calculate the new transform and dimensions
    new_transform, new_width, new_height = calculate_default_transform(
        src_crs, dst_crs, width, height, *src_transform.bounds)
    new_data = np.empty((new_height, new_width), dtype=data.dtype)

    # Reproject the data
    reproject(
        source=data,
        destination=new_data,
        src_transform=src_transform,
        src_crs=src_crs,
        dst_transform=new_transform,
        dst_crs=dst_crs,
        resampling=Resampling.bilinear
    )

    return new_data, new_transform
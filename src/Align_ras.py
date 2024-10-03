import rasterio
from rasterio.merge import merge
from rasterio.warp import calculate_default_transform, reproject, Resampling
import numpy as np


def align_rasters(lst_raster, ndvi_raster, tree_height_raster, output_resolution=(10, 10)):
    """
    Aligns LST, NDVI, and Tree Height rasters to have the same bounding box and resolution.

    Args:
    - lst_raster: path to the LST raster file
    - ndvi_raster: path to the NDVI raster file
    - tree_height_raster: path to the tree height raster file
    - output_resolution: tuple for resolution (default is 1m x 1m)

    Returns:
    - lst_aligned, ndvi_aligned, tree_height_aligned: aligned raster arrays
    - meta: metadata of the aligned rasters
    """

    # Open rasters
    with rasterio.open(lst_raster) as lst:
        lst_data = lst.read(1)
        lst_transform = lst.transform
        lst_crs = lst.crs
        lst_meta = lst.meta

    with rasterio.open(ndvi_raster) as ndvi:
        ndvi_data = ndvi.read(1)
        ndvi_transform = ndvi.transform
        ndvi_crs = ndvi.crs

    with rasterio.open(tree_height_raster) as th:
        tree_data = th.read(1)
        tree_transform = th.transform
        tree_crs = th.crs

    print("LST Metadata:")
    print("Resolution (res):", lst.transform[0])
    print("Bounds:", lst.bounds)
    print("CRS:", lst.crs)
    print("Width:", lst.width, "Height:", lst.height)

    print("NDVI Metadata:")
    print("Resolution (res):", ndvi.transform[0])
    print("Bounds:", ndvi.bounds)
    print("CRS:", ndvi.crs)
    print("Width:", ndvi.width, "Height:", ndvi.height)

    print("TH Metadata:")
    print("Resolution (res):", th.transform[0])
    print("Bounds:", th.bounds)
    print("CRS:", th.crs)
    print("Width:", th.width, "Height:", th.height)

    # Calculate the intersection of the bounding boxes
    min_x = max(lst_transform[2], ndvi_transform[2], tree_transform[2])
    max_x = min(lst_transform[2] + lst.width * lst_transform[0],
                ndvi_transform[2] + ndvi.width * ndvi_transform[0],
                tree_transform[2] + th.width * tree_transform[0])

    min_y = max(lst_transform[5] + lst.height * lst_transform[4],
                ndvi_transform[5] + ndvi.height * ndvi_transform[4],
                tree_transform[5] + th.height * tree_transform[4])

    max_y = min(lst_transform[5], ndvi_transform[5], tree_transform[5])

    if max_y > min_y:

        new_height = int((max_y - min_y) / output_resolution[1])
    else:

        new_height = int((min_y - max_y) / output_resolution[1])


    new_width = int((max_x - min_x) / output_resolution[0])

    #cropping
    new_transform = rasterio.transform.from_bounds(min_x, min_y, max_x, max_y, new_width, new_height)

    # Prepare metadata for aligned rasters
    aligned_meta = lst_meta.copy()
    aligned_meta.update({
        "height": new_height,
        "width": new_width,
        "transform": new_transform,
        "crs": lst_crs,
        "dtype": 'float32'
    })

    # Reproject and resample each raster to match the new resolution and bounding box
    lst_aligned = np.empty((new_height, new_width), dtype=np.float32)
    ndvi_aligned = np.empty((new_height, new_width), dtype=np.float32)
    tree_aligned = np.empty((new_height, new_width), dtype=np.float32)

    with rasterio.open(lst_raster) as lst:
        reproject(
            source=rasterio.band(lst, 1),
            destination=lst_aligned,
            src_transform=lst.transform,
            src_crs=lst.crs,
            dst_transform=new_transform,
            dst_crs=lst_crs,
            resampling=Resampling.bilinear
        )

    with rasterio.open(ndvi_raster) as ndvi:
        reproject(
            source=rasterio.band(ndvi, 1),
            destination=ndvi_aligned,
            src_transform=ndvi.transform,
            src_crs=ndvi.crs,
            dst_transform=new_transform,
            dst_crs=lst_crs,
            resampling=Resampling.bilinear
        )

    with rasterio.open(tree_height_raster) as th:
        reproject(
            source=rasterio.band(th, 1),
            destination=tree_aligned,
            src_transform=th.transform,
            src_crs=th.crs,
            dst_transform=new_transform,
            dst_crs=lst_crs,
            resampling=Resampling.bilinear
        )

    return lst_aligned, ndvi_aligned, tree_aligned, aligned_meta
